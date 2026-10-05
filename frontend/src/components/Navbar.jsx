import React from 'react';
import { useAuth } from '../context/AuthContext';
import { useTheme } from '../context/ThemeContext';
import { Sun, Moon, LogOut, GraduationCap, Shield, UserCheck } from 'lucide-react';

export const Navbar = () => {
  const { user, logout } = useAuth();
  const { isDarkMode, toggleTheme } = useTheme();

  const getRoleBadge = (role) => {
    switch (role) {
      case 'admin':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-500/20 text-purple-300 border border-purple-500/30"><Shield className="w-3 h-3" /> Admin</span>;
      case 'faculty':
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-500/20 text-blue-300 border border-blue-500/30"><UserCheck className="w-3 h-3" /> Faculty</span>;
      default:
        return <span className="inline-flex items-center gap-1 px-2.5 py-0.5 rounded-full text-xs font-semibold bg-emerald-500/20 text-emerald-300 border border-emerald-500/30"><GraduationCap className="w-3 h-3" /> Student</span>;
    }
  };

  return (
    <nav className="sticky top-0 z-40 w-full border-b border-indigo-950/50 bg-slate-950/80 backdrop-blur-md px-6 py-3.5 flex items-center justify-between text-slate-100 shadow-lg">
      <div className="flex items-center gap-3">
        <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-purple-600 to-indigo-500 flex items-center justify-center shadow-lg shadow-purple-500/25">
          <GraduationCap className="w-6 h-6 text-white" />
        </div>
        <div>
          <span className="text-xl font-extrabold bg-gradient-to-r from-white via-purple-200 to-purple-400 bg-clip-text text-transparent">
            EduNexus
          </span>
          <span className="hidden sm:inline-block ml-2 text-xs font-medium text-purple-300/70 border border-purple-500/20 px-2 py-0.5 rounded-full bg-purple-950/30">
            Agentic ERP AI
          </span>
        </div>
      </div>

      {user && (
        <div className="flex items-center gap-4">
          <div className="hidden md:flex items-center gap-2 text-sm text-slate-300 bg-slate-900/60 px-3 py-1.5 rounded-xl border border-slate-800">
            <span className="font-semibold text-slate-100">{user.full_name}</span>
            {getRoleBadge(user.role)}
          </div>

          {/* Theme Toggle Button */}
          <button
            onClick={toggleTheme}
            className="p-2 rounded-xl bg-slate-900 border border-slate-800 hover:border-purple-500/50 text-slate-300 hover:text-purple-300 transition-all cursor-pointer"
            title="Toggle Light / Dark Mode"
          >
            {isDarkMode ? <Sun className="w-5 h-5 text-amber-400" /> : <Moon className="w-5 h-5 text-indigo-400" />}
          </button>

          {/* Logout Button */}
          <button
            onClick={logout}
            className="flex items-center gap-2 px-3 py-1.5 rounded-xl bg-red-950/30 hover:bg-red-900/50 border border-red-800/40 text-red-300 text-sm font-medium transition-all cursor-pointer"
          >
            <LogOut className="w-4 h-4" />
            <span className="hidden sm:inline">Logout</span>
          </button>
        </div>
      )}
    </nav>
  );
};
