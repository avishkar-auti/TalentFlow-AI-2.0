import { useState, useEffect, useCallback } from 'react';

export const useMediaDevices = () => {
  const [stream, setStream] = useState<MediaStream | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isGranted, setIsGranted] = useState(false);

  const requestPermissions = useCallback(async () => {
    try {
      const mediaStream = await navigator.mediaDevices.getUserMedia({
        video: true,
        audio: true
      });
      setStream(mediaStream);
      setIsGranted(true);
      setError(null);
    } catch (err) {
      const e = err as Error;
      setError(e.message || 'Failed to access camera/microphone');
      setIsGranted(false);
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
