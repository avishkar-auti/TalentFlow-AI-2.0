import React from 'react';
import { Mic, MicOff, Video, VideoOff, X } from 'lucide-react';
import { ProctoringAlert } from './ProctoringAlert';

interface WebRTCVideoGridProps {
  localStream: MediaStream | null;
  remoteStream: MediaStream | null;
  localVideoRef: React.RefObject<HTMLVideoElement>;
  remoteVideoRef: React.RefObject<HTMLVideoElement>;
  isMuted: boolean;
  isVideoOff: boolean;
  onToggleMute: () => void;
  onToggleVideo: () => void;
  onEndCall: () => void;
  connectionState: string;
  proctoringMsg: string | null;
  alertType: 'vision' | 'audio' | 'termination' | 'peer' | 'info';
  onClearAlert?: () => void;
}

export function WebRTCVideoGrid({
  localStream,
  remoteStream,
  localVideoRef,
  remoteVideoRef,
  isMuted,
  isVideoOff,
  onToggleMute,
  onToggleVideo,
  onEndCall,
  connectionState,
  proctoringMsg,
  alertType,
  onClearAlert
}: WebRTCVideoGridProps) {
  // Attach local media stream to local video element
  React.useEffect(() => {
    if (localVideoRef.current && localStream) {
      localVideoRef.current.srcObject = localStream;
    }
  }, [localStream, localVideoRef]);

  // Attach remote media stream to remote video element
  React.useEffect(() => {
    if (remoteVideoRef.current && remoteStream) {
      remoteVideoRef.current.srcObject = remoteStream;
    }
  }, [remoteStream, remoteVideoRef]);

  return (
    <div className="relative w-full h-full bg-slate-900 rounded-xl overflow-hidden shadow-2xl flex flex-col">
      {/* Remote Video Stream (Main View) */}
      <div className="flex-1 relative bg-slate-800">
        <video
          ref={remoteVideoRef}
          autoPlay
          playsInline
          className="absolute inset-0 w-full h-full object-cover"
        />
        
        {/* Connection Overlay if not fully connected/streaming remote */}
        {(!remoteStream || connectionState !== 'connected') && (
          <div className="absolute inset-0 flex flex-col items-center justify-center bg-slate-900/80 backdrop-blur-sm z-10">
            <div className="animate-pulse bg-blue-500/20 p-4 rounded-full mb-4">
              <Video className="w-8 h-8 text-blue-400" />
            </div>
            <p className="text-slate-300 font-medium">
              {connectionState === 'connecting' ? 'Connecting to peer...' : 
               connectionState === 'disconnected' ? 'Peer disconnected' :
               'Waiting for remote video stream...'}
            </p>
          </div>
        )}

        {/* Proctoring & Peer Alert HUD */}
        <ProctoringAlert 
          message={proctoringMsg}
          alertType={alertType}
          onClose={onClearAlert}
        />

        {/* Local Video Stream (PIP / Inset) */}
        <div className="absolute bottom-6 right-6 w-48 h-36 bg-black rounded-lg overflow-hidden shadow-xl border border-slate-700 z-20">
          <video
            ref={localVideoRef}
            autoPlay
            playsInline
            muted
            className={`w-full h-full object-cover ${!isVideoOff ? '' : 'hidden'}`}
          />
          {isVideoOff && (
            <div className="absolute inset-0 flex items-center justify-center bg-slate-800">
              <VideoOff className="w-6 h-6 text-slate-500" />
            </div>
          )}
          {isMuted && (
            <div className="absolute top-2 right-2 bg-red-500/90 p-1 rounded-md backdrop-blur-sm">
              <MicOff className="w-3 h-3 text-white" />
            </div>
          )}
        </div>
      </div>

      {/* Control Bar */}
      <div className="h-20 bg-slate-900 border-t border-slate-800 flex items-center justify-center gap-4 px-6 shrink-0 z-30">
        <button
          onClick={onToggleMute}
          className={`p-4 rounded-full transition-colors ${
            isMuted ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
          title={isMuted ? "Unmute" : "Mute"}
        >
          {isMuted ? <MicOff className="w-5 h-5" /> : <Mic className="w-5 h-5" />}
        </button>

        <button
          onClick={onToggleVideo}
          className={`p-4 rounded-full transition-colors ${
            isVideoOff ? 'bg-red-500/10 text-red-500 hover:bg-red-500/20' : 'bg-slate-800 text-slate-300 hover:bg-slate-700'
          }`}
          title={isVideoOff ? "Turn on camera" : "Turn off camera"}
        >
          {isVideoOff ? <VideoOff className="w-5 h-5" /> : <Video className="w-5 h-5" />}
        </button>
        
        <div className="w-px h-8 bg-slate-800 mx-2" />

        <button
          onClick={onEndCall}
          className="px-6 py-3 bg-red-500 hover:bg-red-600 text-white rounded-full font-medium transition-colors flex items-center gap-2"
        >
          <X className="w-5 h-5" />
          End Call
        </button>
      </div>
    </div>
  );
}
