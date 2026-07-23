import React from 'react';
import { useDroppable } from '@dnd-kit/core';
import { SortableContext, verticalListSortingStrategy } from '@dnd-kit/sortable';
import KanbanCard from './KanbanCard';
import { Candidate } from '../../types';

interface KanbanColumnProps {
  id: string;
  title: string;
  items: Candidate[];
}

export default function KanbanColumn({ id, title, items }: KanbanColumnProps) {
  const { setNodeRef } = useDroppable({ id });

  return (
    <div className="w-80 flex flex-col h-full max-h-full bg-gray-100/50 dark:bg-navy-800/30 rounded-xl border border-gray-200/50 dark:border-gray-700/50">
      <div className="p-4 border-b border-gray-200/50 dark:border-gray-700/50 flex justify-between items-center">
        <h3 className="font-semibold text-sm dark:text-gray-200">{title}</h3>
        <span className="bg-white dark:bg-navy-900 text-xs px-2 py-1 rounded-full font-medium dark:text-gray-400">
          {items.length}
        </span>
      </div>
      <div ref={setNodeRef} className="flex-1 p-3 overflow-y-auto space-y-3">
        <SortableContext items={items.map(i => i.id)} strategy={verticalListSortingStrategy}>
          {items.map((item) => (
            <KanbanCard key={item.id} candidate={item} />
          ))}
        </SortableContext>
      </div>
    </div>
  );
}
