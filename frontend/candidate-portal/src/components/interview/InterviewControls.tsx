import React, { useState } from 'react';
import { Mic, MicOff, Send, Square } from 'lucide-react';
import { Button } from '../ui/Button';
import { Input } from '../ui/Input';

interface InterviewControlsProps {
  onSendMessage: (text: string) => void;
  onEndInterview: () => void;
  isListening: boolean;
  onToggleListen: () => void;
  transcript: string;
}

export function InterviewControls({ 
  onSendMessage, 
  onEndInterview, 
  isListening, 
  onToggleListen,
  transcript
}: InterviewControlsProps) {
  const [text, setText] = useState('');

  const handleSend = () => {
    const message = text || transcript;
    if (message.trim()) {
      onSendMessage(message);
      setText('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 rounded-b-xl">
      <div className="flex items-end gap-2">
        <button
          onClick={onToggleListen}
          className={`p-3 rounded-full flex-shrink-0 transition-colors ${
            isListening 
              ? 'bg-red-100 text-red-600 hover:bg-red-200 dark:bg-red-900/30 dark:text-red-400' 
              : 'bg-gray-200 text-gray-600 hover:bg-gray-300 dark:bg-gray-700 dark:text-gray-300'
          }`}
          title={isListening ? "Stop listening" : "Start speaking"}
        >
          {isListening ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
        </button>

        <div className="flex-1 relative">
          <Input
            value={isListening ? transcript : text}
            onChange={(e) => !isListening && setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={isListening ? "Listening..." : "Type your answer here..."}
            className="w-full bg-white pr-10"
            disabled={isListening}
          />
        </div>

        <Button 
          onClick={handleSend}
          disabled={(!text.trim() && !transcript.trim())}
          className="rounded-full w-10 h-10 p-0 flex items-center justify-center flex-shrink-0"
        >
          <Send className="h-4 w-4" />
        </Button>
      </div>

      <div className="mt-4 flex justify-between items-center text-xs text-gray-500">
        <p>Press Enter to send. Use microphone for speech-to-text.</p>
        <Button 
          variant="ghost" 
          size="sm" 
          onClick={onEndInterview}
          className="text-red-500 hover:text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
        >
          <Square className="h-3 w-3 mr-1" /> End Interview
        </Button>
      </div>
    </div>
  );
}
