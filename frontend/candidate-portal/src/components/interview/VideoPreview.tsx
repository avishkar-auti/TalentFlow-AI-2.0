import React, { useEffect, useRef } from 'react';

interface VideoPreviewProps {
  stream: MediaStream | null;
  className?: string;
  muted?: boolean;
}

export function VideoPreview({ stream, className, muted = true }: VideoPreviewProps) {
  const videoRef = useRef<HTMLVideoElement>(null);

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream]);

  if (!stream) {
    return <div className={`bg-black ${className}`} />;
  }

  return (
    <video
      ref={videoRef}
      autoPlay
      playsInline
      muted={muted}
      className={`w-full h-full object-cover rounded-lg mirror ${className}`}
      style={{ transform: 'scaleX(-1)' }}
    />
  );
}
