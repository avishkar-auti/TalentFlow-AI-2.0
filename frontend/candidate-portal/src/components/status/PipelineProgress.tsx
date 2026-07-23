import React from 'react';
import { Check, Circle } from 'lucide-react';
import { APPLICATION_STAGES } from '../../utils/constants';

interface PipelineProgressProps {
  currentStage: string;
}

export function PipelineProgress({ currentStage }: PipelineProgressProps) {
  const currentIndex = APPLICATION_STAGES.findIndex(s => s.id === currentStage);
  
  return (
    <div className="py-6">
      <div className="relative">
        <div className="absolute inset-0 flex items-center" aria-hidden="true">
          <div className="h-0.5 w-full bg-gray-200 dark:bg-gray-700" />
        </div>
        <ul className="relative flex justify-between">
          {APPLICATION_STAGES.map((stage, stepIdx) => {
            const isCompleted = stepIdx < currentIndex;
            const isCurrent = stepIdx === currentIndex;
            
            return (
              <li key={stage.id} className="relative text-center">
                <div className="flex items-center justify-center">
                  <div className={`
                    h-8 w-8 rounded-full flex items-center justify-center z-10
                    ${isCompleted ? 'bg-primary-500' : isCurrent ? 'bg-white border-2 border-primary-500 dark:bg-gray-900' : 'bg-white border-2 border-gray-300 dark:bg-gray-900 dark:border-gray-700'}
                  `}>
                    {isCompleted ? (
                      <Check className="h-5 w-5 text-white" />
                    ) : isCurrent ? (
                      <Circle className="h-2.5 w-2.5 fill-primary-500 text-primary-500" />
                    ) : (
                      <span className="h-2.5 w-2.5 rounded-full bg-transparent" />
                    )}
                  </div>
                </div>
                <div className="mt-3 hidden sm:block">
                  <span className={`text-xs font-medium ${isCurrent ? 'text-primary-600 dark:text-primary-400' : 'text-gray-500 dark:text-gray-400'}`}>
                    {stage.label}
                  </span>
                </div>
              </li>
            );
          })}
        </ul>
      </div>
    </div>
  );
}
