import React, { useEffect, useRef } from 'react';

interface VideoPreviewProps {
  stream: MediaStream | null;
  className?: string;
  muted?: boolean;
  videoRef?: React.RefObject<HTMLVideoElement>;
}

export function VideoPreview({ stream, className, muted = true, videoRef: externalRef }: VideoPreviewProps) {
  const internalRef = useRef<HTMLVideoElement>(null);
  const videoRef = externalRef || internalRef;

  useEffect(() => {
    if (videoRef.current && stream) {
      videoRef.current.srcObject = stream;
    }
  }, [stream, videoRef]);

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
