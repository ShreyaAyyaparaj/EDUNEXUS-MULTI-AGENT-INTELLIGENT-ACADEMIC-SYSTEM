import React, { useState, useEffect } from 'react';
import { useAuth } from '../context/AuthContext';
import { loginApi } from '../services/api';
import {
  GraduationCap, Shield, UserCheck, Eye, EyeOff, CheckCircle2,
  User, ArrowRight, HelpCircle, Sparkles
} from 'lucide-react';

export const LoginPage = () => {
  const { login } = useAuth();
  const [selectedRole, setSelectedRole] = useState('student');
  const [identifier, setIdentifier] = useState('2023CSE042');
  const [password, setPassword] = useState('EduNexus@2026');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState(null);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Clear session_expired URL query parameter cleanly on load
    if (window.location.search.includes('session_expired')) {
      window.history.replaceState({}, document.title, window.location.pathname);
    }
  }, []);

  const handleRoleTabChange = (role) => {
    setSelectedRole(role);
    setError(null);
    if (role === 'student') {
      setIdentifier('2023CSE042');
      setPassword('EduNexus@2026');
    } else if (role === 'faculty') {
      setIdentifier('faculty@educamp.edu');
      setPassword('EduNexus@2026');
    } else if (role === 'admin') {
      setIdentifier('admin@educamp.edu');
      setPassword('EduNexus@2026');
    }
  };

  const handleDirectDemoLogin = async (role) => {
    setLoading(true);
    setError(null);
    let demoIdentifier = '2023CSE042';
    if (role === 'faculty') demoIdentifier = 'faculty@educamp.edu';
    if (role === 'admin') demoIdentifier = 'admin@educamp.edu';

    try {
      const res = await loginApi(demoIdentifier, 'EduNexus@2026', role);
      login(res);
    } catch (err) {
      setError(err.message || 'Login failed.');
    } finally {
      setLoading(false);
    }
  };

  const handleSubmit = async (e) => {
    e?.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const res = await loginApi(identifier, password, selectedRole);
      login(res);
    } catch (err) {
      setError(err.message || 'Authentication failed. Please verify credentials.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div
      className="min-h-screen w-full relative flex flex-col justify-between p-6 md:p-12 bg-cover bg-center bg-no-repeat text-slate-100 font-sans"
      style={{ backgroundImage: "linear-gradient(to right, rgba(15, 23, 42, 0.85), rgba(15, 23, 42, 0.4)), url('/campus_bg.png')" }}
    >
      {/* Top Left Branding Badge matching attached campus image */}
      <div className="z-10 flex items-center gap-3">
        <div className="w-12 h-12 rounded-2xl bg-gradient-to-tr from-purple-600 via-indigo-600 to-purple-700 flex items-center justify-center shadow-2xl border border-purple-400/30">
          <GraduationCap className="w-7 h-7 text-white" />
        </div>
        <div>
          <h1 className="text-xl md:text-2xl font-black tracking-tight text-white uppercase drop-shadow-md">
            EDUNEXUS ACADEMIC COLLEGE
          </h1>
          <p className="text-xs text-purple-200 font-medium">Autonomous Institution • ERP Decision Support System</p>
        </div>
      </div>

      {/* Main Content Grid: Login Panel on Left Side as requested */}
      <div className="z-10 my-auto py-8 flex flex-col lg:flex-row items-start justify-between gap-12">
        {/* Left Side Translucent Campus Sign In Card */}
        <div className="w-full max-w-md bg-slate-900/90 border border-slate-700/60 backdrop-blur-xl rounded-3xl p-7 md:p-8 shadow-2xl space-y-5">
          <div className="flex items-center justify-between">
            <h2 className="text-2xl font-bold text-white tracking-tight">Sign in here</h2>
            <span className="text-[10px] font-bold bg-purple-500/20 text-purple-300 border border-purple-500/30 px-2.5 py-1 rounded-full uppercase">
              {selectedRole} Portal
            </span>
          </div>

          {/* Role Selection Switcher */}
          <div className="grid grid-cols-3 gap-1.5 p-1 bg-slate-950/80 rounded-2xl border border-slate-800">
            <button
              type="button"
              onClick={() => handleRoleTabChange('student')}
              className={`py-2 px-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                selectedRole === 'student' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <GraduationCap className="w-3.5 h-3.5" /> Student
            </button>

            <button
              type="button"
              onClick={() => handleRoleTabChange('faculty')}
              className={`py-2 px-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                selectedRole === 'faculty' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <UserCheck className="w-3.5 h-3.5" /> Faculty
            </button>

            <button
              type="button"
              onClick={() => handleRoleTabChange('admin')}
              className={`py-2 px-2 rounded-xl text-xs font-bold flex items-center justify-center gap-1 transition-all cursor-pointer ${
                selectedRole === 'admin' ? 'bg-purple-600 text-white shadow-lg' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              <Shield className="w-3.5 h-3.5" /> Admin
            </button>
          </div>

          {error && (
            <div className="p-3 rounded-xl bg-red-950/60 border border-red-800 text-red-300 text-xs font-medium">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Registration id / email / phone no.
              </label>
              <div className="relative">
                <input
                  type="text"
                  value={identifier}
                  onChange={e => setIdentifier(e.target.value)}
                  placeholder="e.g. 2023CSE042 or student@educamp.edu"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-purple-500 text-white text-xs rounded-xl pl-3.5 pr-10 py-3 outline-none transition-all placeholder:text-slate-500"
                />
                <User className="w-4 h-4 text-slate-400 absolute right-3 top-3.5" />
              </div>
            </div>

            <div>
              <label className="block text-xs font-semibold text-slate-300 mb-1">
                Password
              </label>
              <div className="relative">
                <input
                  type={showPassword ? "text" : "password"}
                  value={password}
                  onChange={e => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  required
                  className="w-full bg-slate-950/80 border border-slate-700 focus:border-purple-500 text-white text-xs rounded-xl pl-3.5 pr-10 py-3 outline-none transition-all placeholder:text-slate-500"
                />
                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  className="absolute right-3 top-3.5 text-slate-400 hover:text-slate-200 cursor-pointer"
                >
                  {showPassword ? <EyeOff className="w-4 h-4" /> : <Eye className="w-4 h-4" />}
                </button>
              </div>
            </div>

            {/* Captcha Security Guard Badge matching image */}
            <div className="p-3 rounded-xl bg-slate-950/90 border border-slate-800 flex items-center justify-between text-xs">
              <div className="flex items-center gap-2 text-emerald-400 font-semibold">
                <CheckCircle2 className="w-5 h-5 text-emerald-400" />
                <span>Success! EduNexus AI Security Guard</span>
              </div>
              <span className="text-[10px] text-slate-400 font-mono">Verified 256-bit</span>
            </div>

            {/* Red / Gradient Sign In Action Button matching image */}
            <button
              type="submit"
              disabled={loading}
              className="w-full py-3.5 rounded-xl bg-gradient-to-r from-red-500 via-rose-600 to-purple-600 hover:from-red-600 hover:to-purple-700 text-white font-bold text-sm shadow-xl transition-all cursor-pointer disabled:opacity-50 flex items-center justify-center gap-2"
            >
              {loading ? 'Signing in...' : 'Sign In'}
              <ArrowRight className="w-4 h-4" />
            </button>
          </form>

          {/* Quick 1-Click Instant Demo Login Shortcuts */}
          <div className="pt-2 space-y-2">
            <p className="text-[11px] text-slate-400 font-medium flex items-center justify-center gap-1">
              <Sparkles className="w-3.5 h-3.5 text-amber-400" /> 1-Click Direct Demo Sign In:
            </p>
            <div className="grid grid-cols-3 gap-2 text-[11px]">
              <button
                type="button"
                onClick={() => handleDirectDemoLogin('student')}
                className="py-2 rounded-xl bg-purple-950/60 hover:bg-purple-900 border border-purple-800/60 text-purple-200 font-semibold transition-all cursor-pointer"
              >
                Student
              </button>

              <button
                type="button"
                onClick={() => handleDirectDemoLogin('faculty')}
                className="py-2 rounded-xl bg-blue-950/60 hover:bg-blue-900 border border-blue-800/60 text-blue-200 font-semibold transition-all cursor-pointer"
              >
                Faculty
              </button>

              <button
                type="button"
                onClick={() => handleDirectDemoLogin('admin')}
                className="py-2 rounded-xl bg-emerald-950/60 hover:bg-emerald-900 border border-emerald-800/60 text-emerald-200 font-semibold transition-all cursor-pointer"
              >
                Admin
              </button>
            </div>
          </div>

          <div className="pt-2 text-center text-xs text-slate-400 space-y-1">
            <p className="hover:text-purple-300 cursor-pointer">Forgot password?</p>
            <p className="hover:text-purple-300 cursor-pointer flex items-center justify-center gap-1">
              <HelpCircle className="w-3.5 h-3.5" /> Need assistance? Get Help Here
            </p>
          </div>
        </div>

        {/* Right Side Info Box for Campus Portal Context */}
        <div className="hidden lg:block max-w-md space-y-4 text-slate-100 bg-slate-900/40 p-6 rounded-3xl border border-slate-800/50 backdrop-blur-md">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-purple-500/20 text-purple-200 border border-purple-500/30 text-xs font-semibold">
            <Sparkles className="w-3.5 h-3.5 text-amber-300" /> EduNexus Academic ERP Engine
          </div>
          <h2 className="text-3xl font-black text-white leading-tight">
            Intelligent Academic Decision Support & RAG Analytics
          </h2>
          <p className="text-xs text-slate-300 leading-relaxed">
            EduNexus monitors student attendance and performance, matches research interests with faculty mentors, answers policy queries with grounded RAG search, and produces strategic executive placement forecasts.
          </p>

          <div className="pt-4 border-t border-slate-800/80 grid grid-cols-2 gap-4 text-xs">
            <div>
              <span className="font-black text-lg text-white block">100%</span>
              <span className="text-slate-400 text-[11px]">Human-in-the-Loop Decisions</span>
            </div>
            <div>
              <span className="font-black text-lg text-white block">4 Agents</span>
              <span className="text-slate-400 text-[11px]">LangGraph AI Nodes</span>
            </div>
          </div>
        </div>
      </div>

      {/* Footer */}
      <div className="z-10 pt-4 border-t border-slate-800/40 text-center text-[11px] text-slate-400">
        © 2026 EduNexus Academic Decision Support Platform. All Rights Reserved.
      </div>
    </div>
  );
};
