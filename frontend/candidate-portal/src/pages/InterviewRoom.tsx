import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Card } from '../components/ui/Card';
import { ConsentScreen } from '../components/interview/ConsentScreen';
import { VideoPreview } from '../components/interview/VideoPreview';
import { ChatPanel } from '../components/interview/ChatPanel';
import { InterviewControls } from '../components/interview/InterviewControls';
import { InterviewTimer } from '../components/interview/InterviewTimer';
import { ProctoringAlert } from '../components/interview/ProctoringAlert';
import { useMediaDevices } from '../hooks/useMediaDevices';
import { useSpeechRecognition } from '../hooks/useSpeechRecognition';
import { useWebSocket } from '../hooks/useWebSocket';
import type { InterviewMessage } from '../types';

export function InterviewRoom() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [hasConsented, setHasConsented] = useState(false);
  const [isInterviewActive, setIsInterviewActive] = useState(false);
  const [messages, setMessages] = useState<InterviewMessage[]>([]);
  const [proctoringMsg, setProctoringMsg] = useState<string | null>(null);

  const { stream, isGranted, error: mediaError, requestPermissions, stopStream } = useMediaDevices();
  const { isListening, transcript, startListening, stopListening, setTranscript } = useSpeechRecognition();
  // Using dummy WS to avoid connection errors if backend is not running, 
  // but integrating hooks as requested
  const { sendMessage, lastMessage, isConnected } = useWebSocket(isInterviewActive ? id : undefined);

  // Handle incoming WS messages
  useEffect(() => {
    if (lastMessage) {
      if (lastMessage.type === 'message') {
        setMessages(prev => [...prev, {
          id: Date.now().toString(),
          sender: 'interviewer',
          content: lastMessage.content,
          timestamp: new Date().toISOString()
        }]);
      } else if (lastMessage.type === 'proctoring_flag') {
        setProctoringMsg("Please ensure your face is clearly visible.");
        setTimeout(() => setProctoringMsg(null), 5000);
      }
    }
  }, [lastMessage]);

  const handleStartInterview = () => {
    setHasConsented(true);
    setIsInterviewActive(true);
    // Mock initial message
    setTimeout(() => {
      setMessages([{
        id: '1',
        sender: 'interviewer',
        content: 'Hi there! Welcome to the interview. Could you start by telling me a little about yourself?',
        timestamp: new Date().toISOString()
      }]);
    }, 1000);
  };

  const handleSendMessage = (text: string) => {
    if (!text.trim()) return;
    
    // Add user message locally
    setMessages(prev => [...prev, {
      id: Date.now().toString(),
      sender: 'candidate',
      content: text,
      timestamp: new Date().toISOString()
    }]);

    // Send via WS
    if (isConnected) {
      sendMessage({ type: 'message', content: text });
    }
    
    // Clear transcript if using voice
    setTranscript('');
    stopListening();
    
    // Mock response for demo purposes
    setTimeout(() => {
      setMessages(prev => [...prev, {
        id: Date.now().toString(),
        sender: 'interviewer',
        content: "Thank you for sharing that. Can you describe a challenging project you worked on recently?",
        timestamp: new Date().toISOString()
      }]);
    }, 2000);
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

  return (
    <div className="h-[calc(100vh-8rem)] max-w-6xl mx-auto flex gap-6 pb-6 animate-fade-in">
      {/* Left side: Video */}
      <div className="w-1/3 flex flex-col gap-4">
        <Card className="flex-1 relative overflow-hidden bg-gray-900 border-0 flex flex-col">
          <div className="absolute top-4 left-4 z-10 flex gap-2">
            <div className="bg-black/50 backdrop-blur-sm text-white px-2 py-1 rounded text-xs flex items-center gap-2">
              <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-500' : 'bg-red-500'}`} />
              {isConnected ? 'Connected' : 'Reconnecting...'}
            </div>
          </div>
          
          <div className="absolute top-4 right-4 z-10">
            <InterviewTimer isActive={isInterviewActive} />
          </div>

          <ProctoringAlert message={proctoringMsg} />

          <div className="flex-1 relative h-full">
            <VideoPreview stream={stream} className="absolute inset-0 rounded-none object-cover" />
          </div>
        </Card>
      </div>

      {/* Right side: Chat & Controls */}
      <Card className="flex-1 flex flex-col border-gray-200 dark:border-gray-700 shadow-lg">
        <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800 flex justify-between items-center rounded-t-xl">
          <h2 className="font-semibold text-lg text-gray-900 dark:text-white">Live Interview</h2>
          <span className="text-sm text-gray-500">Question 1 of ~5</span>
        </div>
        
        <ChatPanel messages={messages} />
        
        <InterviewControls 
          onSendMessage={handleSendMessage}
          onEndInterview={handleEndInterview}
          isListening={isListening}
          onToggleListen={toggleListen}
          transcript={transcript}
        />
      </Card>
    </div>
  );
}
