import React, { useState, useEffect } from 'react';
import { getStudentDashboardApi, createMentorRequestApi } from '../services/api';
import {
  GraduationCap, Calendar, Award, CheckCircle2, Clock,
  AlertTriangle, BookOpen, UserPlus, Sparkles, RefreshCw
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export const StudentDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Mentor Request Modal State
  const [showMentorModal, setShowMentorModal] = useState(false);
  const [facultyId, setFacultyId] = useState(1);
  const [topic, setTopic] = useState('Deep Learning Research');
  const [message, setMessage] = useState('I am interested in working on LLM multi-agent optimization under your guidance.');
  const [mentorSubmitting, setMentorSubmitting] = useState(false);
  const [mentorSuccess, setMentorSuccess] = useState(null);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getStudentDashboardApi();
      setData(res);
    } catch (err) {
      setError(err.message || 'Failed to load dashboard data.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleSendMentorRequest = async (e) => {
    e.preventDefault();
    setMentorSubmitting(true);
    setMentorSuccess(null);
    try {
      const res = await createMentorRequestApi(facultyId, topic, message);
      setMentorSuccess(`Mentorship request submitted to ${res.faculty_name}! Status: ${res.status}`);
      setTimeout(() => setShowMentorModal(false), 2000);
    } catch (err) {
      alert(err.message || 'Failed to submit mentorship request');
    } finally {
      setMentorSubmitting(false);
    }
  };

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <div className="h-32 bg-slate-900/60 rounded-3xl animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          {[1, 2, 3, 4].map(i => <div key={i} className="h-28 bg-slate-900/60 rounded-2xl animate-pulse"></div>)}
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
        <h3 className="text-lg font-bold">Unable to load dashboard</h3>
        <p className="text-sm text-slate-400">{error}</p>
        <button
          onClick={fetchDashboard}
          className="px-4 py-2 bg-purple-600 hover:bg-purple-500 rounded-xl font-semibold text-xs transition-all"
        >
          Retry
        </button>
      </div>
    );
  }

  const marksChartData = (data?.marks_summary || []).map(m => ({
    course: m.course_code,
    Internal1: m.internal1 || 0,
    Internal2: m.internal2 || 0
  }));

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="relative rounded-3xl bg-gradient-to-r from-purple-950 via-indigo-950 to-slate-900 border border-purple-500/20 p-6 md:p-8 overflow-hidden shadow-2xl">
        <div className="relative z-10 flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2 text-xs font-semibold text-purple-300 mb-1">
              <GraduationCap className="w-4 h-4 text-purple-400" />
              <span>{data?.department_name} • Semester {data?.semester}</span>
            </div>
            <h1 className="text-2xl md:text-3xl font-extrabold text-white">
              Welcome back, {data?.student_name}!
            </h1>
            <p className="text-xs text-slate-400 mt-1">Roll Number: <span className="text-slate-200 font-mono">{data?.roll_number}</span></p>
          </div>

          <button
            onClick={() => setShowMentorModal(true)}
            className="flex items-center gap-2 px-5 py-3 rounded-2xl bg-gradient-to-r from-purple-600 to-indigo-600 hover:from-purple-500 hover:to-indigo-500 text-white text-xs font-bold shadow-lg shadow-purple-600/30 transition-all cursor-pointer"
          >
            <UserPlus className="w-4 h-4" />
            <span>Request Faculty Mentor</span>
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Cumulative GPA</span>
            <Award className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-white">{data?.cgpa}</div>
          <p className="text-[11px] text-emerald-400 font-medium">Top 10% of class cohort</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Overall Attendance</span>
            <Calendar className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-black text-white">{data?.overall_attendance}%</div>
          <div className="w-full bg-slate-800 h-2 rounded-full overflow-hidden">
            <div
              className={`h-full transition-all duration-500 ${
                data?.overall_attendance >= 75 ? 'bg-purple-500' : 'bg-red-500'
              }`}
              style={{ width: `${data?.overall_attendance}%` }}
            ></div>
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Assignment Completion</span>
            <CheckCircle2 className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-black text-white">{data?.assignment_completion_rate}%</div>
          <p className="text-[11px] text-slate-400">On-time electronic submissions</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>AI Risk Status</span>
            <Sparkles className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-xl font-bold uppercase tracking-wider text-emerald-400">
            {data?.risk_status === 'good' ? 'GOOD STANDING' : 'ATTENTION REQUIRED'}
          </div>
          <p className="text-[11px] text-slate-400 truncate">{data?.risk_summary}</p>
        </div>
      </div>

      {/* Main Analytics Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        {/* Marks Trend Chart */}
        <div className="lg:col-span-2 p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <BookOpen className="w-5 h-5 text-purple-400" />
              Course Internal Exam Performance
            </h3>
            <span className="text-xs text-slate-400 font-mono">Max: 100</span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={marksChartData}>
                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                <XAxis dataKey="course" stroke="#94a3b8" />
                <YAxis stroke="#94a3b8" domain={[0, 100]} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }}
                />
                <Bar dataKey="Internal1" fill="#7c3aed" radius={[6, 6, 0, 0]} />
                <Bar dataKey="Internal2" fill="#38bdf8" radius={[6, 6, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* SkillFolio Progress */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <Award className="w-5 h-5 text-amber-400" />
            SkillFolio Verified Achievements
          </h3>

          <div className="space-y-3">
            {(data?.skillfolios || []).map(skill => (
              <div key={skill.id} className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-start justify-between">
                <div>
                  <h4 className="text-xs font-bold text-slate-200">{skill.title}</h4>
                  <p className="text-[10px] text-slate-400 mt-0.5">{skill.issuing_body} • <span className="uppercase">{skill.category}</span></p>
                </div>
                <span className="text-[10px] font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-2 py-0.5 rounded-full">
                  {skill.status}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Course Attendance & Assignments List */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {/* Attendance Breakdown */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100">Course Attendance Breakup</h3>
          <div className="space-y-3">
            {(data?.attendances_by_course || []).map((att, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-purple-300">{att.course_code}</span>
                  <p className="text-xs text-slate-300 font-medium">{att.course_name}</p>
                  <p className="text-[10px] text-slate-400">{att.present} of {att.total} classes attended</p>
                </div>
                <div className="text-right">
                  <span className={`text-sm font-black ${att.percentage >= 75 ? 'text-emerald-400' : 'text-red-400'}`}>
                    {att.percentage}%
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Assignments Portal */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100">Pending & Graded Assignments</h3>
          <div className="space-y-3">
            {(data?.assignments || []).map(asgn => (
              <div key={asgn.id} className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <span className="text-xs font-bold text-indigo-300">{asgn.course_code}</span>
                  <p className="text-xs text-slate-300 font-medium">{asgn.title}</p>
                  <p className="text-[10px] text-slate-400">Due: {asgn.due_date}</p>
                </div>
                <div>
                  <span className={`text-xs font-semibold px-2.5 py-1 rounded-full border ${
                    asgn.status === 'graded' ? 'bg-emerald-500/20 text-emerald-300 border-emerald-500/30' :
                    asgn.status === 'submitted' ? 'bg-blue-500/20 text-blue-300 border-blue-500/30' :
                    'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  }`}>
                    {asgn.status.toUpperCase()}
                  </span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Mentor Request Modal */}
      {showMentorModal && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-purple-500/30 rounded-3xl p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Request Faculty Mentorship</h3>
            <p className="text-xs text-slate-400">Agent 2 will evaluate your request alignment with faculty research profiles.</p>

            {mentorSuccess && (
              <div className="p-3 rounded-xl bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs">
                {mentorSuccess}
              </div>
            )}

            <form onSubmit={handleSendMentorRequest} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Select Faculty Member</label>
                <select
                  value={facultyId}
                  onChange={e => setFacultyId(Number(e.target.value))}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-100 rounded-xl p-2.5 outline-none"
                >
                  <option value={1}>Dr. Aris Thorne (Associate Prof - NLP & Agentic AI)</option>
                  <option value={2}>Prof. Rajesh Sharma (HOD - Computer Vision & Edge AI)</option>
                  <option value={3}>Dr. Mei Lin Chen (Assistant Prof - VLSI & Embedded Systems)</option>
                </select>
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Research Topic</label>
                <input
                  type="text"
                  value={topic}
                  onChange={e => setTopic(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-100 rounded-xl p-2.5 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Message to Faculty</label>
                <textarea
                  rows={3}
                  value={message}
                  onChange={e => setMessage(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-100 rounded-xl p-2.5 outline-none"
                />
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowMentorModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 hover:bg-slate-700 text-xs text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={mentorSubmitting}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs text-white font-semibold"
                >
                  {mentorSubmitting ? 'Submitting...' : 'Submit Request'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
