import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { ConsentScreen } from '../components/interview/ConsentScreen';
import { VideoPreview } from '../components/interview/VideoPreview';
import { ChatPanel } from '../components/interview/ChatPanel';
import { InterviewControls } from '../components/interview/InterviewControls';
import { InterviewTimer } from '../components/interview/InterviewTimer';
import { ProctoringAlert } from '../components/interview/ProctoringAlert';
import { useMediaDevices } from '../hooks/useMediaDevices';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useAudioNoiseDetector } from '../hooks/useAudioNoiseDetector';
import { useWebSocket } from '../hooks/useWebSocket';
import { useFaceDetection } from '../hooks/useFaceDetection';
import { ShieldAlert, Volume2, AlertOctagon, Users, Code, Eye, EyeOff } from 'lucide-react';
import type { InterviewMessage } from '../types';

export function InterviewRoom() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const location = useLocation();
  
  const queryParams = new URLSearchParams(location.search);
  const interviewMode = queryParams.get('mode') || 'ai_screening'; // hr_round, technical_coding, ai_screening
  
  const [hasConsented, setHasConsented] = useState(false);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [proctoringMsg, setProctoringMsg] = useState<string | null>(null);
  const [warningCount, setWarningCount] = useState<number>(0);
  const [alertType, setAlertType] = useState<'vision' | 'audio' | 'termination'>('vision');
  const [isTerminated, setIsTerminated] = useState<boolean>(false);
  const [terminationReason, setTerminationReason] = useState<string>('');
  const [lastFlagTime, setLastFlagTime] = useState<number>(0);

  const { stream, isGranted, error: mediaError, requestPermissions, stopStream } = useMediaDevices();
  const { isListening, transcript, startListening, stopListening, setTranscript } = useSpeechRecognition();
  const { audioStatus, noiseLevel, isNoiseWarning } = useAudioNoiseDetector(stream);

  const { sendMessage, lastMessage, isConnected } = useWebSocket(isInterviewActive ? id : undefined);
  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);

  // Hook up face-api.js detection
  const faceDetection = useFaceDetection(videoRef, isInterviewActive && !isTerminated);

  // Video frame extraction loop for real-time OpenCV vision proctoring
  useEffect(() => {
    if (!isInterviewActive || !isConnected || isTerminated || !stream) return;

    const interval = setInterval(() => {
      const videoEl = videoRef.current;
      if (videoEl && videoEl.readyState === 4) {
        const canvas = canvasRef.current || document.createElement('canvas');
        canvas.width = 640;
        canvas.height = 480;
        const ctx = canvas.getContext('2d');
        if (ctx) {
          ctx.drawImage(videoEl, 0, 0, 640, 480);
          const frameBase64 = canvas.toDataURL('image/jpeg', 0.6);
          sendMessage({ type: 'frame', data: frameBase64 });
        }
      }
    }, 1500);

    return () => clearInterval(interval);
  }, [isInterviewActive, isConnected, isTerminated, stream, sendMessage]);

  // Handle client-side face-api warnings
  useEffect(() => {
    if (faceDetection.lastViolationType && isInterviewActive && !isTerminated) {
      const now = Date.now();
      // Debounce flags to avoid spamming (e.g. 1 flag per 5 seconds max for same issue)
      if (now - lastFlagTime > 5000) {
        setLastFlagTime(now);
        const newCount = warningCount + 1;
        setWarningCount(newCount);
        
        let localAlertType: 'vision' | 'termination' = 'vision';
        let uiMsg = faceDetection.warningMessage || 'Proctoring violation detected.';
        
        // Custom UI based on violation type
        if (faceDetection.lastViolationType === 'MULTIPLE_FACES' || newCount >= 5) {
          localAlertType = newCount >= 5 ? 'termination' : 'vision';
        }

        setAlertType(localAlertType);
        setProctoringMsg(uiMsg);

        // Send flag to backend
        if (isConnected) {
          sendMessage({
            type: 'client_flag',
            flag_type: faceDetection.lastViolationType,
            message: faceDetection.warningMessage,
            timestamp: new Date().toISOString()
          });
        }

        if (newCount >= 5) {
          handleAutoTermination("Maximum warning limit (5/5) exceeded due to client-side face detection violations.");
        }
      }
    } else if (!faceDetection.lastViolationType && proctoringMsg && alertType === 'vision' && !isNoiseWarning) {
      // Clear message if no violation after a while (optional, could just let it timeout)
      const timer = setTimeout(() => setProctoringMsg(null), 3000);
      return () => clearTimeout(timer);
    }
  }, [faceDetection.lastViolationType, isInterviewActive, isTerminated]);

  // Audio noise alert handling
  useEffect(() => {
    if (isNoiseWarning && isInterviewActive && !isTerminated) {
      const now = Date.now();
      if (now - lastFlagTime > 5000) {
        setLastFlagTime(now);
        const newCount = warningCount + 1;
        setWarningCount(newCount);
        
        setAlertType('audio');
        setProctoringMsg('Background noise/extra voice detected. Please remain in a quiet room.');
        
        if (isConnected) {
          sendMessage({
            type: 'client_flag',
            flag_type: 'AUDIO_NOISE',
            message: 'Background noise detected',
            timestamp: new Date().toISOString()
          });
        }
        
        if (newCount >= 5) {
          handleAutoTermination("Maximum warning limit (5/5) exceeded due to repeated audio noise violations.");
        }
      }
    }
  }, [isNoiseWarning, isInterviewActive, isTerminated]);

  // Handle incoming WebSocket messages (including server vision proctoring)
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'message') {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: 'interviewer',
          content: lastMessage.content,
          timestamp: new Date().toISOString()
        }]);
      } else if (lastMessage.type === 'vision_result') {
        if (lastMessage.flags && lastMessage.flags.length > 0) {
          const latestFlag = lastMessage.flags[lastMessage.flags.length - 1];
          // Use server's warning count or increment local
          const currWarnings = lastMessage.warning_count || latestFlag.warning_number || (warningCount + 1);
          
          if (currWarnings > warningCount) {
            setWarningCount(currWarnings);
            setAlertType('vision');
            setProctoringMsg(latestFlag.user_message || `Warning ${currWarnings}/5: Proctoring policy violation.`);

            if (lastMessage.is_terminated || currWarnings >= 5) {
              handleAutoTermination(latestFlag.user_message || "Maximum warning limit (5/5) exceeded from server analysis.");
            }
          }
        }
      } else if (lastMessage.type === 'interview_terminated') {
        handleAutoTermination(lastMessage.reason || "Interview automatically terminated for policy violations.");
      }
    }
  }, [lastMessage]);

  const handleAutoTermination = async (reason: string) => {
    setIsTerminated(true);
    setTerminationReason(reason);
    setIsInterviewActive(false);
    stopStream();
    stopListening();

    // Call backend to mark interview failed & reject candidate
    if (id) {
      try {
        await fetch(`http://localhost:8000/api/v1/interviews/${id}/fail`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ notes: `Auto-terminated: ${reason}` })
        });
      } catch (e) {
        console.warn('Failed to update interview status:', e);
      }
    }

    // Redirect to status page after 3 seconds
    setTimeout(() => navigate('/status?terminated=true'), 3000);
  };

  const handleStartInterview = () => {
    setHasConsented(true);
    setIsInterviewActive(true);
    
    // Auto focus the video stream to the ref for face-api
    setTimeout(() => {
      const vid = document.querySelector('video');
      if (vid && videoRef) {
        // We need to attach the stream to our own ref if not already
        videoRef.current = vid as any;
      }
    }, 500);

    setTimeout(() => {
      let welcomeMsg = 'Welcome to your AI hiring interview. Please speak clearly. Proctoring is active.';
      if (interviewMode === 'hr_round') welcomeMsg = 'Welcome to the Live HR Round. Please wait for the recruiter to join or start with automated screening.';
      if (interviewMode === 'technical_coding') welcomeMsg = 'Welcome to the Technical Interview. This session is proctored.';
      
      setMessages([{
        id: '1',
        sender: 'interviewer',
        content: welcomeMsg,
        timestamp: new Date().toISOString()
      }]);
    }, 1000);
  };

  const handleSendMessage = (text: string) => {
    if (!text.trim() || isTerminated) return;
    
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'candidate',
      content: text,
      timestamp: new Date().toISOString()
    }]);

    if (isConnected) {
      sendMessage({ type: 'message', content: text });
    }
    
    setTranscript('');
    stopListening();
  };

  const handleEndInterview = () => {
    stopStream();
    setIsInterviewActive(false);
    navigate('/status');
  };

  const toggleListen = () => {
    if (isListening) {
      stopListening();
    } else {
      startListening();
    }
  };

  if (!hasConsented) {
    return (
      <ConsentScreen 
        onAccept={handleStartInterview}
        stream={stream}
        isGranted={isGranted}
        onRequestPermissions={requestPermissions}
        permissionError={mediaError}
      />
    );
  }

  // Header content based on mode
  let headerTitle = "AI Candidate Interview";
  let HeaderIcon = ShieldAlert;
  
  if (interviewMode === 'hr_round') {
    headerTitle = "Live HR Interview";
    HeaderIcon = Users;
  } else if (interviewMode === 'technical_coding') {
    headerTitle = "Technical Interview - Coding Assessment";
    HeaderIcon = Code;
  }

  return (
    <div className="h-[calc(100vh-8rem)] max-w-6xl mx-auto flex gap-6 pb-6 animate-fade-in relative">
      <canvas ref={canvasRef} className="hidden" width={640} height={480} />

      {/* Auto-Termination Overlay Modal */}
      {isTerminated && (
        <div className="fixed inset-0 z-50 bg-black/80 backdrop-blur-md flex items-center justify-center p-4">
          <Card className="max-w-md w-full p-8 text-center border-red-500/50 bg-gray-900 text-white shadow-2xl">
            <div className="w-20 h-20 bg-red-500/20 text-red-500 rounded-full flex items-center justify-center mx-auto mb-6 border border-red-500/30">
              <AlertOctagon className="w-12 h-12 animate-pulse" />
            </div>
            <h2 className="text-3xl font-extrabold text-red-400 mb-3">Interview Terminated</h2>
            <div className="bg-red-950/40 p-4 rounded-xl border border-red-900/50 mb-6 text-left">
              <span className="text-xs font-bold uppercase tracking-wider text-red-500/70 block mb-1">Termination Reason</span>
              <p className="text-sm text-gray-200 font-mono">
                {terminationReason || "5 Proctoring Warnings Exceeded. Session automatically closed."}
              </p>
            </div>
            <p className="text-sm text-gray-400 mb-8 leading-relaxed">
              You have exceeded the maximum allowable proctoring warnings (5/5). Your interview video, frame logs, and session flags have been securely recorded and transmitted to the recruitment team for manual compliance review.
            </p>
            <button
              onClick={() => navigate('/status?terminated=true')}
              className="w-full py-3.5 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl shadow-lg transition-all active:scale-[0.98]"
            >
              Return to Dashboard
            </button>
          </Card>
        </div>
      )}

      {/* Left side: Video & Proctoring Indicators */}
      <div className="w-1/3 flex flex-col gap-4">
        <Card className="flex-1 relative overflow-hidden bg-gray-900 border-0 flex flex-col shadow-xl">
          <div className="absolute top-4 left-4 z-10 flex flex-col gap-2">
            <div className="bg-black/60 backdrop-blur-sm text-white px-2.5 py-1 rounded-md text-xs flex items-center gap-2 border border-white/10">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              {isConnected ? 'Server Conn: Active' : 'Reconnecting...'}
            </div>
            
            <div className="bg-black/60 backdrop-blur-sm text-white px-2.5 py-1 rounded-md text-xs flex items-center gap-2 border border-white/10">
              {faceDetection.isLoaded ? (
                <>
                  <Eye className="w-3.5 h-3.5 text-blue-400" /> Client Vision AI: Active
                </>
              ) : (
                <>
                  <EyeOff className="w-3.5 h-3.5 text-gray-400" /> Loading Vision AI...
                </>
              )}
            </div>

            {/* Warning Count HUD */}
            <div className={`px-2.5 py-1 rounded-md text-xs font-bold font-mono flex items-center gap-1.5 border backdrop-blur-sm transition-colors ${
              warningCount >= 4 
                ? 'bg-red-600/90 text-white border-red-400 animate-pulse shadow-[0_0_15px_rgba(220,38,38,0.5)]'
                : warningCount > 0
                ? 'bg-amber-500/90 text-white border-amber-300'
                : 'bg-black/60 text-emerald-400 border-white/10'
            }`}>
              <ShieldAlert className="w-3.5 h-3.5" />
              Warnings: {warningCount} / 5
            </div>

            {/* Web Audio Noise Level Meter */}
            <div className="bg-black/60 backdrop-blur-sm text-white px-2.5 py-1 rounded-md text-xs flex items-center gap-2 border border-white/10">
              <Volume2 className={`w-3.5 h-3.5 ${
                audioStatus === 'high_noise' ? 'text-red-400 animate-pulse' : audioStatus === 'background_noise' ? 'text-amber-400' : 'text-emerald-400'
              }`} />
              <span>Audio:</span>
              <span className={`font-semibold capitalize ${
                audioStatus === 'high_noise' ? 'text-red-400' : audioStatus === 'background_noise' ? 'text-amber-400' : 'text-emerald-400'
              }`}>
                {audioStatus === 'clean' ? 'Clear Voice' : audioStatus === 'background_noise' ? 'Noise Detected' : audioStatus === 'high_noise' ? 'High Noise' : 'Standby'}
              </span>
            </div>
          </div>
          
          <div className="absolute top-4 right-4 z-10">
            <InterviewTimer isActive={isInterviewActive && !isTerminated} />
          </div>

          <ProctoringAlert 
            message={proctoringMsg} 
            warningCount={warningCount} 
            maxWarnings={5} 
            alertType={alertType} 
          />

          <div className="flex-1 relative h-full">
            <VideoPreview stream={stream} className="absolute inset-0 rounded-none object-cover" videoRef={videoRef} />
          </div>
        </Card>
      </div>

      {/* Right side: Chat & Controls */}
      <Card className="flex-1 flex flex-col border-gray-200 dark:border-gray-700 shadow-lg bg-white/95 dark:bg-gray-900/95 backdrop-blur-md">
        <div className="p-5 border-b border-gray-200 dark:border-gray-800 bg-gray-50/80 dark:bg-gray-800/80 flex justify-between items-center rounded-t-xl">
          <div className="flex items-center gap-3">
            <div className={`p-2 rounded-lg ${interviewMode === 'hr_round' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : interviewMode === 'technical_coding' ? 'bg-violet-100 text-violet-600 dark:bg-violet-900/30 dark:text-violet-400' : 'bg-primary-100 text-primary-600 dark:bg-primary-900/30 dark:text-primary-400'}`}>
              <HeaderIcon className="w-5 h-5" />
            </div>
            <div>
              <h2 className="font-bold text-lg text-gray-900 dark:text-white leading-none">{headerTitle}</h2>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] font-bold tracking-wider uppercase bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-2 py-0.5 rounded border border-emerald-500/20">
                  PROCTORING ACTIVE
                </span>
              </div>
            </div>
          </div>
          <span className="text-sm font-medium text-gray-500 flex items-center gap-1.5 bg-white dark:bg-gray-900 px-3 py-1.5 rounded-lg border border-gray-200 dark:border-gray-700 shadow-sm">
            <div className="w-2 h-2 bg-red-500 rounded-full animate-pulse"></div> Live Session
          </span>
        </div>
        
        <div className="flex-1 overflow-hidden">
          <ChatPanel messages={messages} />
        </div>
        
        <div className="p-4 border-t border-gray-100 dark:border-gray-800 bg-white dark:bg-gray-900 rounded-b-xl">
          <InterviewControls 
            onSendMessage={handleSendMessage}
            onEndInterview={handleEndInterview}
            isListening={isListening}
            onToggleListen={toggleListen}
            transcript={transcript}
          />
        </div>
      </Card>
    </div>
  );
}
