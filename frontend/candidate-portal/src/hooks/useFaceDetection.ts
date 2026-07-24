import { useState, useEffect, useRef, useCallback } from 'react';

// Declare faceapi globally for TypeScript
declare const faceapi: any;

export interface FaceDetectionResult {
  isLoaded: boolean;
  faceCount: number;
  isFaceVisible: boolean;
  lastViolationType: string | null;
  warningMessage: string | null;
}

export function useFaceDetection(videoRef: React.RefObject<HTMLVideoElement>, isActive: boolean): FaceDetectionResult {
  const [isLoaded, setIsLoaded] = useState(false);
  const [faceCount, setFaceCount] = useState(0);
  const [isFaceVisible, setIsFaceVisible] = useState(true);
  const [lastViolationType, setLastViolationType] = useState<string | null>(null);
  const [warningMessage, setWarningMessage] = useState<string | null>(null);
  
  const faceAbsentStartTime = useRef<number | null>(null);

  // Load script and models
  useEffect(() => {
    const loadFaceApi = async () => {
      // Check if already loaded
      if ((window as any).faceapi) {
        await loadModels();
        return;
      }

      const script = document.createElement('script');
      script.src = 'https://cdn.jsdelivr.net/npm/face-api.js@0.22.2/dist/face-api.min.js';
      script.async = true;
      script.onload = async () => {
        await loadModels();
      };
      document.head.appendChild(script);
    };

    const loadModels = async () => {
      try {
        const MODEL_URL = 'https://justadudewhohacks.github.io/face-api.js/models';
        await faceapi.nets.ssdMobilenetv1.loadFromUri(MODEL_URL);
        await faceapi.nets.faceLandmark68Net.loadFromUri(MODEL_URL);
        setIsLoaded(true);
      } catch (err) {
        console.warn('Failed to load face-api models', err);
      }
    };

    loadFaceApi();
  }, []);

  // Run detection
  useEffect(() => {
    if (!isLoaded || !isActive || !videoRef.current) return;

    let intervalId: any;

    const detectFaces = async () => {
      try {
        if (!videoRef.current || videoRef.current.paused || videoRef.current.ended) return;

        const detections = await faceapi.detectAllFaces(videoRef.current).withFaceLandmarks();
        
        const currentFaceCount = detections.length;
        setFaceCount(currentFaceCount);
        
        if (currentFaceCount === 0) {
          if (!faceAbsentStartTime.current) {
            faceAbsentStartTime.current = Date.now();
          } else {
            const absentDuration = Date.now() - faceAbsentStartTime.current;
            if (absentDuration > 5000) {
              setLastViolationType('EXTENDED_ABSENCE');
              setWarningMessage('Face absent > 5 seconds - violation!');
              setIsFaceVisible(false);
            } else if (absentDuration > 3000) {
              setLastViolationType('NO_FACE');
              setWarningMessage('Face not visible - please face the camera');
              setIsFaceVisible(false);
            }
          }
        } else {
          // Face(s) detected, reset absent timer
          faceAbsentStartTime.current = null;
          setIsFaceVisible(true);

          if (currentFaceCount > 1) {
            setLastViolationType('MULTIPLE_FACES');
            setWarningMessage('Multiple people detected - violation!');
          } else {
            // 1 face detected, check head pose / landmarks
            const landmarks = detections[0].landmarks;
            const nose = landmarks.getNose();
            const jawOutline = landmarks.getJawOutline();
            
            // Very rough head pose estimation based on nose position relative to jaw
            const leftJaw = jawOutline[0];
            const rightJaw = jawOutline[16];
            
            // Check if nose is too close to left or right jaw (looking away)
            const noseX = nose[3].x; // Tip of nose
            const leftDist = noseX - leftJaw.x;
            const rightDist = rightJaw.x - noseX;
            
            const ratio = leftDist / rightDist;
            if (ratio > 3 || ratio < 0.33) {
              setLastViolationType('LOOKING_AWAY');
              setWarningMessage('Looking away detected');
            } 
            else {
              // Check looking down
              const topNose = nose[0].y;
              const bottomNose = nose[3].y;
              const noseLength = bottomNose - topNose;
              // Just a heuristic for HEAD_DOWN
              if (noseLength < 10) { // arbitrary small value if face is tilted down
                // setLastViolationType('HEAD_DOWN');
                // setWarningMessage('Looking down detected - phone use?');
              } else {
                setLastViolationType(null);
                setWarningMessage(null);
              }
            }
          }
        }
      } catch (err) {
        console.warn('Face detection error', err);
      }
    };

    intervalId = setInterval(detectFaces, 2000);

    return () => clearInterval(intervalId);
  }, [isLoaded, isActive, videoRef]);

  return { isLoaded, faceCount, isFaceVisible, lastViolationType, warningMessage };
}
