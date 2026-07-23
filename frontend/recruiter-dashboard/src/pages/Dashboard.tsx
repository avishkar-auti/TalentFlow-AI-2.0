import React, { useEffect, useState } from 'react';
import { Users, Briefcase, Calendar, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip } from 'recharts';
import { apiClient } from '../utils/api';

export default function Dashboard() {
  const [statsData, setStatsData] = useState({
    totalCandidates: 0,
    openJobs: 0,
    interviewsScheduled: 0,
    hiredCount: 0
  });

  const [funnelData, setFunnelData] = useState<Array<{ name: string; value: number }>>([
    { name: 'Applied', value: 0 },
    { name: 'Screening', value: 0 },
    { name: 'Recruiter Review', value: 0 },
    { name: 'Interview', value: 0 },
    { name: 'Decision', value: 0 },
    { name: 'Hired', value: 0 }
  ]);

  const [activities, setActivities] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    async function fetchDashboardData() {
      try {
        const [statsRes, pipelineRes, activityRes] = await Promise.allSettled([
          apiClient.get('/dashboard/stats'),
          apiClient.get('/dashboard/pipeline'),
          apiClient.get('/dashboard/activity')
        ]);

        if (statsRes.status === 'fulfilled' && statsRes.value.data?.data) {
          const d = statsRes.value.data.data;
          setStatsData({
            totalCandidates: d.total_candidates || 0,
            openJobs: d.open_jobs || 0,
            interviewsScheduled: d.interviews_scheduled || 0,
            hiredCount: d.hired_count || 0
          });
        }

        if (pipelineRes.status === 'fulfilled' && pipelineRes.value.data?.data) {
          const p = pipelineRes.value.data.data;
          setFunnelData([
            { name: 'Applied', value: p.applied || 0 },
            { name: 'Screening', value: p.screening || 0 },
            { name: 'Review', value: p.recruiter_review || 0 },
            { name: 'Interview', value: (p.interview_scheduled || 0) + (p.interview_completed || 0) },
            { name: 'Decision', value: p.decision || 0 },
            { name: 'Hired', value: p.hired || 0 }
          ]);
        }

        if (activityRes.status === 'fulfilled' && activityRes.value.data?.data) {
          setActivities(activityRes.value.data.data || []);
        }
      } catch (err) {
        console.warn('Dashboard live API fetch warning, displaying live state:', err);
      } finally {
        setLoading(false);
      }
    }

    fetchDashboardData();
  }, []);

  const stats = [
    { label: 'Total Candidates', value: statsData.totalCandidates, icon: Users, color: 'text-blue-500' },
    { label: 'Open Jobs', value: statsData.openJobs, icon: Briefcase, color: 'text-purple-500' },
    { label: 'Interviews Scheduled', value: statsData.interviewsScheduled, icon: Calendar, color: 'text-teal-500' },
    { label: 'Total Hired', value: statsData.hiredCount, icon: TrendingUp, color: 'text-orange-500' },
  ];

  return (
    <div className="space-y-6 animate-fade-in pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold dark:text-white">Dashboard Overview</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Live metrics connected to FastAPI backend & Firestore.</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="glass-card p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
                <h3 className="text-3xl font-bold dark:text-white mt-2">{loading ? '...' : stat.value}</h3>
              </div>
              <div className={`p-3 rounded-xl bg-opacity-10 dark:bg-opacity-20 ${stat.color.replace('text', 'bg')}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
            <div className="mt-4 text-xs text-gray-400">
              Live Firestore count
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 lg:col-span-2 h-96">
          <h3 className="text-lg font-bold dark:text-white mb-6">Real-Time Hiring Funnel</h3>
          <ResponsiveContainer width="100%" height="100%">
            <BarChart data={funnelData} layout="vertical" margin={{ top: 0, right: 0, left: 20, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#374151" />
              <XAxis type="number" stroke="#9ca3af" />
              <YAxis dataKey="name" type="category" stroke="#9ca3af" />
              <Tooltip cursor={{fill: '#1e293b'}} contentStyle={{backgroundColor: '#0f172a', border: 'none', borderRadius: '8px', color: '#fff'}} />
              <Bar dataKey="value" fill="#3b82f6" radius={[0, 4, 4, 0]} barSize={32} />
            </BarChart>
          </ResponsiveContainer>
        </div>
        
        <div className="glass-card p-6 overflow-hidden flex flex-col">
          <h3 className="text-lg font-bold dark:text-white mb-4">Recent System Activity</h3>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {activities.length === 0 ? (
              <p className="text-xs text-gray-500 dark:text-gray-400 italic">No recent activities logged yet.</p>
            ) : (
              activities.map((act, i) => (
                <div key={i} className="flex gap-4 relative">
                  <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1 z-10">
                    <div className="w-2 h-2 rounded-full bg-primary"></div>
                  </div>
                  <div>
                    <p className="text-sm dark:text-gray-200">{act.details?.user_facing_status || act.action}</p>
                    <p className="text-xs text-gray-500 mt-1">{act.agent_name || 'System'}</p>
                  </div>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
