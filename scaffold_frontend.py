import os
import json

base_dir = r"C:\Users\avish\.gemini\antigravity\scratch\TalentFlow-AI\frontend\recruiter-dashboard\src"

files = {
    "context/AuthContext.tsx": """import React, { createContext, useContext, useState, ReactNode } from 'react';
import { User } from '../types';

interface AuthContextType {
  user: User | null;
  login: (token: string, userData: User) => void;
  logout: () => void;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(() => {
    const saved = localStorage.getItem('user');
    return saved ? JSON.parse(saved) : null;
  });

  const login = (token: string, userData: User) => {
    localStorage.setItem('token', token);
    localStorage.setItem('user', JSON.stringify(userData));
    setUser(userData);
  };

  const logout = () => {
    localStorage.removeItem('token');
    localStorage.removeItem('user');
    setUser(null);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};
""",
    "hooks/useApi.ts": """import { useState, useCallback } from 'react';
import { apiClient } from '../utils/api';
import { AxiosRequestConfig } from 'axios';

export const useApi = <T,>() => {
  const [data, setData] = useState<T | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const request = useCallback(async (config: AxiosRequestConfig) => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient(config);
      setData(response.data);
      return response.data;
    } catch (err: any) {
      const message = err.response?.data?.message || err.message || 'An error occurred';
      setError(message);
      throw err;
    } finally {
      setLoading(false);
    }
  }, []);

  return { data, loading, error, request };
};
""",
    "components/layout/Sidebar.tsx": """import React from 'react';
import { NavLink } from 'react-router-dom';
import { LayoutDashboard, Users, Briefcase, Calendar, FileBarChart, Settings } from 'lucide-react';
import { clsx } from 'clsx';

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: FileBarChart, label: 'Pipeline', path: '/pipeline' },
  { icon: Briefcase, label: 'Jobs', path: '/jobs' },
  { icon: Users, label: 'Candidates', path: '/candidates' },
  { icon: Calendar, label: 'Interviews', path: '/interviews' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

export default function Sidebar() {
  return (
    <aside className="w-64 glass border-r flex flex-col h-full flex-shrink-0 z-20 hidden md:flex">
      <div className="h-16 flex items-center px-6 border-b border-gray-200/50 dark:border-gray-700/50">
        <span className="text-xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent">
          TalentFlow-AI
        </span>
      </div>
      <nav className="flex-1 py-4 px-3 space-y-1 overflow-y-auto">
        {navItems.map((item) => (
          <NavLink
            key={item.path}
            to={item.path}
            className={({ isActive }) =>
              clsx(
                'flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-colors duration-200',
                isActive
                  ? 'bg-primary/10 text-primary dark:bg-primary/20'
                  : 'text-gray-700 hover:bg-gray-100 dark:text-gray-300 dark:hover:bg-navy-800'
              )
            }
          >
            <item.icon className="w-5 h-5 mr-3 flex-shrink-0" />
            {item.label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
""",
    "components/layout/Header.tsx": """import React from 'react';
import { Search, Bell, Sun, Moon } from 'lucide-react';

export default function Header() {
  const [isDark, setIsDark] = React.useState(true);

  const toggleTheme = () => {
    setIsDark(!isDark);
    document.documentElement.classList.toggle('dark');
  };

  return (
    <header className="h-16 glass border-b flex items-center justify-between px-6 z-10">
      <div className="flex-1 max-w-md flex items-center">
        <div className="relative w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search candidates, jobs..."
            className="w-full pl-10 pr-4 py-2 bg-gray-100/50 dark:bg-navy-900/50 border-none rounded-full focus:ring-2 focus:ring-primary/50 outline-none text-sm"
          />
        </div>
      </div>
      <div className="flex items-center space-x-4">
        <button onClick={toggleTheme} className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors">
          {isDark ? <Sun className="w-5 h-5 text-gray-300" /> : <Moon className="w-5 h-5 text-gray-600" />}
        </button>
        <button className="p-2 rounded-full hover:bg-gray-100 dark:hover:bg-navy-800 transition-colors relative">
          <Bell className="w-5 h-5 text-gray-600 dark:text-gray-300" />
          <span className="absolute top-1.5 right-1.5 w-2 h-2 bg-red-500 rounded-full"></span>
        </button>
        <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-primary to-secondary p-[2px] cursor-pointer">
          <div className="w-full h-full rounded-full bg-white dark:bg-navy-900 flex items-center justify-center overflow-hidden">
            <img src="https://ui-avatars.com/api/?name=Recruiter&background=random" alt="User" className="w-full h-full object-cover" />
          </div>
        </div>
      </div>
    </header>
  );
}
""",
    "components/layout/MainLayout.tsx": """import React from 'react';
import { Outlet, Navigate } from 'react-router-dom';
import Sidebar from './Sidebar';
import Header from './Header';
import { useAuth } from '../../context/AuthContext';

export default function MainLayout() {
  const { user } = useAuth();

  // For dev purposes, if you want to bypass auth, comment this out:
  // if (!user) return <Navigate to="/login" replace />;

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50 dark:bg-navy-900">
      <Sidebar />
      <div className="flex flex-col flex-1 min-w-0 overflow-hidden">
        <Header />
        <main className="flex-1 overflow-y-auto p-6 relative">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
""",
    "pages/Login.tsx": """import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { Mail, Lock, ArrowRight } from 'lucide-react';

export default function Login() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const navigate = useNavigate();
  const { login } = useAuth();

  const handleLogin = (e: React.FormEvent) => {
    e.preventDefault();
    // Dummy login
    login('dummy-token', { id: '1', email, name: 'Test User', role: 'recruiter' });
    navigate('/dashboard');
  };

  return (
    <div className="min-h-screen flex items-center justify-center relative bg-navy-900 overflow-hidden">
      {/* Background blobs */}
      <div className="absolute top-[-20%] left-[-10%] w-[500px] h-[500px] rounded-full bg-primary/20 blur-[100px]"></div>
      <div className="absolute bottom-[-20%] right-[-10%] w-[600px] h-[600px] rounded-full bg-secondary/20 blur-[120px]"></div>
      
      <div className="glass-card w-full max-w-md p-8 relative z-10 animate-slide-up">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-primary to-accent mb-2">
            TalentFlow-AI
          </h1>
          <p className="text-gray-400">Sign in to your recruiter dashboard</p>
        </div>
        
        <form onSubmit={handleLogin} className="space-y-6">
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="email" 
                value={email}
                onChange={e => setEmail(e.target.value)}
                className="w-full bg-navy-900/50 border border-gray-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                placeholder="name@company.com"
                required
              />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">Password</label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-500" />
              <input 
                type="password" 
                value={password}
                onChange={e => setPassword(e.target.value)}
                className="w-full bg-navy-900/50 border border-gray-700 rounded-lg py-2.5 pl-10 pr-4 text-white focus:ring-2 focus:ring-primary focus:border-transparent outline-none transition-all"
                placeholder="••••••••"
                required
              />
            </div>
          </div>
          
          <button 
            type="submit"
            className="w-full bg-gradient-to-r from-primary to-accent hover:from-primary/90 hover:to-accent/90 text-white font-medium py-2.5 rounded-lg flex items-center justify-center transition-all shadow-lg shadow-primary/25"
          >
            Sign In <ArrowRight className="ml-2 w-4 h-4" />
          </button>
        </form>
        
        <p className="mt-6 text-center text-sm text-gray-400">
          Don't have an account? <Link to="/register" className="text-primary hover:text-primary/80">Register</Link>
        </p>
      </div>
    </div>
  );
}
""",
    "pages/Register.tsx": """import React from 'react';
import { Link } from 'react-router-dom';

export default function Register() {
  return (
    <div className="min-h-screen flex items-center justify-center relative bg-navy-900 overflow-hidden">
      <div className="glass-card w-full max-w-md p-8 relative z-10">
        <h2 className="text-2xl font-bold text-white mb-6 text-center">Create Account</h2>
        <form className="space-y-4">
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" placeholder="Name" />
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" type="email" placeholder="Email" />
          <input className="w-full bg-navy-900/50 border border-gray-700 rounded-lg p-2.5 text-white" type="password" placeholder="Password" />
          <button className="w-full bg-primary text-white py-2.5 rounded-lg">Register</button>
        </form>
        <p className="mt-4 text-center text-sm text-gray-400">
          Already have an account? <Link to="/login" className="text-primary">Login</Link>
        </p>
      </div>
    </div>
  );
}
""",
    "pages/Dashboard.tsx": """import React from 'react';
import { Users, Briefcase, Calendar, TrendingUp } from 'lucide-react';
import { ResponsiveContainer, AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, BarChart, Bar } from 'recharts';

const stats = [
  { label: 'Total Candidates', value: '2,845', icon: Users, color: 'text-blue-500', trend: '+12%' },
  { label: 'Open Jobs', value: '24', icon: Briefcase, color: 'text-purple-500', trend: '+2' },
  { label: 'Interviews Today', value: '8', icon: Calendar, color: 'text-teal-500', trend: 'Same' },
  { label: 'Hiring Rate', value: '4.2%', icon: TrendingUp, color: 'text-orange-500', trend: '+0.4%' },
];

const funnelData = [
  { name: 'Applied', value: 1000 },
  { name: 'Screening', value: 800 },
  { name: 'Interview', value: 300 },
  { name: 'Offer', value: 50 },
  { name: 'Hired', value: 40 },
];

export default function Dashboard() {
  return (
    <div className="space-y-6 animate-fade-in pb-10">
      <div className="flex justify-between items-end">
        <div>
          <h1 className="text-2xl font-bold dark:text-white">Dashboard Overview</h1>
          <p className="text-gray-500 dark:text-gray-400 mt-1">Welcome back! Here is your recruitment summary.</p>
        </div>
        <button className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition-colors">
          Download Report
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat, idx) => (
          <div key={idx} className="glass-card p-6">
            <div className="flex justify-between items-start">
              <div>
                <p className="text-sm font-medium text-gray-500 dark:text-gray-400">{stat.label}</p>
                <h3 className="text-3xl font-bold dark:text-white mt-2">{stat.value}</h3>
              </div>
              <div className={`p-3 rounded-xl bg-opacity-10 dark:bg-opacity-20 ${stat.color.replace('text', 'bg')}`}>
                <stat.icon className={`w-6 h-6 ${stat.color}`} />
              </div>
            </div>
            <div className="mt-4 text-sm text-green-500 font-medium">
              {stat.trend} <span className="text-gray-400 font-normal">vs last month</span>
            </div>
          </div>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="glass-card p-6 lg:col-span-2 h-96">
          <h3 className="text-lg font-bold dark:text-white mb-6">Hiring Funnel</h3>
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
          <h3 className="text-lg font-bold dark:text-white mb-4">Recent Activity</h3>
          <div className="flex-1 overflow-y-auto pr-2 space-y-4">
            {[1, 2, 3, 4, 5].map((i) => (
              <div key={i} className="flex gap-4 relative">
                {i !== 5 && <div className="absolute left-[11px] top-8 bottom-[-16px] w-[2px] bg-gray-200 dark:bg-gray-700"></div>}
                <div className="w-6 h-6 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1 z-10">
                  <div className="w-2 h-2 rounded-full bg-primary"></div>
                </div>
                <div>
                  <p className="text-sm dark:text-gray-200"><span className="font-semibold">Sarah Jenkins</span> moved to Interview</p>
                  <p className="text-xs text-gray-500 mt-1">{i * 2} hours ago</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
""",
    "pages/Pipeline.tsx": """import React, { useState } from 'react';
import { DndContext, DragOverlay, closestCorners, KeyboardSensor, PointerSensor, useSensor, useSensors } from '@dnd-kit/core';
import { SortableContext, arrayMove, sortableKeyboardCoordinates, horizontalListSortingStrategy } from '@dnd-kit/sortable';
import KanbanColumn from '../components/pipeline/KanbanColumn';
import KanbanCard from '../components/pipeline/KanbanCard';
import { PIPELINE_STAGES } from '../utils/constants';
import { Candidate } from '../types';

// Dummy data
const initialCandidates: Record<string, Candidate[]> = {
  'applied': [
    { id: 'c1', name: 'Alice Smith', email: 'alice@ext.com', jobId: 'j1', jobTitle: 'Frontend Eng', stage: 'applied', matchScore: 92, appliedDate: '2023-10-01', timeInStage: 2, skills: [], experience: [], education: [] }
  ],
  'screening': [
    { id: 'c2', name: 'Bob Jones', email: 'bob@ext.com', jobId: 'j1', jobTitle: 'Frontend Eng', stage: 'screening', matchScore: 85, appliedDate: '2023-09-28', timeInStage: 5, skills: [], experience: [], education: [] }
  ],
  'review': [],
  'interview_scheduled': [],
  'interview_completed': [],
  'decision': [],
  'hired': [],
  'rejected': []
};

export default function Pipeline() {
  const [candidatesMap, setCandidatesMap] = useState(initialCandidates);
  const [activeId, setActiveId] = useState<string | null>(null);

  const sensors = useSensors(
    useSensor(PointerSensor, { activationConstraint: { distance: 5 } }),
    useSensor(KeyboardSensor, { coordinateGetter: sortableKeyboardCoordinates })
  );

  const handleDragStart = (event: any) => setActiveId(event.active.id);

  const handleDragOver = (event: any) => {
    const { active, over } = event;
    if (!over) return;

    const activeId = active.id;
    const overId = over.id;

    // Logic to move between columns if activeId and overId are in different columns
    // (Simplified for this boilerplate)
  };

  const handleDragEnd = (event: any) => {
    setActiveId(null);
    const { active, over } = event;
    if (!over) return;
    
    // In a full implementation, we update state to move card across columns
  };

  const activeCandidate = activeId ? Object.values(candidatesMap).flat().find(c => c.id === activeId) : null;

  return (
    <div className="h-full flex flex-col animate-fade-in">
      <div className="mb-6 flex justify-between items-center">
        <h1 className="text-2xl font-bold dark:text-white">Pipeline Board</h1>
        <select className="bg-white dark:bg-navy-800 border border-gray-200 dark:border-gray-700 rounded-lg px-4 py-2 text-sm">
          <option>All Jobs</option>
          <option>Frontend Engineer</option>
        </select>
      </div>

      <div className="flex-1 overflow-x-auto pb-4">
        <DndContext sensors={sensors} collisionDetection={closestCorners} onDragStart={handleDragStart} onDragOver={handleDragOver} onDragEnd={handleDragEnd}>
          <div className="flex gap-6 h-full items-start" style={{ minWidth: 'max-content' }}>
            {PIPELINE_STAGES.map((stage) => (
              <KanbanColumn key={stage.id} id={stage.id} title={stage.title} items={candidatesMap[stage.id] || []} />
            ))}
          </div>
          <DragOverlay>
            {activeCandidate ? <KanbanCard candidate={activeCandidate} isOverlay /> : null}
          </DragOverlay>
        </DndContext>
      </div>
    </div>
  );
}
""",
    "components/pipeline/KanbanColumn.tsx": """import React from 'react';
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
""",
    "components/pipeline/KanbanCard.tsx": """import React from 'react';
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
""",
    "pages/CandidateProfile.tsx": """import React from 'react';
import { useParams } from 'react-router-dom';
import { Mail, Phone, MapPin, Download, CheckCircle, AlertTriangle, Lightbulb } from 'lucide-react';
import AISummary from '../components/candidates/AISummary';

export default function CandidateProfile() {
  const { id } = useParams();
  const [activeTab, setActiveTab] = React.useState('overview');

  return (
    <div className="animate-fade-in pb-20">
      {/* Header */}
      <div className="glass-card p-6 mb-6">
        <div className="flex flex-col md:flex-row justify-between md:items-center gap-4">
          <div className="flex items-center gap-5">
            <div className="w-20 h-20 rounded-full bg-gradient-to-br from-primary to-secondary p-1">
              <div className="w-full h-full rounded-full bg-white dark:bg-navy-900 flex items-center justify-center overflow-hidden">
                <img src="https://ui-avatars.com/api/?name=Alice+Smith&size=150" alt="Avatar" />
              </div>
            </div>
            <div>
              <h1 className="text-2xl font-bold dark:text-white">Alice Smith</h1>
              <p className="text-gray-500 dark:text-gray-400 text-sm mt-1">Applying for: Frontend Engineer</p>
              <div className="flex gap-4 mt-2 text-xs text-gray-500">
                <span className="flex items-center gap-1"><Mail className="w-3 h-3" /> alice@example.com</span>
                <span className="flex items-center gap-1"><MapPin className="w-3 h-3" /> New York, NY</span>
              </div>
            </div>
          </div>
          
          <div className="flex gap-3">
            <button className="px-4 py-2 bg-gray-100 dark:bg-navy-800 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium hover:bg-gray-200 dark:hover:bg-navy-700 transition">
              Reject
            </button>
            <button className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-primary/90 transition shadow-lg shadow-primary/25">
              Move to Next Stage
            </button>
          </div>
        </div>

        {/* Tabs */}
        <div className="flex gap-6 mt-8 border-b border-gray-200 dark:border-gray-800">
          {['overview', 'resume', 'interview', 'report'].map(tab => (
            <button
              key={tab}
              onClick={() => setActiveTab(tab)}
              className={`pb-3 text-sm font-medium capitalize transition-colors relative ${
                activeTab === tab ? 'text-primary' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'
              }`}
            >
              {tab}
              {activeTab === tab && (
                <span className="absolute bottom-0 left-0 w-full h-0.5 bg-primary rounded-t-full"></span>
              )}
            </button>
          ))}
        </div>
      </div>

      {/* Content */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {activeTab === 'overview' && (
            <>
              <AISummary />
              
              <div className="glass-card p-6">
                <h3 className="text-lg font-bold dark:text-white mb-4">Experience</h3>
                <div className="space-y-6 border-l-2 border-gray-200 dark:border-gray-800 ml-3 pl-5 relative">
                  {[1, 2].map(i => (
                    <div key={i} className="relative">
                      <div className="absolute -left-[27px] top-1 w-3 h-3 rounded-full bg-primary ring-4 ring-white dark:ring-navy-900"></div>
                      <h4 className="font-semibold text-gray-900 dark:text-white">Senior Frontend Developer</h4>
                      <p className="text-sm text-primary mb-2">TechCorp Inc. • 2020 - Present</p>
                      <p className="text-sm text-gray-600 dark:text-gray-400">Led the development of core web applications using React and TypeScript. Improved performance by 40%.</p>
                    </div>
                  ))}
                </div>
              </div>
            </>
          )}
          {activeTab === 'resume' && (
            <div className="glass-card p-6 min-h-[600px] flex items-center justify-center border-2 border-dashed border-gray-300 dark:border-gray-700">
              <div className="text-center">
                <Download className="w-10 h-10 text-gray-400 mx-auto mb-3" />
                <p className="text-gray-500">PDF Viewer Component Here</p>
              </div>
            </div>
          )}
        </div>

        <div className="space-y-6">
          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Match Score</h3>
            <div className="flex justify-center my-6">
              <div className="w-32 h-32 rounded-full border-8 border-primary/20 flex items-center justify-center relative">
                <div className="absolute w-full h-full rounded-full border-8 border-primary border-t-transparent -rotate-45"></div>
                <span className="text-3xl font-bold dark:text-white">92<span className="text-lg text-gray-500">%</span></span>
              </div>
            </div>
            
            <div className="space-y-3 mt-6">
              <div className="flex justify-between text-sm">
                <span className="text-gray-500">Skills Match</span>
                <span className="font-medium dark:text-white">95%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5"><div className="bg-green-500 h-1.5 rounded-full w-[95%]"></div></div>
              
              <div className="flex justify-between text-sm mt-4">
                <span className="text-gray-500">Experience</span>
                <span className="font-medium dark:text-white">88%</span>
              </div>
              <div className="w-full bg-gray-200 dark:bg-gray-700 rounded-full h-1.5"><div className="bg-primary h-1.5 rounded-full w-[88%]"></div></div>
            </div>
          </div>

          <div className="glass-card p-6">
            <h3 className="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">Top Skills</h3>
            <div className="flex flex-wrap gap-2">
              {['React', 'TypeScript', 'Node.js', 'GraphQL', 'Tailwind CSS'].map(skill => (
                <span key={skill} className="px-3 py-1 bg-gray-100 dark:bg-navy-800 text-xs font-medium text-gray-700 dark:text-gray-300 rounded-lg border border-gray-200 dark:border-gray-700">
                  {skill}
                </span>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
""",
    "components/candidates/AISummary.tsx": """import React from 'react';
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
""",
    "pages/Jobs.tsx": """import React from 'react';
import { Plus, Users, MapPin, Briefcase } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Jobs() {
  return (
    <div className="animate-fade-in pb-10">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold dark:text-white">Active Jobs</h1>
        <button className="bg-primary text-white px-4 py-2 rounded-lg text-sm font-medium hover:bg-primary/90 transition shadow-lg shadow-primary/25 flex items-center">
          <Plus className="w-4 h-4 mr-2" /> Create Job
        </button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {[1, 2, 3, 4].map(i => (
          <div key={i} className="glass-card p-6 group hover:border-primary/50 transition-colors">
            <div className="flex justify-between items-start mb-4">
              <div>
                <span className="text-xs font-medium px-2 py-1 bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300 rounded-full">Active</span>
                <h3 className="text-lg font-bold dark:text-white mt-3">Frontend Engineer</h3>
                <p className="text-sm text-gray-500 mt-1">Engineering Dept</p>
              </div>
            </div>
            
            <div className="space-y-2 mb-6">
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <MapPin className="w-4 h-4 mr-2" /> Remote (US)
              </div>
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <Briefcase className="w-4 h-4 mr-2" /> Full-time
              </div>
              <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
                <Users className="w-4 h-4 mr-2" /> 42 Candidates
              </div>
            </div>
            
            <Link to={`/jobs/${i}`} className="block w-full text-center py-2 bg-gray-100 dark:bg-navy-800 hover:bg-gray-200 dark:hover:bg-navy-700 text-sm font-medium rounded-lg transition-colors text-gray-700 dark:text-gray-300">
              View Pipeline
            </Link>
          </div>
        ))}
      </div>
    </div>
  );
}
""",
    "pages/JobDetail.tsx": """import React from 'react';
import { useParams, Link } from 'react-router-dom';

export default function JobDetail() {
  const { id } = useParams();
  
  return (
    <div className="animate-fade-in">
      <div className="mb-6 flex items-center justify-between">
        <div>
          <Link to="/jobs" className="text-sm text-primary hover:underline mb-2 inline-block">← Back to Jobs</Link>
          <h1 className="text-2xl font-bold dark:text-white">Frontend Engineer</h1>
          <p className="text-gray-500">Pipeline for Job ID: {id}</p>
        </div>
      </div>
      <div className="glass-card p-6 flex items-center justify-center h-96">
        <p className="text-gray-500">Job specific pipeline board goes here (similar to main Pipeline)</p>
      </div>
    </div>
  );
}
""",
    "pages/Candidates.tsx": """import React from 'react';
import { Link } from 'react-router-dom';
import { Search, Filter } from 'lucide-react';

export default function Candidates() {
  return (
    <div className="animate-fade-in h-full flex flex-col">
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold dark:text-white">All Candidates</h1>
      </div>
      
      <div className="glass-card p-4 mb-6 flex gap-4">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input type="text" placeholder="Search by name, email, or skills..." className="w-full pl-10 pr-4 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm" />
        </div>
        <button className="flex items-center px-4 py-2 bg-gray-50 dark:bg-navy-900 border border-gray-200 dark:border-gray-700 rounded-lg text-sm font-medium dark:text-gray-200">
          <Filter className="w-4 h-4 mr-2" /> Filters
        </button>
      </div>

      <div className="glass-card flex-1 overflow-hidden flex flex-col">
        <div className="overflow-x-auto">
          <table className="w-full text-sm text-left">
            <thead className="text-xs text-gray-500 uppercase bg-gray-50/50 dark:bg-navy-900/50 border-b border-gray-200 dark:border-gray-800">
              <tr>
                <th className="px-6 py-4 font-medium">Candidate Name</th>
                <th className="px-6 py-4 font-medium">Applied Job</th>
                <th className="px-6 py-4 font-medium">Stage</th>
                <th className="px-6 py-4 font-medium">Match Score</th>
                <th className="px-6 py-4 font-medium">Date</th>
                <th className="px-6 py-4 text-right">Action</th>
              </tr>
            </thead>
            <tbody>
              {[1, 2, 3, 4, 5].map(i => (
                <tr key={i} className="border-b border-gray-100 dark:border-gray-800 hover:bg-gray-50/50 dark:hover:bg-navy-800/50 transition-colors">
                  <td className="px-6 py-4">
                    <div className="flex items-center">
                      <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center text-primary font-bold mr-3">
                        AS
                      </div>
                      <div>
                        <div className="font-medium dark:text-white">Alice Smith {i}</div>
                        <div className="text-xs text-gray-500">alice.smith@example.com</div>
                      </div>
                    </div>
                  </td>
                  <td className="px-6 py-4 dark:text-gray-300">Frontend Engineer</td>
                  <td className="px-6 py-4">
                    <span className="px-2.5 py-1 text-xs rounded-full bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300 font-medium">Applied</span>
                  </td>
                  <td className="px-6 py-4">
                    <span className="text-green-500 font-medium">92%</span>
                  </td>
                  <td className="px-6 py-4 text-gray-500 dark:text-gray-400">Oct 01, 2023</td>
                  <td className="px-6 py-4 text-right">
                    <Link to={`/candidates/c${i}`} className="text-primary hover:underline font-medium">View Profile</Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
""",
    "pages/Settings.tsx": """import React from 'react';

export default function Settings() {
  return (
    <div className="animate-fade-in max-w-2xl mx-auto">
      <h1 className="text-2xl font-bold dark:text-white mb-6">Settings</h1>
      <div className="glass-card p-6 space-y-6">
        <div>
          <h3 className="text-lg font-semibold dark:text-white mb-4">Profile Information</h3>
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Full Name</label>
              <input type="text" className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-navy-900 text-gray-900 dark:text-white" defaultValue="Recruiter Name" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">Email</label>
              <input type="email" className="w-full px-4 py-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-navy-900 text-gray-900 dark:text-white" defaultValue="recruiter@company.com" disabled />
            </div>
          </div>
        </div>
        <hr className="border-gray-200 dark:border-gray-700" />
        <div>
          <h3 className="text-lg font-semibold dark:text-white mb-4">Preferences</h3>
          <div className="flex items-center justify-between">
            <span className="text-sm dark:text-gray-300">Email Notifications</span>
            <input type="checkbox" className="toggle" defaultChecked />
          </div>
        </div>
        <div className="pt-4 flex justify-end">
          <button className="px-6 py-2 bg-primary text-white rounded-lg font-medium shadow-lg shadow-primary/25 hover:bg-primary/90 transition-colors">
            Save Changes
          </button>
        </div>
      </div>
    </div>
  );
}
"""
}

for file_path, content in files.items():
    full_path = os.path.join(base_dir, file_path)
    os.makedirs(os.path.dirname(full_path), exist_ok=True)
    with open(full_path, "w", encoding="utf-8") as f:
        f.write(content)

print("Scaffolding complete!")
