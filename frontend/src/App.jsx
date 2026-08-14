import React from 'react';
import { AuthProvider, useAuth } from './context/AuthContext';
import { ThemeProvider } from './context/ThemeContext';
import { Navbar } from './components/Navbar';
import { ChatbotWidget } from './components/ChatbotWidget';
import { LoginPage } from './pages/LoginPage';
import { StudentDashboard } from './pages/StudentDashboard';
import { FacultyDashboard } from './pages/FacultyDashboard';
import { AdminDashboard } from './pages/AdminDashboard';

const MainContent = () => {
  const { user, isAuthenticated } = useAuth();

  if (!isAuthenticated || !user) {
    return <LoginPage />;
  }

  return (
    <div className="min-h-screen flex flex-col bg-[var(--bg-primary)] text-[var(--text-main)] transition-colors duration-300">
      <Navbar />
      <main className="flex-1 pb-20">
        {user.role === 'admin' && <AdminDashboard />}
        {user.role === 'faculty' && <FacultyDashboard />}
        {user.role === 'student' && <StudentDashboard />}
      </main>
      {/* Site-wide persistent RAG chatbot widget accessible on every page */}
      <ChatbotWidget />
    </div>
  );
};

export default function App() {
  return (
    <AuthProvider>
      <ThemeProvider>
        <MainContent />
      </ThemeProvider>
    </AuthProvider>
  );
}
