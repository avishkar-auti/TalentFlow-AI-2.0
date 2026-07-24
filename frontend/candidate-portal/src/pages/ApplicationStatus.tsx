import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, CardContent, CardHeader, CardTitle } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { StatusTimeline } from '../components/status/StatusTimeline';
import { CheckCircle2, Clock, Calendar, Video, Code, Users, Award, PlayCircle, Loader2 } from 'lucide-react';
import axios from 'axios';

// 7 Pipeline Stages
const STAGES = [
  { id: 'applied', label: 'Applied' },
  { id: 'screening', label: 'Screening' },
  { id: 'shortlisted', label: 'Shortlisted' },
  { id: 'ai_screening', label: 'AI Interview' },
  { id: 'hr_round', label: 'HR Round' },
  { id: 'technical', label: 'Technical' },
  { id: 'offer', label: 'Offer' }
];

export function ApplicationStatus() {
  const navigate = useNavigate();
  const [candidateData, setCandidateData] = useState<any>(null);
  const [interviews, setInterviews] = useState<any[]>([]);
  const [currentStage, setCurrentStage] = useState<string>('applied');
  const [timelineEvents, setTimelineEvents] = useState<any[]>([]);
  const [isTerminated, setIsTerminated] = useState<boolean>(false);
  const [loading, setLoading] = useState(true);

  // Real ATS data — populated from the candidate's actual resume analysis once available.
  // null fields render an "analysis pending" state instead of a fabricated score.
  const [atsDetails, setAtsDetails] = useState<any>({
    score: null,
    keywordMatch: null,
    skillOverlap: null,
    experienceMatch: null,
    educationMatch: null,
    sectionCompleteness: null,
    formattingQuality: null,
    matchedKeywords: [],
    missingKeywords: []
  });

  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    if (params.get('terminated') === 'true') {
      setIsTerminated(true);
    }
  }, []);

  useEffect(() => {
    async function fetchData() {
      let candId = localStorage.getItem('talentflow_candidate_id');
      
      try {
        if (!candId) {
          const listRes = await axios.get('http://localhost:8000/api/v1/candidates').catch(() => null);
          const cands = listRes?.data?.data;
          if (Array.isArray(cands) && cands.length > 0) {
            candId = cands[0].id || cands[0].candidateId;
            if (candId) localStorage.setItem('talentflow_candidate_id', candId);
          }
        }

        if (candId) {
          // Fetch Candidate Status
          const res = await axios.get(`http://localhost:8000/api/v1/candidates/${candId}`).catch(() => null);
          const data = res?.data?.data || null;
          
          if (data) {
            setCandidateData(data);
            const stage = data.pipeline_stage || data.stage || 'shortlisted';
            setCurrentStage(stage);

            // Pull the real ATS breakdown computed by the backend for this resume.
            const score = data.atsScore ?? data.ats_score ?? data.overallScore ?? null;
            const breakdown = data.atsBreakdown || {};
            if (score !== null) {
              setAtsDetails({
                score: Math.round(score),
                keywordMatch: breakdown.keyword_match ?? null,
                skillOverlap: breakdown.skill_overlap ?? null,
                experienceMatch: breakdown.experience_match ?? null,
                educationMatch: breakdown.education_match ?? null,
                sectionCompleteness: breakdown.section_completeness ?? null,
                formattingQuality: breakdown.formatting_quality ?? null,
                matchedKeywords: data.matched_keywords || [],
                missingKeywords: data.missing_keywords || []
              });
            }
          }

          // Fetch Interviews
          const interviewsRes = await axios.get(`http://localhost:8000/api/v1/interviews?candidate_id=${candId}`).catch(() => null);
          if (interviewsRes?.data?.data) {
            setInterviews(interviewsRes.data.data);
          } else {
            // Mock interviews for demo if API fails
            setInterviews([
              {
                id: 'int_ai_123',
                type: 'ai_screening',
                scheduled_time: new Date(Date.now() + 3600000).toISOString(),
                status: 'scheduled'
              }
            ]);
          }
        }
      } catch (e) {
        console.warn('Live candidate status fetch warning:', e);
      } finally {
        setLoading(false);
      }
    }

    fetchData();
  }, []);

  // Compute Pipeline Progress
  const currentStageIndex = STAGES.findIndex(s => s.id === currentStage);
  const isRejected = currentStage === 'rejected';

  // Render ATS Breakdown Bar
  const renderAtsBar = (label: string, value: number | null, weight: string) => (
    <div className="mb-3 last:mb-0">
      <div className="flex justify-between text-xs mb-1">
        <span className="font-medium text-gray-700 dark:text-gray-300">{label} <span className="text-gray-400">({weight})</span></span>
        <span className="font-semibold text-gray-900 dark:text-white">{value != null ? `${Math.round(value)}%` : '—'}</span>
      </div>
      <div className="h-1.5 w-full bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div
          className="h-full bg-primary-500 rounded-full transition-all duration-1000"
          style={{ width: `${value ?? 0}%` }}
        />
      </div>
    </div>
  );

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="flex flex-col items-center gap-4 text-primary-500">
          <Loader2 className="w-8 h-8 animate-spin" />
          <p className="text-sm font-medium">Loading your application dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-fade-in pb-16 pt-8">
      {/* Session Terminated Alert */}
      {isTerminated && (
        <div className="bg-red-500/10 border border-red-500/30 p-6 rounded-2xl flex items-start gap-4 shadow-sm">
          <div className="p-3 bg-red-500 text-white rounded-xl font-bold flex-shrink-0">5/5</div>
          <div>
            <h3 className="text-lg font-bold text-red-600 dark:text-red-400">Interview Session Terminated</h3>
            <p className="text-sm text-red-700/80 dark:text-red-300/80 mt-1">
              Your interview session was automatically closed after exceeding the maximum allowable proctoring warnings (5/5 warnings). Your video, frame logs, and session flags have been transmitted to the recruitment team for manual compliance review.
            </p>
          </div>
        </div>
      )}

      {/* Header */}
      <div>
        <h1 className="text-3xl font-extrabold text-gray-900 dark:text-white mb-2">Application Dashboard</h1>
        <p className="text-gray-600 dark:text-gray-400 flex items-center gap-2">
          {candidateData?.job_title || 'Software Engineer Candidate Profile'} 
          <span className="text-xs bg-gray-100 dark:bg-gray-800 px-2 py-0.5 rounded font-mono border border-gray-200 dark:border-gray-700">
            {localStorage.getItem('talentflow_applied_job_id') || 'JOB-1234'}
          </span>
        </p>
      </div>

      {/* Pipeline Progress (7 Stages) */}
      <Card className="overflow-hidden border-none shadow-lg shadow-gray-200/40 dark:shadow-none bg-white/80 dark:bg-gray-900/80 backdrop-blur-md">
        <CardContent className="p-8">
          {isRejected ? (
            <div className="text-center py-6">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-red-100 dark:bg-red-900/30 text-red-500 mb-4">
                <CheckCircle2 className="w-8 h-8" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 dark:text-white mb-2">Application Not Selected</h3>
              <p className="text-gray-500 max-w-md mx-auto">
                Thank you for your interest. Unfortunately, we are not moving forward with your application at this time. We will keep your resume on file for future opportunities.
              </p>
            </div>
          ) : (
            <div className="relative">
              {/* Progress Line */}
              <div className="absolute top-1/2 left-0 w-full h-1 bg-gray-200 dark:bg-gray-800 -translate-y-1/2 rounded-full z-0"></div>
              <div 
                className="absolute top-1/2 left-0 h-1 bg-primary-500 -translate-y-1/2 rounded-full z-0 transition-all duration-700 ease-in-out"
                style={{ width: `${(Math.max(0, currentStageIndex) / (STAGES.length - 1)) * 100}%` }}
              ></div>

              {/* Stage Nodes */}
              <div className="relative z-10 flex justify-between">
                {STAGES.map((stage, idx) => {
                  const isCompleted = currentStageIndex > idx;
                  const isCurrent = currentStageIndex === idx;
                  const isUpcoming = currentStageIndex < idx;

                  return (
                    <div key={stage.id} className="flex flex-col items-center gap-2 group">
                      <div 
                        className={`w-10 h-10 rounded-full flex items-center justify-center text-sm font-bold border-2 transition-all duration-300
                          ${isCompleted ? 'bg-primary-500 border-primary-500 text-white shadow-lg shadow-primary-500/30' : 
                            isCurrent ? 'bg-white dark:bg-gray-900 border-primary-500 text-primary-500 shadow-[0_0_0_4px] shadow-primary-500/20' : 
                            'bg-white dark:bg-gray-900 border-gray-200 dark:border-gray-700 text-gray-400'}`}
                      >
                        {isCompleted ? <CheckCircle2 className="w-5 h-5" /> : idx + 1}
                      </div>
                      <span className={`text-[11px] font-semibold uppercase tracking-wider text-center
                        ${isCurrent ? 'text-primary-600 dark:text-primary-400' : 
                          isCompleted ? 'text-gray-900 dark:text-gray-300' : 'text-gray-400'}`}
                      >
                        {stage.label}
                      </span>
                    </div>
                  );
                })}
              </div>
            </div>
          )}

          {/* Dynamic Stage CTA */}
          <div className="mt-10 p-6 bg-gray-50 dark:bg-gray-800/50 rounded-2xl border border-gray-100 dark:border-gray-700/50 flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex-1">
              <h4 className="text-lg font-bold text-gray-900 dark:text-white mb-1">
                {currentStage === 'screening' && 'Resume is being evaluated...'}
                {currentStage === 'shortlisted' && 'Resume Shortlisted! 🎉'}
                {currentStage === 'ai_screening' && 'Action Required: Complete AI Interview'}
                {currentStage === 'hr_round' && 'HR Interview Scheduled'}
                {currentStage === 'technical' && 'Technical Assessment Pending'}
                {currentStage === 'offer' && 'Congratulations! Offer Extended 🎊'}
              </h4>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                {currentStage === 'screening' && 'Our ATS is analyzing your profile against the job requirements.'}
                {currentStage === 'shortlisted' && 'Await interview invitation from recruiter or proceed if available below.'}
                {currentStage === 'ai_screening' && 'You have a pending asynchronous video interview.'}
                {currentStage === 'hr_round' && 'Join the live session with our HR representative at the scheduled time.'}
                {currentStage === 'technical' && 'Complete your live technical coding challenge with the engineering team.'}
                {currentStage === 'offer' && 'Please check your email for the official offer letter and next steps.'}
              </p>
            </div>
            
            <div className="w-full md:w-auto flex-shrink-0">
              {currentStage === 'screening' && (
                <Button disabled className="w-full md:w-auto opacity-80 cursor-wait">
                  <Loader2 className="w-4 h-4 mr-2 animate-spin" /> Evaluating...
                </Button>
              )}
              {currentStage === 'shortlisted' && (
                <Button className="w-full md:w-auto pointer-events-none bg-emerald-500 hover:bg-emerald-600">
                  Ready for Next Step
                </Button>
              )}
              {(currentStage === 'ai_screening' || currentStage === 'interview') && (
                <Button onClick={() => navigate(`/interview/${interviews[0]?.id || 'demo_ai_int'}`)} className="w-full md:w-auto group">
                  <PlayCircle className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" /> Start AI Interview
                </Button>
              )}
              {currentStage === 'hr_round' && (
                <Button onClick={() => navigate(`/interview/${interviews[0]?.id || 'demo_hr_int'}?mode=hr_round`)} className="w-full md:w-auto bg-blue-600 hover:bg-blue-700 group">
                  <Users className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" /> Join HR Interview
                </Button>
              )}
              {currentStage === 'technical' && (
                <Button onClick={() => navigate(`/technical/${interviews[0]?.id || 'demo_tech_int'}`)} className="w-full md:w-auto bg-violet-600 hover:bg-violet-700 group">
                  <Code className="w-4 h-4 mr-2 group-hover:scale-110 transition-transform" /> Start Technical Coding Test
                </Button>
              )}
              {currentStage === 'offer' && (
                <div className="flex gap-3 w-full md:w-auto">
                  <Button onClick={() => {
                    axios.post(`http://localhost:8000/api/v1/interviews/offer/${candidateData?.id}/accept`).then(() => {
                      alert('🎉 Congratulations! You accepted the offer.');
                      window.location.reload();
                    }).catch(e => alert('Error: ' + e.message));
                  }} className="flex-1 md:flex-none bg-emerald-600 hover:bg-emerald-700 text-white font-semibold">
                    ✅ Accept Offer
                  </Button>
                  <Button onClick={() => {
                    const reason = prompt('Why are you rejecting? (optional)');
                    axios.post(`http://localhost:8000/api/v1/interviews/offer/${candidateData?.id}/reject`, { reason }).then(() => {
                      alert('Offer rejected. Thank you for considering us.');
                      navigate('/jobs');
                    }).catch(e => alert('Error: ' + e.message));
                  }} className="flex-1 md:flex-none bg-gray-600 hover:bg-gray-700 text-white font-semibold">
                    ❌ Decline
                  </Button>
                </div>
              )}
            </div>
          </div>
        </CardContent>
      </Card>

      <div className="grid lg:grid-cols-3 gap-8">
        {/* Left Column: ATS & Upcoming */}
        <div className="lg:col-span-2 space-y-8">
          
          {/* ATS Score Section */}
          <Card className="overflow-hidden border-gray-200 dark:border-gray-800 shadow-sm">
            <CardHeader className="bg-gray-50/50 dark:bg-gray-800/30 border-b border-gray-100 dark:border-gray-800 pb-4">
              <div className="flex items-center justify-between">
                <CardTitle className="flex items-center gap-2 text-lg">
                  <Award className="w-5 h-5 text-primary-500" /> ATS Resume Match Analysis
                </CardTitle>
                {atsDetails.score >= 70 && (
                  <span className="bg-emerald-500/10 text-emerald-600 dark:text-emerald-400 px-3 py-1 rounded-full text-xs font-bold border border-emerald-500/20 shadow-sm flex items-center gap-1.5">
                    <CheckCircle2 className="w-3.5 h-3.5" /> Shortlisted!
                  </span>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-6">
              {atsDetails.score === null ? (
                <div className="text-center py-10">
                  <Loader2 className="w-8 h-8 mx-auto text-gray-400 mb-3 animate-spin" />
                  <p className="text-sm text-gray-500 dark:text-gray-400">Your resume is still being analyzed by our ATS engine. Check back shortly.</p>
                </div>
              ) : (
              <>
              <div className="flex flex-col md:flex-row gap-8 items-center md:items-start">

                {/* Score Ring */}
                <div className="flex-shrink-0 flex flex-col items-center justify-center mt-2">
                  <div className="relative w-36 h-36 flex items-center justify-center">
                    <svg className="w-full h-full transform -rotate-90">
                      <circle cx="72" cy="72" r="64" className="stroke-gray-100 dark:stroke-gray-800" strokeWidth="12" fill="none" />
                      <circle 
                        cx="72" cy="72" r="64" 
                        className={`transition-all duration-1000 ease-out ${atsDetails.score >= 70 ? 'stroke-emerald-500' : atsDetails.score >= 50 ? 'stroke-amber-500' : 'stroke-red-500'}`}
                        strokeWidth="12" fill="none" 
                        strokeDasharray="402.12"
                        strokeDashoffset={402.12 - (402.12 * atsDetails.score) / 100}
                        strokeLinecap="round"
                      />
                    </svg>
                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                      <span className="text-4xl font-extrabold text-gray-900 dark:text-white leading-none">{atsDetails.score}</span>
                      <span className="text-xs text-gray-500 font-medium mt-1">Match %</span>
                    </div>
                  </div>
                </div>

                {/* Breakdown Bars */}
                <div className="flex-1 w-full grid grid-cols-1 sm:grid-cols-2 gap-x-8 gap-y-4">
                  <div className="col-span-1 sm:col-span-2 text-sm font-semibold text-gray-900 dark:text-white mb-1">
                    6-Factor Breakdown
                  </div>
                  {renderAtsBar('Keyword Match', atsDetails.keywordMatch, '35%')}
                  {renderAtsBar('Skill Overlap', atsDetails.skillOverlap, '30%')}
                  {renderAtsBar('Experience Match', atsDetails.experienceMatch, '15%')}
                  {renderAtsBar('Education Match', atsDetails.educationMatch, '10%')}
                  {renderAtsBar('Section Completeness', atsDetails.sectionCompleteness, '5%')}
                  {renderAtsBar('Formatting Quality', atsDetails.formattingQuality, '5%')}
                </div>
              </div>

              {/* Keywords Tags */}
              <div className="mt-8 pt-6 border-t border-gray-100 dark:border-gray-800">
                <div className="grid sm:grid-cols-2 gap-6">
                  <div>
                    <h5 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Matched Keywords</h5>
                    <div className="flex flex-wrap gap-2">
                      {atsDetails.matchedKeywords.map((kw: string, i: number) => (
                        <span key={i} className="px-2.5 py-1 bg-emerald-50 dark:bg-emerald-900/20 text-emerald-700 dark:text-emerald-400 text-xs rounded-md border border-emerald-200 dark:border-emerald-800/50">
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                  <div>
                    <h5 className="text-xs font-bold text-gray-500 uppercase tracking-wider mb-3">Missing Keywords</h5>
                    <div className="flex flex-wrap gap-2">
                      {atsDetails.missingKeywords.map((kw: string, i: number) => (
                        <span key={i} className="px-2.5 py-1 bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400 text-xs rounded-md border border-red-200 dark:border-red-800/50">
                          {kw}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </div>
              </>
              )}
            </CardContent>
          </Card>

          {/* Upcoming Interviews */}
          <Card className="border-gray-200 dark:border-gray-800 shadow-sm">
            <CardHeader className="pb-4">
              <CardTitle className="text-lg flex items-center gap-2">
                <Calendar className="w-5 h-5 text-primary-500" /> Upcoming Interviews
              </CardTitle>
            </CardHeader>
            <CardContent>
              {interviews.length === 0 ? (
                <div className="text-center py-8 bg-gray-50 dark:bg-gray-800/30 rounded-xl border border-dashed border-gray-200 dark:border-gray-700">
                  <Calendar className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">No upcoming interviews scheduled yet.</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {interviews.map((intv) => {
                    const scheduledTime = new Date(intv.scheduled_time || Date.now() + 86400000);
                    const isSoon = scheduledTime.getTime() - Date.now() < 15 * 60000; // within 15 mins
                    const isReady = intv.status === 'in_progress' || isSoon;
                    
                    let icon = <Video className="w-5 h-5" />;
                    let title = "AI Screening Interview";
                    let navPath = `/interview/${intv.id}`;
                    
                    if (intv.type === 'hr_round' || currentStage === 'hr_round') {
                      icon = <Users className="w-5 h-5" />;
                      title = "HR Round (Live)";
                      navPath = `/interview/${intv.id}?mode=hr_round`;
                    } else if (intv.type === 'technical' || currentStage === 'technical') {
                      icon = <Code className="w-5 h-5" />;
                      title = "Technical Coding Assessment";
                      navPath = `/technical/${intv.id}`;
                    }

                    return (
                      <div key={intv.id} className="flex flex-col sm:flex-row items-center gap-4 p-4 rounded-2xl bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 shadow-sm hover:border-primary-300 dark:hover:border-primary-700 transition-colors">
                        <div className="w-12 h-12 flex-shrink-0 bg-primary-100 dark:bg-primary-900/30 text-primary-600 dark:text-primary-400 rounded-xl flex items-center justify-center">
                          {icon}
                        </div>
                        <div className="flex-1 text-center sm:text-left">
                          <h4 className="font-bold text-gray-900 dark:text-white text-base">{title}</h4>
                          <div className="flex items-center justify-center sm:justify-start gap-4 text-xs text-gray-500 mt-1.5">
                            <span className="flex items-center gap-1.5"><Clock className="w-3.5 h-3.5" /> {scheduledTime.toLocaleString([], { dateStyle: 'medium', timeStyle: 'short' })}</span>
                            <span className={`px-2 py-0.5 rounded-md font-medium capitalize ${intv.status === 'scheduled' ? 'bg-amber-100 text-amber-700 dark:bg-amber-900/30 dark:text-amber-400' : 'bg-primary-100 text-primary-700 dark:bg-primary-900/30 dark:text-primary-400'}`}>
                              {intv.status || 'scheduled'}
                            </span>
                          </div>
                        </div>
                        <div className="w-full sm:w-auto mt-2 sm:mt-0 flex-shrink-0">
                          <Button 
                            disabled={!isReady && intv.status !== 'in_progress'} 
                            onClick={() => navigate(navPath)}
                            className="w-full sm:w-auto"
                            variant={isReady ? 'primary' : 'outline'}
                          >
                            Join Interview
                          </Button>
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </CardContent>
          </Card>
        </div>

        {/* Right Column: Timeline */}
        <div className="space-y-6">
          <Card className="border-gray-200 dark:border-gray-800 shadow-sm h-full">
            <CardHeader className="pb-2 border-b border-gray-100 dark:border-gray-800">
              <CardTitle className="text-lg">Activity Timeline</CardTitle>
            </CardHeader>
            <CardContent className="pt-6">
              <StatusTimeline events={[
                {
                  id: '1',
                  title: 'Application Submitted',
                  description: 'Resume received & scanned by ATS.',
                  date: new Date(Date.now() - 86400000 * 2).toISOString(),
                  isComplete: true
                },
                {
                  id: '2',
                  title: 'Resume Shortlisted',
                  description: 'Profile matched job requirements.',
                  date: new Date(Date.now() - 86400000).toISOString(),
                  isComplete: currentStageIndex >= 2
                },
                {
                  id: '3',
                  title: 'AI Screening Invite',
                  description: 'Invitation sent for async interview.',
                  date: new Date().toISOString(),
                  isComplete: currentStageIndex >= 3
                },
                {
                  id: '4',
                  title: 'HR Round',
                  description: 'Live discussion regarding fit.',
                  date: new Date(Date.now() + 86400000).toISOString(),
                  isComplete: currentStageIndex >= 4
                },
                {
                  id: '5',
                  title: 'Technical Assessment',
                  description: 'Live coding environment evaluation.',
                  date: new Date(Date.now() + 86400000 * 2).toISOString(),
                  isComplete: currentStageIndex >= 5
                }
              ]} />
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
