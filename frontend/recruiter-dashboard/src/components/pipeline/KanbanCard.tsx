import React from 'react';
import { useSortable } from '@dnd-kit/sortable';
import { CSS } from '@dnd-kit/utilities';
import { Candidate } from '../../types';
import { Clock } from 'lucide-react';
import { useNavigate } from 'react-router-dom';

interface KanbanCardProps {
  candidate: Candidate;
  isOverlay?: boolean;
}

export default function KanbanCard({ candidate, isOverlay }: KanbanCardProps) {
  const navigate = useNavigate();
  const { attributes, listeners, setNodeRef, transform, transition, isDragging } = useSortable({
    id: candidate.id,
    data: { type: 'Candidate', candidate }
  });

  const style = {
    transform: CSS.Transform.toString(transform),
    transition,
    opacity: isDragging ? 0.4 : 1,
  };

  const getScoreColor = (score: number) => {
    if (score >= 90) return 'text-green-500 bg-green-500/10 border-green-500/20';
    if (score >= 70) return 'text-yellow-500 bg-yellow-500/10 border-yellow-500/20';
    return 'text-red-500 bg-red-500/10 border-red-500/20';
  };

  return (
    <div
      ref={setNodeRef}
      style={style}
      {...attributes}
      {...listeners}
      onClick={() => !isDragging && navigate(`/candidates/${candidate.id}`)}
      className={`glass-card p-4 cursor-grab active:cursor-grabbing hover:border-primary/50 transition-colors ${
        isOverlay ? 'rotate-2 scale-105 shadow-2xl' : ''
      }`}
    >
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-sm dark:text-white">{candidate.name}</h4>
        <span className={`text-xs px-2 py-0.5 rounded border font-medium ${getScoreColor(candidate.matchScore)}`}>
          {candidate.matchScore}%
        </span>
      </div>
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 truncate">{candidate.jobTitle}</p>
      
      <div className="flex items-center text-xs text-gray-400 mt-2">
        <Clock className="w-3 h-3 mr-1" />
        <span>{candidate.timeInStage}d in stage</span>
      </div>
    </div>
  );
}
