import { useState, useEffect, useRef } from 'react';

export type AudioNoiseStatus = 'inactive' | 'clean' | 'background_noise' | 'high_noise';

export function useAudioNoiseDetector(stream: MediaStream | null) {
  const [audioStatus, setAudioStatus] = useState<AudioNoiseStatus>('inactive');
  const [noiseLevel, setNoiseLevel] = useState<number>(0);
  const [isNoiseWarning, setIsNoiseWarning] = useState<boolean>(false);

  const audioCtxRef = useRef<AudioContext | null>(null);
  const analyserRef = useRef<AnalyserNode | null>(null);
  const sourceRef = useRef<MediaStreamAudioSourceNode | null>(null);
  const animationFrameRef = useRef<number | null>(null);

  useEffect(() => {
    if (!stream || stream.getAudioTracks().length === 0) {
      setAudioStatus('inactive');
      setNoiseLevel(0);
      setIsNoiseWarning(false);
      return;
    }

    try {
      const AudioCtx = window.AudioContext || (window as any).webkitAudioContext;
      const audioCtx = new AudioCtx();
      const analyser = audioCtx.createAnalyser();
      analyser.fftSize = 512;
      analyser.smoothingTimeConstant = 0.8;

      const source = audioCtx.createMediaStreamSource(stream);
      source.connect(analyser);

      audioCtxRef.current = audioCtx;
      analyserRef.current = analyser;
      sourceRef.current = source;

      const dataArray = new Uint8Array(analyser.frequencyBinCount);

      let noiseExceededCounter = 0;

      const checkAudio = () => {
        if (!analyserRef.current) return;

        analyser.getByteFrequencyData(dataArray);

        let sum = 0;
        for (let i = 0; i < dataArray.length; i++) {
          sum += dataArray[i];
        }
        const average = sum / dataArray.length;
        const normalizedLevel = Math.min(Math.round((average / 128) * 100), 100);

        setNoiseLevel(normalizedLevel);

        if (normalizedLevel > 65) {
          noiseExceededCounter += 1;
          if (noiseExceededCounter > 20) {
            setAudioStatus('high_noise');
            setIsNoiseWarning(true);
          }
        } else if (normalizedLevel > 35) {
          setAudioStatus('background_noise');
          if (noiseExceededCounter > 10) {
            setIsNoiseWarning(true);
          }
        } else {
          noiseExceededCounter = Math.max(0, noiseExceededCounter - 1);
          setAudioStatus('clean');
          setIsNoiseWarning(false);
        }

        animationFrameRef.current = requestAnimationFrame(checkAudio);
      };

      checkAudio();
    } catch (err) {
      console.warn('Web Audio API initialized with warning:', err);
    }

    return () => {
      if (animationFrameRef.current) {
        cancelAnimationFrame(animationFrameRef.current);
      }
      if (sourceRef.current) {
        sourceRef.current.disconnect();
      }
      if (audioCtxRef.current && audioCtxRef.current.state !== 'closed') {
        audioCtxRef.current.close().catch(() => {});
      }
    };
  }, [stream]);

  return { audioStatus, noiseLevel, isNoiseWarning };
}
