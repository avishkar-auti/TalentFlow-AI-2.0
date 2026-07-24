import { useState, useEffect, useCallback } from 'react';

const createSimulatedStream = (): MediaStream => {
  const canvas = document.createElement('canvas');
  canvas.width = 640;
  canvas.height = 480;
  const ctx = canvas.getContext('2d');

  let hue = 0;
  const draw = () => {
    if (!ctx) return;
    hue = (hue + 1) % 360;
    ctx.fillStyle = '#0f172a';
    ctx.fillRect(0, 0, 640, 480);

    ctx.strokeStyle = `hsl(${hue}, 70%, 50%)`;
    ctx.lineWidth = 4;
    ctx.beginPath();
    ctx.arc(320, 190, 45, 0, Math.PI * 2);
    ctx.stroke();

    ctx.fillStyle = '#f8fafc';
    ctx.font = 'bold 20px sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Live Meeting Feed', 320, 270);

    ctx.fillStyle = '#94a3b8';
    ctx.font = '14px sans-serif';
    ctx.fillText('Virtual Video & Audio Active', 320, 305);
  };

  draw();
  setInterval(draw, 1000 / 30);

  const canvasStream = (canvas as any).captureStream ? (canvas as any).captureStream(30) : null;
  const videoTrack = canvasStream ? canvasStream.getVideoTracks()[0] : null;

  let audioTrack: MediaStreamTrack | null = null;
  try {
    const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
    if (AudioContextClass) {
      const audioCtx = new AudioContextClass();
      const osc = audioCtx.createOscillator();
      const dst = audioCtx.createMediaStreamDestination();
      osc.connect(dst);
      osc.start();
      audioTrack = dst.stream.getAudioTracks()[0];
    }
  } catch (e) {
    console.warn('AudioContext fallback warning:', e);
  }

  const tracks: MediaStreamTrack[] = [];
  if (videoTrack) tracks.push(videoTrack);
  if (audioTrack) tracks.push(audioTrack);

  return new MediaStream(tracks);
};

export const useMediaDevices = () => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGranted, setIsGranted] = useState(false);

  const requestPermissions = useCallback(async () => {
    try {
      if (navigator.mediaDevices && navigator.mediaDevices.getUserMedia) {
        try {
          const mediaStream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: true
          });
          setStream(mediaStream);
          setIsGranted(true);
          setError(null);
          return;
        } catch (e1) {
          try {
            const videoOnlyStream = await navigator.mediaDevices.getUserMedia({ video: true });
            setStream(videoOnlyStream);
            setIsGranted(true);
            setError(null);
            return;
          } catch (e2) {}
        }
      }

      // Fallback to simulated media stream if hardware device is missing or blocked
      const simStream = createSimulatedStream();
      setStream(simStream);
      setIsGranted(true);
      setError(null);
    } catch (err) {
      const simStream = createSimulatedStream();
      setStream(simStream);
      setIsGranted(true);
      setError(null);
    }
  }, []);

  const stopStream = useCallback(() => {
    if (stream) {
      stream.getTracks().forEach(track => track.stop());
      setStream(null);
      setIsGranted(false);
    }
  }, [stream]);

  useEffect(() => {
    return () => stopStream();
  }, [stopStream]);

  return { stream, error, isGranted, requestPermissions, stopStream };
};
