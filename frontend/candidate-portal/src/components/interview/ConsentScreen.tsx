import React, { useState } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/Card';
import { Button } from '../ui/Button';
import { Shield, Camera, Mic, Eye, Info } from 'lucide-react';
import { VideoPreview } from './VideoPreview';

interface ConsentScreenProps {
  onAccept: () => void;
  stream: MediaStream | null;
  onRequestPermissions: () => void;
  isGranted: boolean;
  permissionError: string | null;
}

export function ConsentScreen({ onAccept, stream, onRequestPermissions, isGranted, permissionError }: ConsentScreenProps) {
  const [acceptedTerms, setAcceptedTerms] = useState(false);

  return (
    <div className="max-w-3xl mx-auto py-8 px-4">
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl flex items-center gap-2">
            <Shield className="h-6 w-6 text-primary-500" />
            Interview Preparation & Explicit Proctoring Consent
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-6">
          <div className="bg-blue-50 dark:bg-blue-900/20 p-4 rounded-lg flex gap-3 text-blue-800 dark:text-blue-200">
            <Info className="h-5 w-5 shrink-0 mt-0.5" />
            <p className="text-sm">
              You are about to enter a live, AI-assisted interview. Please review the security and gaze tracking disclosures below before proceeding.
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="space-y-4">
              <h3 className="font-semibold text-lg border-b pb-2 dark:border-gray-700">Session & Proctoring Disclosures</h3>
              <ul className="space-y-3 text-sm text-gray-600 dark:text-gray-300">
                <li className="flex gap-2">
                  <Camera className="h-4 w-4 shrink-0 mt-0.5 text-blue-400" />
                  <span><strong>Camera & Identity:</strong> Your video stream will verify candidate presence and identity consistency.</span>
                </li>
                <li className="flex gap-2">
                  <Eye className="h-4 w-4 shrink-0 mt-0.5 text-amber-400" />
                  <span><strong>Eye Movement & Gaze Direction:</strong> Real-time frame analysis evaluates eye movement, eye aspect ratio, and gaze direction to ensure exam integrity.</span>
                </li>
                <li className="flex gap-2">
                  <Mic className="h-4 w-4 shrink-0 mt-0.5 text-teal-400" />
                  <span><strong>Audio & Speech:</strong> Your responses will be transcribed and analyzed for technical evaluation.</span>
                </li>
                <li className="flex gap-2">
                  <Shield className="h-4 w-4 shrink-0 mt-0.5 text-emerald-400" />
                  <span><strong>Privacy First:</strong> Only objective integrity flags (e.g. timestamps & flag counts) are stored — no subjective judgments or full video recordings are kept.</span>
                </li>
              </ul>

              <div className="mt-6">
                <label className="flex items-start gap-3 cursor-pointer">
                  <input 
                    type="checkbox" 
                    className="mt-1 h-4 w-4 rounded border-gray-300 text-primary-600 focus:ring-primary-500"
                    checked={acceptedTerms}
                    onChange={(e) => setAcceptedTerms(e.target.checked)}
                  />
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    I consent to camera access, audio recording, and real-time automated evaluation of my <strong>eye movement, gaze direction, and head pose</strong> for interview integrity purposes.
                  </span>
                </label>
              </div>
            </div>

            <div className="space-y-4 flex flex-col h-full">
              <h3 className="font-semibold text-lg border-b pb-2 dark:border-gray-700">Camera Check</h3>
              
              <div className="flex-1 bg-gray-100 dark:bg-gray-900 rounded-lg overflow-hidden flex items-center justify-center min-h-[200px] relative border border-gray-200 dark:border-gray-700">
                {isGranted && stream ? (
                  <VideoPreview stream={stream} />
                ) : (
                  <div className="text-center p-4">
                    <Camera className="h-8 w-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-sm text-gray-500 mb-4">Camera and microphone access required</p>
                    <Button onClick={onRequestPermissions} size="sm" variant="outline">
                      Allow Access
                    </Button>
                    {permissionError && (
                      <p className="text-xs text-amber-500 font-medium mt-2">{permissionError}</p>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          <div className="flex justify-end pt-4 border-t dark:border-gray-700">
            <Button 
              onClick={() => {
                if (!isGranted) onRequestPermissions();
                onAccept();
              }}
              disabled={!acceptedTerms}
              size="lg"
            >
              I Understand and Accept
            </Button>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
