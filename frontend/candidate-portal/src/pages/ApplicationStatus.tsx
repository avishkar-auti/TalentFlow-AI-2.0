import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { PipelineProgress } from '../components/status/PipelineProgress';
import { StatusTimeline } from '../components/status/StatusTimeline';
import { STATUS_MESSAGES } from '../utils/constants';
import axios from 'axios';

export function ApplicationStatus() {
  const navigate = useNavigate();
  const [candidateData, setCandidateData] = useState<any>(null);
  const [currentStage, setCurrentStage] = useState<string>('applied');
  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);

  useEffect(() => {
    async function fetchStatus() {
      const candId = localStorage.getItem('talentflow_candidate_id');
      if (!candId) return;

      try {
        const res = await axios.get(`http://localhost:8000/api/v1/candidates/${candId}`);
        const data = res.data?.data;
        if (data) {
          setCandidateData(data);
          const stage = data.pipeline_stage || 'screening';
          setCurrentStage(stage);

          setTimelineEvents([
            {
              id: '1',
              title: 'Application Submitted',
              description: 'Your resume was successfully received & scanned by ATS.',
              date: data.createdAt || new Date().toISOString(),
              isComplete: true
            },
            {
              id: '2',
              title: 'Resume & AST Analysis',
              description: `Qualifications scanned with ATS match score of ${data.atsScore || 88}%.`,
              date: new Date().toISOString(),
              isComplete: true
            },
            {
              id: '3',
              title: 'AI Interview Room',
              description: 'You are invited to complete your live AI interview.',
              date: new Date().toISOString(),
              isComplete: stage === 'interview_completed'
            }
          ]);
        }
      } catch (e) {
        console.warn('Live candidate status fetch warning:', e);
      }
    }

    fetchStatus();
  }, []);

  return (
    <div className="max-w-4xl mx-auto space-y-8 animate-fade-in">
      <div>
        <h1 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">Application Status</h1>
        <p className="text-gray-600 dark:text-gray-400">
          {candidateData?.job_title || 'Software Engineer'}
        </p>
      </div>

      <Card>
        <CardContent className="pt-6 pb-2">
          <PipelineProgress currentStage={currentStage} />
        </CardContent>
      </Card>

      <div className="grid md:grid-cols-3 gap-8">
        <div className="md:col-span-2 space-y-6">
          <Card>
            <CardHeader>
              <CardTitle>Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <StatusTimeline events={timelineEvents.length > 0 ? timelineEvents : [
                {
                  id: '1',
                  title: 'Application Submitted',
                  description: 'Your resume has been uploaded.',
                  date: new Date().toISOString(),
                  isComplete: true
                }
              ]} />
            </CardContent>
          </Card>
        </div>

        <div className="space-y-6">
          <Card className="bg-primary-50 dark:bg-primary-900/20 border-primary-200 dark:border-primary-800">
            <CardHeader>
              <CardTitle className="text-primary-800 dark:text-primary-300">Next Step</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <p className="text-sm text-primary-700 dark:text-primary-400">
                {STATUS_MESSAGES[currentStage] || 'Your application is progressing smoothly through review.'}
              </p>
              <Button 
                className="w-full" 
                onClick={() => navigate(`/interview/${candidateData?.id || 'demo-int-1'}`)}
              >
                Start AI Interview Now
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
