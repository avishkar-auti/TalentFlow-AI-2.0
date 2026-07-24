import React, { useEffect, useState, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Code, Play, Send, CheckCircle2, Lock, Clock, Terminal, RotateCcw, Sparkles, HelpCircle, Users } from 'lucide-react';
import { Card, CardContent } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import axios from 'axios';

const STARTER_CODES: Record<string, string> = {
  python: `def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
print("Result:", two_sum([2, 7, 11, 15], 9))
`,
  javascript: `function twoSum(nums, target) {
    const map = new Map();
    for (let i = 0; i < nums.length; i++) {
        const diff = target - nums[i];
        if (map.has(diff)) return [map.get(diff), i];
        map.set(nums[i], i);
    }
    return [];
}
console.log("Result:", twoSum([2, 7, 11, 15], 9));
`,
  typescript: `function twoSum(nums: number[], target: number): number[] {
    const map = new Map<number, number>();
    for (let i = 0; i < nums.length; i++) {
        const diff = target - nums[i];
        if (map.has(diff)) return [map.get(diff)!, i];
        map.set(nums[i], i);
    }
    return [];
}
console.log("Result:", twoSum([2, 7, 11, 15], 9));
`,
  cpp: `#include <iostream>
#include <unordered_map>
#include <vector>
using namespace std;
vector<int> twoSum(vector<int>& nums, int target) {
    unordered_map<int, int> seen;
    for (int i = 0; i < nums.size(); i++) {
        int diff = target - nums[i];
        if (seen.find(diff) != seen.end())
            return {seen[diff], i};
        seen[nums[i]] = i;
    }
    return {};
}
int main() {
    vector<int> nums = {2, 7, 11, 15};
    auto res = twoSum(nums, 9);
    cout << "Result: [" << res[0] << ", " << res[1] << "]" << endl;
}
`,
  java: `import java.util.*;
class Solution {
    public int[] twoSum(int[] nums, int target) {
        Map<Integer, Integer> seen = new HashMap<>();
        for (int i = 0; i < nums.length; i++) {
            int diff = target - nums[i];
            if (seen.containsKey(diff))
                return new int[]{seen.get(diff), i};
            seen.put(nums[i], i);
        }
        return new int[]{};
    }
    public static void main(String[] args) {
        int[] nums = {2, 7, 11, 15};
        int[] res = new Solution().twoSum(nums, 9);
        System.out.println("Result: [" + res[0] + ", " + res[1] + "]");
    }
}
`,
  c: `#include <stdio.h>
#include <string.h>
int* twoSum(int* nums, int numsSize, int target, int* returnSize) {
    int* result = (int*)malloc(2 * sizeof(int));
    for (int i = 0; i < numsSize; i++) {
        for (int j = i + 1; j < numsSize; j++) {
            if (nums[i] + nums[j] == target) {
                result[0] = i;
                result[1] = j;
                *returnSize = 2;
                return result;
            }
        }
    }
    *returnSize = 0;
    return result;
}
int main() {
    int nums[] = {2, 7, 11, 15};
    int returnSize;
    int* res = twoSum(nums, 4, 9, &returnSize);
    printf("Result: [%d, %d]\\n", res[0], res[1]);
}
`
};

export function TechnicalSandbox() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  
  const [candidateStage, setCandidateStage] = useState<string>('applied');
  const [loadingStage, setLoadingStage] = useState<boolean>(true);
  const [language, setLanguage] = useState<string>('python');
  const [code, setCode] = useState<string>(STARTER_CODES.python);
  const [stdin, setStdin] = useState<string>('');
  const [isRunning, setIsRunning] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isGettingHint, setIsGettingHint] = useState(false);
  const [aiHint, setAiHint] = useState<{ hint: string; structure: string; timeComp: string; spaceComp: string } | null>(null);

  const [output, setOutput] = useState<{
    stdout: string;
    stderr: string;
    status: string;
    exec_time: number;
    exit_code: number;
  } | null>(null);

  const [submitted, setSubmitted] = useState(false);
  const [chatMessages, setChatMessages] = useState<Array<{sender: string, content: string, timestamp: string}>>([]);
  const [chatInput, setChatInput] = useState('');
  const [chatConnected, setChatConnected] = useState(false);
  const wsRef = useRef<WebSocket | null>(null);
  const chatScrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (chatScrollRef.current) {
      chatScrollRef.current.scrollTop = chatScrollRef.current.scrollHeight;
    }
  }, [chatMessages]);

  useEffect(() => {
    if (!id) return;
    const wsUrl = `ws://localhost:8000/ws/recruiter-chat/${id}?role=candidate`;
    try {
      wsRef.current = new WebSocket(wsUrl);
      wsRef.current.onopen = () => setChatConnected(true);
      wsRef.current.onmessage = (e) => {
        const msg = JSON.parse(e.data);
        if (msg.type === 'chat_message') {
          setChatMessages(prev => [...prev, {
            sender: msg.sender_role === 'recruiter' ? 'Recruiter' : 'You',
            content: msg.content,
            timestamp: msg.timestamp
          }]);
        }
      };
      wsRef.current.onerror = () => setChatConnected(false);
      wsRef.current.onclose = () => setChatConnected(false);
      return () => wsRef.current?.close();
    } catch (e) {
      console.warn('Chat WebSocket error:', e);
    }
  }, [id]);

  const sendChatMessage = (e: React.FormEvent) => {
    e.preventDefault();
    if (!chatInput.trim() || !wsRef.current) return;
    wsRef.current.send(JSON.stringify({ content: chatInput }));
    setChatInput('');
  };

  useEffect(() => {
    async function checkCandidateStage() {
      const candidateId = localStorage.getItem('talentflow_candidate_id');
      if (!candidateId) {
        setLoadingStage(false);
        return;
      }
      try {
        const res = await axios.get(`http://localhost:8000/api/v1/candidates/${candidateId}`);
        const cand = res.data?.data || res.data;
        const stage = cand?.pipeline_stage || cand?.stage || 'applied';
        setCandidateStage(stage.toLowerCase());
      } catch (err) {
        console.warn('Failed to fetch candidate stage:', err);
      } finally {
        setLoadingStage(false);
      }
    }
    checkCandidateStage();
  }, []);

  const ALLOWED_STAGES = ['shortlisted', 'technical', 'interview_completed', 'offer', 'hired', 'demo'];
  const isUnlocked = ALLOWED_STAGES.includes(candidateStage) || localStorage.getItem('talentflow_candidate_id') === null;

  const handleLanguageChange = (newLang: string) => {
    setLanguage(newLang);
    setCode(STARTER_CODES[newLang] || STARTER_CODES.python);
  };

  const handleRunCode = async () => {
    setIsRunning(true);
    setOutput(null);
    const candidateId = localStorage.getItem('talentflow_candidate_id') || 'cand_demo';

    try {
      const res = await axios.post('http://localhost:8000/api/v1/internal/execute-code', {
        language,
        code,
        stdin_input: stdin,
        candidate_id: candidateId,
        interview_id: id || 'demo_int_1',
        test_cases: [
          { input: "[2, 7, 11, 15], 9", expected: "[0, 1]" }
        ]
      });

      const data = res.data?.data || res.data;
      setOutput({
        stdout: data.stdout || '',
        stderr: data.stderr || '',
        status: data.status || 'success',
        exec_time: data.execution_time_ms || 0,
        exit_code: data.exit_code ?? 0,
      });
    } catch (err: any) {
      setOutput({
        stdout: '',
        stderr: err.response?.data?.detail || err.message || 'Execution failed',
        status: 'error',
        exec_time: 0,
        exit_code: 1,
      });
    } finally {
      setIsRunning(false);
    }
  };

  const handleFetchAiHint = async () => {
    setIsGettingHint(true);
    try {
      const res = await axios.post('http://localhost:8000/api/v1/internal/execute-code/hint', {
        language,
        problem_title: "Two Sum Target",
        current_code: code
      });
      const data = res.data?.data || res.data;
      setAiHint({
        hint: data.hint || '',
        structure: data.suggested_structure || '',
        timeComp: data.time_complexity || 'O(N)',
        spaceComp: data.space_complexity || 'O(N)'
      });
    } catch (err) {
      console.warn('AI Hint error:', err);
    } finally {
      setIsGettingHint(false);
    }
  };

  const handleSubmit = async () => {
    setIsSubmitting(true);
    await handleRunCode();

    // Submit code for AI scoring
    const interviewId = id || 'demo_int_1';
    try {
      await axios.post('http://localhost:8000/api/v1/interviews/code-submission', {
        interview_id: interviewId,
        language,
        code,
        expected_output: '[0, 1]'
      });
    } catch (e) {
      console.warn('Code submission error:', e);
    }

    setSubmitted(true);
    setIsSubmitting(false);
    setTimeout(() => {
      navigate('/status');
    }, 2500);
  };

  if (loadingStage) {
    return (
      <div className="max-w-4xl mx-auto p-12 text-center text-sm text-gray-500 bg-white dark:bg-gray-900 rounded-3xl mt-10">
        Checking shortlisting access status...
      </div>
    );
  }

  // Render Locked State UI if candidate is not shortlisted
  if (!isUnlocked) {
    return (
      <div className="max-w-3xl mx-auto mt-12 p-8 bg-white dark:bg-gray-900 rounded-3xl border border-amber-200 dark:border-amber-950 shadow-xl text-center space-y-6 animate-fade-in">
        <div className="bg-amber-100 dark:bg-amber-900/30 p-4 rounded-full w-16 h-16 mx-auto flex items-center justify-center">
          <Lock className="w-8 h-8 text-amber-600 dark:text-amber-400" />
        </div>

        <div>
          <span className="px-3 py-1 text-xs font-bold uppercase tracking-wider bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-300 rounded-full inline-block mb-2">
            🔒 Coding Test Round Locked
          </span>
          <h2 className="text-2xl font-extrabold text-gray-900 dark:text-white">
            Shortlist Access Required
          </h2>
          <p className="text-xs text-gray-600 dark:text-gray-400 max-w-md mx-auto mt-2 leading-relaxed">
            Your candidate profile is currently under review by our recruitment team. Once HR shortlists your application, this Technical Coding Sandbox window will automatically unlock.
          </p>
        </div>

        <div className="pt-2 flex justify-center gap-4">
          <Button onClick={() => navigate('/status')} className="text-xs font-semibold px-6 py-2.5 rounded-xl">
            View Application Status
          </Button>
          <Button onClick={() => navigate('/jobs')} variant="outline" className="text-xs font-semibold px-6 py-2.5 rounded-xl">
            Browse Other Jobs
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-fade-in pb-16">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <span className="px-3 py-1 text-xs font-bold uppercase tracking-wider bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300 rounded-full inline-block mb-2">
            💻 Technical Interview Round (UNLOCKED 🔓)
          </span>
          <h1 className="text-2xl font-extrabold text-gray-900 dark:text-white flex items-center gap-2">
            <Code className="w-6 h-6 text-violet-500" /> Interactive Technical Coding & AI Code Sandbox
          </h1>
          <p className="text-xs text-gray-500 dark:text-gray-400">
            Write, execute, and evaluate your technical code against automated test cases in real-time.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <select
            value={language}
            onChange={(e) => handleLanguageChange(e.target.value)}
            className="py-2 px-3 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl text-xs font-semibold dark:text-white outline-none"
          >
            <option value="python">Python 3</option>
            <option value="javascript">JavaScript</option>
            <option value="typescript">TypeScript</option>
            <option value="cpp">C++</option>
            <option value="java">Java</option>
            <option value="c">C</option>
          </select>

          <Button
            onClick={handleFetchAiHint}
            isLoading={isGettingHint}
            variant="outline"
            size="sm"
            className="border-violet-300 text-violet-600 dark:text-violet-300 font-semibold flex items-center gap-1.5"
          >
            <Sparkles className="w-3.5 h-3.5 text-violet-500" /> AI Code Hint
          </Button>

          <Button
            onClick={handleRunCode}
            isLoading={isRunning}
            size="sm"
            className="bg-emerald-600 hover:bg-emerald-700 text-white font-semibold flex items-center gap-1.5"
          >
            <Play className="w-3.5 h-3.5 fill-white" /> Run Code
          </Button>

          <Button
            onClick={handleSubmit}
            isLoading={isSubmitting}
            size="sm"
            className="bg-violet-600 hover:bg-violet-700 text-white font-semibold flex items-center gap-1.5"
          >
            <Send className="w-3.5 h-3.5" /> Submit Solution
          </Button>
        </div>
      </div>

      {submitted && (
        <div className="bg-emerald-500/10 border border-emerald-500/30 p-4 rounded-2xl flex items-center justify-between text-emerald-600 dark:text-emerald-400">
          <div className="flex items-center gap-2 text-sm font-bold">
            <CheckCircle2 className="w-5 h-5" /> Technical Solution Submitted & Recorded to Firestore!
          </div>
          <span className="text-xs text-gray-400">Redirecting to status page...</span>
        </div>
      )}

      {aiHint && (
        <div className="bg-violet-500/10 border border-violet-500/30 p-4 rounded-2xl space-y-2 animate-fade-in">
          <div className="flex items-center gap-2 text-xs font-bold text-violet-700 dark:text-violet-300">
            <Sparkles className="w-4 h-4" /> AI Co-Pilot Code Structure Hint:
          </div>
          <p className="text-xs text-gray-700 dark:text-gray-300 font-medium">{aiHint.hint}</p>
          <div className="flex gap-4 text-[11px] font-mono text-gray-500 pt-1">
            <span>Target Time Complexity: <strong className="text-violet-600 dark:text-violet-400">{aiHint.timeComp}</strong></span>
            <span>Target Space Complexity: <strong className="text-violet-600 dark:text-violet-400">{aiHint.spaceComp}</strong></span>
          </div>
        </div>
      )}

      {/* Editor & Console Grid */}
      <div className="grid lg:grid-cols-6 gap-4">
        {/* Left: Code Editor (3 cols) */}
        <div className="lg:col-span-3 space-y-4">
          <Card className="border-gray-200 dark:border-gray-800 overflow-hidden shadow-lg">
            <div className="bg-gray-900 px-4 py-2.5 flex items-center justify-between border-b border-gray-800">
              <span className="text-xs font-mono font-bold text-gray-300 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-violet-400" /> main.{language === 'python' ? 'py' : 'js'}
              </span>
              <button
                onClick={() => setCode(STARTER_CODES[language] || '')}
                className="text-gray-400 hover:text-white text-xs flex items-center gap-1 transition"
              >
                <RotateCcw className="w-3 h-3" /> Reset Code
              </button>
            </div>

            <textarea
              value={code}
              onChange={(e) => setCode(e.target.value)}
              rows={18}
              className="w-full bg-gray-950 text-gray-100 font-mono text-xs p-4 outline-none resize-none leading-relaxed"
              spellCheck={false}
            />
          </Card>
        </div>

        {/* Middle: Problem Description & Console Output (2 cols) */}
        <div className="lg:col-span-2 space-y-4">
          {/* Problem Card */}
          <Card className="p-5 border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900">
            <h3 className="text-sm font-bold text-gray-900 dark:text-white mb-2">
              Problem Statement: Two Sum Target
            </h3>
            <p className="text-xs text-gray-600 dark:text-gray-300 leading-relaxed mb-3">
              Given an array of integers <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-violet-500">nums</code> and an integer <code className="bg-gray-100 dark:bg-gray-800 px-1 py-0.5 rounded text-violet-500">target</code>, return indices of the two numbers such that they add up to target.
            </p>
            <div className="bg-gray-50 dark:bg-gray-800/50 p-3 rounded-xl text-[11px] font-mono space-y-1">
              <div><strong className="text-gray-500">Input:</strong> nums = [2,7,11,15], target = 9</div>
              <div><strong className="text-gray-500">Output:</strong> [0, 1]</div>
            </div>
          </Card>

          {/* Terminal Console Output */}
          <Card className="border-gray-200 dark:border-gray-800 overflow-hidden bg-gray-950 shadow-lg">
            <div className="bg-gray-900 px-4 py-2.5 flex items-center justify-between border-b border-gray-800">
              <span className="text-xs font-mono font-bold text-gray-300 flex items-center gap-2">
                <Terminal className="w-4 h-4 text-emerald-400" /> Output Terminal Console
              </span>
              {output && (
                <span className="text-[10px] font-mono text-gray-400 flex items-center gap-1">
                  <Clock className="w-3 h-3 text-gray-400" /> {output.exec_time} ms
                </span>
              )}
            </div>

            <div className="p-4 min-h-[160px] max-h-[220px] overflow-y-auto font-mono text-xs">
              {!output && !isRunning && (
                <p className="text-gray-600 italic">Click 'Run Code' to execute your solution in the backend sandbox.</p>
              )}
              {isRunning && (
                <p className="text-violet-400 animate-pulse">Running code in backend sandbox...</p>
              )}
              {output && (
                <div className="space-y-2">
                  {output.stdout && (
                    <div>
                      <span className="text-emerald-400 font-bold block mb-1">STDOUT:</span>
                      <pre className="text-gray-200 bg-black/40 p-2 rounded whitespace-pre-wrap">{output.stdout}</pre>
                    </div>
                  )}
                  {output.stderr && (
                    <div>
                      <span className="text-red-400 font-bold block mb-1">STDERR:</span>
                      <pre className="text-red-300 bg-red-950/30 p-2 rounded whitespace-pre-wrap">{output.stderr}</pre>
                    </div>
                  )}
                  <div className="pt-2 flex items-center gap-2 text-[11px]">
                    <span className={`px-2 py-0.5 rounded font-bold ${
                      output.exit_code === 0 ? 'bg-emerald-500/20 text-emerald-400' : 'bg-red-500/20 text-red-400'
                    }`}>
                      Exit Code: {output.exit_code}
                    </span>
                  </div>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Right: Recruiter 1-on-1 Chat (1 col) */}
        <div className="lg:col-span-1">
          <Card className="h-[580px] flex flex-col border-gray-200 dark:border-gray-800 bg-white dark:bg-gray-900 shadow-lg">
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-4 py-3 border-b border-blue-700/30 flex items-center gap-2">
              <Users className="w-4 h-4 text-white" />
              <span className="text-xs font-bold text-white">Recruiter Chat</span>
              <div className={`ml-auto w-2 h-2 rounded-full ${chatConnected ? 'bg-emerald-400 animate-pulse' : 'bg-gray-400'}`} />
            </div>

            <div className="flex-1 overflow-y-auto p-3 space-y-3" ref={chatScrollRef}>
              {chatMessages.length === 0 && (
                <div className="text-center text-gray-500 dark:text-gray-400 text-xs mt-8">
                  Recruiter will join soon...
                </div>
              )}
              {chatMessages.map((msg, idx) => (
                <div key={idx} className={`flex ${msg.sender === 'You' ? 'justify-end' : 'justify-start'}`}>
                  <div className={`max-w-[85%] rounded-lg px-3 py-2 text-xs ${
                    msg.sender === 'You'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-800 text-gray-800 dark:text-gray-200'
                  }`}>
                    <p className="font-semibold text-[10px] opacity-75 mb-1">{msg.sender}</p>
                    <p className="break-words">{msg.content}</p>
                  </div>
                </div>
              ))}
            </div>

            <form onSubmit={sendChatMessage} className="border-t border-gray-200 dark:border-gray-700 p-3 flex gap-2">
              <input
                type="text"
                value={chatInput}
                onChange={(e) => setChatInput(e.target.value)}
                placeholder="Type message..."
                disabled={!chatConnected}
                className="flex-1 px-3 py-2 bg-gray-50 dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-xs outline-none disabled:opacity-50"
              />
              <button
                type="submit"
                disabled={!chatConnected || !chatInput.trim()}
                className="px-2 py-2 bg-blue-600 text-white rounded-lg disabled:opacity-50 hover:bg-blue-700 transition"
              >
                <Send className="w-3.5 h-3.5" />
              </button>
            </form>
          </Card>
        </div>
      </div>
    </div>
  );
}
