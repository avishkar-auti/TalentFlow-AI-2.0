import React from 'react';
import { CheckCircle, AlertTriangle, Lightbulb } from 'lucide-react';

export default function AISummary() {
  return (
    <div className="glass-card p-6 bg-gradient-to-br from-blue-50/50 to-purple-50/50 dark:from-blue-900/10 dark:to-purple-900/10 border-blue-100 dark:border-blue-900/30">
      <div className="flex items-center gap-2 mb-4">
        <Lightbulb className="w-5 h-5 text-primary" />
        <h3 className="text-lg font-bold dark:text-white">Analysis Summary</h3>
      </div>
      
      <p className="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-6">
        The candidate demonstrates strong alignment with the technical requirements, particularly in modern frontend frameworks. Their experience scaling applications at previous roles directly matches the challenges of this position.
      </p>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div className="bg-white/60 dark:bg-navy-900/60 p-4 rounded-xl border border-green-100 dark:border-green-900/30">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-green-700 dark:text-green-400 mb-3">
            <CheckCircle className="w-4 h-4" /> Key Strengths
          </h4>
          <ul className="space-y-2">
            <li className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
              <span className="mt-1 w-1 h-1 rounded-full bg-green-500 flex-shrink-0"></span>
              Extensive React and TypeScript background
            </li>
            <li className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
              <span className="mt-1 w-1 h-1 rounded-full bg-green-500 flex-shrink-0"></span>
              History of performance optimization
            </li>
          </ul>
        </div>
        
        <div className="bg-white/60 dark:bg-navy-900/60 p-4 rounded-xl border border-yellow-100 dark:border-yellow-900/30">
          <h4 className="flex items-center gap-2 text-sm font-semibold text-yellow-700 dark:text-yellow-500 mb-3">
            <AlertTriangle className="w-4 h-4" /> Areas for Review
          </h4>
          <ul className="space-y-2">
            <li className="text-sm text-gray-600 dark:text-gray-400 flex items-start gap-2">
              <span className="mt-1 w-1 h-1 rounded-full bg-yellow-500 flex-shrink-0"></span>
              Limited experience with backend systems (Node.js)
            </li>
          </ul>
        </div>
      </div>
      
      <div className="mt-6 pt-4 border-t border-gray-200/50 dark:border-gray-700/50">
        <span className="text-xs font-semibold uppercase text-gray-500">Recommendation:</span>
        <span className="ml-2 text-sm font-medium text-gray-900 dark:text-white">Strong proceed to technical interview.</span>
      </div>
    </div>
  );
}
