import React, { useState, useEffect } from 'react';
import { getAdminDashboardApi, getAdminPredictionsApi } from '../services/api';
import {
  Shield, TrendingUp, Users, Building, DollarSign,
  Sparkles, AlertCircle, ArrowUpRight, BarChart3
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

export const AdminDashboard = () => {
  const [dashboardData, setDashboardData] = useState(null);
  const [predictionData, setPredictionData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAdminData = async () => {
    setLoading(true);
    setError(null);
    try {
      const [dash, pred] = await Promise.all([
        getAdminDashboardApi(),
        getAdminPredictionsApi()
      ]);
      setDashboardData(dash);
      setPredictionData(pred);
    } catch (err) {
      setError(err.message || 'Failed to load administrative analytics.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAdminData();
  }, []);

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
        <AlertCircle className="w-12 h-12 text-amber-400 mx-auto" />
        <h3 className="text-lg font-bold">Unable to load admin control panel</h3>
        <p className="text-sm text-slate-400">{error}</p>
        <button onClick={fetchAdminData} className="px-4 py-2 bg-purple-600 rounded-xl font-semibold text-xs">
          Retry
        </button>
      </div>
    );
  }

  const metrics = dashboardData?.placement_metrics || {};

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-purple-950 via-indigo-950 to-slate-900 border border-purple-500/20 p-6 md:p-8 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-purple-300 mb-1">
            <Shield className="w-4 h-4 text-purple-400" />
            <span>Centralized Executive Administration</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">
            EduNexus Institutional Control Panel
          </h1>
          <p className="text-xs text-slate-400 mt-1">Cross-departmental analytics & predictive AI engine</p>
        </div>

        <div className="flex items-center gap-2 bg-purple-950/60 border border-purple-800/50 px-4 py-2 rounded-2xl text-xs font-semibold text-purple-200">
          <Sparkles className="w-4 h-4 text-amber-300" /> Agent 4 Prediction Engine Active
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Total Enrolled Students</span>
            <Users className="w-4 h-4 text-purple-400" />
          </div>
          <div className="text-3xl font-black text-white">{dashboardData?.total_students}</div>
          <p className="text-[11px] text-slate-400">{dashboardData?.total_departments} Academic Departments</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Placement Rate</span>
            <TrendingUp className="w-4 h-4 text-emerald-400" />
          </div>
          <div className="text-3xl font-black text-white">{metrics.placement_rate}%</div>
          <p className="text-[11px] text-emerald-400 font-medium">{metrics.placed_count} of {metrics.total_eligible} eligible placed</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Average Package</span>
            <DollarSign className="w-4 h-4 text-amber-400" />
          </div>
          <div className="text-3xl font-black text-white">{metrics.average_package_lpa} <span className="text-sm font-normal text-slate-400">LPA</span></div>
          <p className="text-[11px] text-slate-400">Highest: {metrics.highest_package_lpa} LPA</p>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/80 border border-slate-800 space-y-2">
          <div className="flex items-center justify-between text-slate-400 text-xs">
            <span>Faculty Members</span>
            <Building className="w-4 h-4 text-indigo-400" />
          </div>
          <div className="text-3xl font-black text-white">{dashboardData?.total_faculty}</div>
          <p className="text-[11px] text-slate-400">Active research mentors</p>
        </div>
      </div>

      {/* AI Prediction Dashboard Section (Agent 4 Integration) */}
      <div className="p-6 md:p-8 rounded-3xl bg-slate-900/80 border border-purple-500/30 space-y-6 shadow-2xl">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-bold text-white flex items-center gap-2">
              <Sparkles className="w-5 h-5 text-amber-300" />
              AI Prediction Dashboard — Next Cohort Placement Outlook
            </h3>
            <p className="text-xs text-slate-400">Moving-average statistical projection with Gemini strategic narrative synthesis</p>
          </div>
          <span className="text-xs bg-emerald-500/20 text-emerald-300 border border-emerald-500/30 px-3 py-1 rounded-full font-bold">
            Projected Rate: {predictionData?.projected_next_year_placement_rate}%
          </span>
        </div>

        {/* Prediction Chart */}
        <div className="h-64 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={predictionData?.historical_trends || []}>
              <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
              <XAxis dataKey="year" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" domain={[60, 100]} />
              <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '12px', fontSize: '12px' }} />
              <Line type="monotone" dataKey="placement_rate_pct" name="Placement Rate (%)" stroke="#a78bfa" strokeWidth={3} dot={{ r: 6 }} />
              <Line type="monotone" dataKey="avg_attendance_pct" name="Avg Attendance (%)" stroke="#38bdf8" strokeWidth={2} strokeDasharray="5 5" />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Gemini Executive Narrative */}
        <div className="p-4 rounded-2xl bg-purple-950/40 border border-purple-800/50 space-y-2">
          <h4 className="text-xs font-bold text-purple-200 flex items-center gap-1.5">
            <Sparkles className="w-4 h-4 text-amber-300" /> Executive Strategic Summary:
          </h4>
          <p className="text-xs text-slate-200 leading-relaxed">
            {predictionData?.ai_narrative_summary}
          </p>
        </div>

        {/* Disclaimer */}
        <p className="text-[10px] text-slate-400 italic">
          {predictionData?.caveat_disclaimer}
        </p>
      </div>

      {/* Top Recruiters & Department Breakup */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100">Top Hiring Partners</h3>
          <div className="space-y-3">
            {(dashboardData?.top_recruiters || []).map((comp, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-white">{comp.company_name}</h4>
                  <p className="text-[10px] text-slate-400">{comp.students_hired} Students Hired</p>
                </div>
                <span className="text-xs font-black text-amber-400 font-mono">
                  {comp.package_lpa} LPA
                </span>
              </div>
            ))}
          </div>
        </div>

        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100">Department Enrolment</h3>
          <div className="space-y-3">
            {(dashboardData?.department_stats || []).map((dept, idx) => (
              <div key={idx} className="p-3.5 rounded-2xl bg-slate-950/60 border border-slate-800 flex items-center justify-between">
                <div>
                  <h4 className="text-xs font-bold text-purple-300">{dept.code}</h4>
                  <p className="text-xs text-slate-300 font-medium">{dept.department_name}</p>
                </div>
                <span className="text-xs font-bold text-slate-200">
                  {dept.student_count} Students
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};
