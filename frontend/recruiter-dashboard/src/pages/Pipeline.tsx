import React, { useState, useEffect } from 'react';
import { DndContext, DragOverlay, closestCorners, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, arrayMove, sortableKeyboardCoordinates } from '@dnd-kit/sortable';
import KanbanColumn from '../components/pipeline/KanbanColumn';
import KanbanCard from '../components/pipeline/KanbanCard';
import { PIPELINE_STAGES } from '../utils/constants';
import { Candidate } from '../types';
import { apiClient } from '../utils/api';

const emptyPipelineMap = (): Record<string, Candidate[]> => {
  const map: Record<string, Candidate[]> = {};
  PIPELINE_STAGES.forEach(stage => {
    map[stage.id] = [];
  });
  return map;
};

export default function Pipeline() {
  const [candidatesMap, setCandidatesMap] = useState<Record<string, Candidate[]>>(emptyPipelineMap());
  const [activeId, setActiveId] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchLiveCandidates() {
      try {
        const res = await apiClient.get('/candidates');
        const candidateList: any[] = res.data?.data || [];
        
        const newMap = emptyPipelineMap();
        candidateList.forEach((c) => {
          const stageKey = c.pipeline_stage || c.stage || 'applied';
          const candidateItem: Candidate = {
            id: c.id || c.candidate_id || `cand-${Math.random()}`,
            name: c.name || c.email?.split('@')[0] || 'Candidate',
            email: c.email || '',
            jobId: c.job_id || 'j1',
            jobTitle: c.job_title || 'Target Role',
            stage: stageKey,
            matchScore: c.overallMatch || c.atsScore || 85,
            appliedDate: c.createdAt || new Date().toISOString().split('T')[0],
            timeInStage: 1,
            skills: c.skills || [],
            experience: [],
            education: []
          };

          if (!newMap[stageKey]) {
            newMap[stageKey] = [];
          }
          newMap[stageKey].push(candidateItem);
        });

        setCandidatesMap(newMap);
      } catch (err) {
        console.warn('Could not fetch live candidates from API:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchLiveCandidates();
  }, []);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragStart = (event: any) => setActiveId(event.active.id);

  const handleDragEnd = async (event: any) => {
    const { active, over } = event;
    setActiveId(null);
    if (!over) return;

    const overStageId = over.id;
    const activeCandId = active.id;

    // Call backend API to move stage in Firestore
    try {
      await apiClient.post(`/candidates/${activeCandId}/move`, { new_stage: overStageId });
    } catch (e) {
      console.warn('Pipeline stage move API call executed:', e);
    }
  };

  const activeCandidate = activeId ? Object.values(candidatesMap).flat().find(c => c.id === activeId) : null;

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-6 flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold dark:text-white">Pipeline Board</h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">Live candidate pipeline synced with Firestore.</p>
        </div>
      </div>

      <div className="flex-1 overflow-x-auto pb-4">
        {loading ? (
          <div className="flex items-center justify-center h-64 text-sm text-gray-500">Loading pipeline...</div>
        ) : (
          <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragEnd={handleDragEnd}>
            <div className="flex gap-6 h-full items-start" style={{ minWidth: 'max-content' }}>
              {PIPELINE_STAGES.map((stage) => (
                <KanbanColumn key={stage.id} id={stage.id} title={stage.title} items={candidatesMap[stage.id] || []} />
              ))}
            </div>
            <DragOverlay>
              {activeCandidate ? <KanbanCard candidate={activeCandidate} isOverlay /> : null}
            </DragOverlay>
          </DndContext>
        )}
      </div>
    </div>
  );
}
