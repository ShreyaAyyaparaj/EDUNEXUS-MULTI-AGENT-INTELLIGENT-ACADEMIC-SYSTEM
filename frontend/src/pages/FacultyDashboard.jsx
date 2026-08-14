import React, { useState, useEffect } from 'react';
import {
  getFacultyDashboardApi, toggleFacultyAvailabilityApi,
  actionMentorRequestApi, sendDepartmentMessageApi
} from '../services/api';
import {
  UserCheck, AlertTriangle, CheckCircle, XCircle, Download,
  MessageSquare, Sparkles, User, RefreshCw, ToggleLeft, ToggleRight
} from 'lucide-react';

export const FacultyDashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Availability state
  const [isAvailable, setIsAvailable] = useState(true);

  // Message Modal State
  const [showMessageModal, setShowMessageModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [msgTitle, setMsgTitle] = useState('Academic Advisory & Counseling');
  const [msgBody, setMsgBody] = useState('Please meet me during office hours tomorrow to discuss your attendance and assignment progress.');
  const [sendingMsg, setSendingMsg] = useState(false);

  const fetchDashboard = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await getFacultyDashboardApi();
      setData(res);
      setIsAvailable(res.is_available_for_mentorship);
    } catch (err) {
      setError(err.message || 'Failed to load faculty dashboard.');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchDashboard();
  }, []);

  const handleToggleAvailability = async () => {
    const nextState = !isAvailable;
    setIsAvailable(nextState);
    try {
      await toggleFacultyAvailabilityApi(nextState);
    } catch (err) {
      setIsAvailable(!nextState);
      alert('Failed to update availability');
    }
  };

  const handleMentorAction = async (requestId, status) => {
    try {
      await actionMentorRequestApi(requestId, status);
      fetchDashboard();
    } catch (err) {
      alert('Failed to process mentor request');
    }
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    if (!selectedStudent) return;
    setSendingMsg(true);
    try {
      await sendDepartmentMessageApi(selectedStudent.student_id, msgTitle, msgBody);
      alert(`Message successfully delivered to student ${selectedStudent.name}!`);
      setShowMessageModal(false);
    } catch (err) {
      alert(err.message || 'Failed to send message.');
    } finally {
      setSendingMsg(false);
    }
  };

  const handleDownloadReport = (studentId, format) => {
    const token = localStorage.getItem('edunexus_token');
    const url = `/api/faculty/export-report/${studentId}?format=${format}`;
    
    // Trigger direct file download
    fetch(url, {
      headers: { 'Authorization': `Bearer ${token}` }
    })
    .then(res => res.blob())
    .then(blob => {
      const blobUrl = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = blobUrl;
      a.download = `student_report_${studentId}.${format}`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    })
    .catch(err => alert('Download failed: ' + err.message));
  };

  if (loading) {
    return (
      <div className="p-8 max-w-7xl mx-auto space-y-6">
        <div className="h-32 bg-slate-900/60 rounded-3xl animate-pulse"></div>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="h-64 bg-slate-900/60 rounded-3xl animate-pulse"></div>
          <div className="h-64 bg-slate-900/60 rounded-3xl animate-pulse"></div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="p-8 max-w-lg mx-auto text-center space-y-4">
        <AlertTriangle className="w-12 h-12 text-amber-400 mx-auto" />
        <h3 className="text-lg font-bold">Unable to load faculty portal</h3>
        <p className="text-sm text-slate-400">{error}</p>
        <button onClick={fetchDashboard} className="px-4 py-2 bg-purple-600 rounded-xl font-semibold text-xs">
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="p-6 md:p-8 max-w-7xl mx-auto space-y-8 animate-in fade-in duration-300">
      {/* Header Banner */}
      <div className="rounded-3xl bg-gradient-to-r from-purple-950 via-indigo-950 to-slate-900 border border-purple-500/20 p-6 md:p-8 shadow-2xl flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2 text-xs font-semibold text-purple-300 mb-1">
            <UserCheck className="w-4 h-4 text-purple-400" />
            <span>{data?.designation} • {data?.department_name} Department</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-extrabold text-white">
            Faculty Workspace — {data?.faculty_name}
          </h1>
          <p className="text-xs text-slate-400 mt-1">Supervising {data?.department_student_count} department students</p>
        </div>

        {/* Live Mentorship Availability Toggle */}
        <div className="flex items-center gap-3 bg-slate-900/80 px-4 py-2.5 rounded-2xl border border-slate-800">
          <span className="text-xs font-semibold text-slate-300">Mentorship Status:</span>
          <button
            onClick={handleToggleAvailability}
            className="flex items-center gap-2 text-xs font-bold transition-all cursor-pointer"
          >
            {isAvailable ? (
              <span className="flex items-center gap-1.5 text-emerald-400 bg-emerald-950/60 px-3 py-1 rounded-xl border border-emerald-800/50">
                <ToggleRight className="w-5 h-5" /> Accepting Students
              </span>
            ) : (
              <span className="flex items-center gap-1.5 text-slate-400 bg-slate-950/60 px-3 py-1 rounded-xl border border-slate-800">
                <ToggleLeft className="w-5 h-5" /> Unavailable
              </span>
            )}
          </button>
        </div>
      </div>

      {/* Main Grid: At-Risk Students & Mentor Request Inbox */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        {/* At-Risk Students Section (Agent 1 Output) */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <div className="flex items-center justify-between">
            <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
              <AlertTriangle className="w-5 h-5 text-amber-400" />
              At-Risk Flagged Students ({data?.at_risk_students?.length || 0})
            </h3>
            <span className="text-[10px] bg-purple-500/20 text-purple-300 px-2 py-0.5 rounded-full font-mono">Agent 1 Scan</span>
          </div>

          <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
            {(data?.at_risk_students || []).map(st => (
              <div key={st.student_id} className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-white">{st.name}</h4>
                    <p className="text-xs text-slate-400 font-mono">Roll: {st.roll_number} • Sem {st.semester}</p>
                  </div>
                  <span className={`text-[10px] font-extrabold px-2.5 py-0.5 rounded-full border ${
                    st.risk_level === 'High' ? 'bg-red-500/20 text-red-300 border-red-500/30' : 'bg-amber-500/20 text-amber-300 border-amber-500/30'
                  }`}>
                    {st.risk_level.toUpperCase()} RISK
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center text-xs p-2 rounded-xl bg-slate-900 border border-slate-800">
                  <div>
                    <span className="text-[10px] text-slate-400 block">Attendance</span>
                    <span className={`font-bold ${st.attendance_percentage < 75 ? 'text-red-400' : 'text-slate-200'}`}>
                      {st.attendance_percentage}%
                    </span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Marks Avg</span>
                    <span className="font-bold text-slate-200">{st.marks_average}%</span>
                  </div>
                  <div>
                    <span className="text-[10px] text-slate-400 block">Unsubmitted</span>
                    <span className="font-bold text-amber-400">{st.unsubmitted_assignments}</span>
                  </div>
                </div>

                <div className="p-2.5 rounded-xl bg-purple-950/30 border border-purple-800/40 text-xs space-y-1">
                  <p className="text-purple-200 text-[11px] font-medium flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-300" /> AI Risk Narrative:
                  </p>
                  <p className="text-slate-300 text-[11px]">{st.ai_risk_narrative}</p>
                </div>

                {/* Actions: Direct Department Message & PDF/CSV Download */}
                <div className="flex items-center gap-2 pt-1">
                  <button
                    onClick={() => { setSelectedStudent(st); setShowMessageModal(true); }}
                    className="flex-1 py-1.5 rounded-xl bg-purple-600/30 hover:bg-purple-600/50 border border-purple-500/40 text-purple-200 text-xs font-semibold flex items-center justify-center gap-1.5 transition-all"
                  >
                    <MessageSquare className="w-3.5 h-3.5" /> Message Student
                  </button>

                  <button
                    onClick={() => handleDownloadReport(st.student_id, 'pdf')}
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1 transition-all"
                    title="Export Student Performance PDF"
                  >
                    <Download className="w-3.5 h-3.5 text-purple-400" /> PDF
                  </button>

                  <button
                    onClick={() => handleDownloadReport(st.student_id, 'csv')}
                    className="px-3 py-1.5 rounded-xl bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold flex items-center gap-1 transition-all"
                    title="Export Student Performance CSV"
                  >
                    <Download className="w-3.5 h-3.5 text-emerald-400" /> CSV
                  </button>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Mentor Requests Inbox */}
        <div className="p-6 rounded-3xl bg-slate-900/80 border border-slate-800 space-y-4">
          <h3 className="text-base font-bold text-slate-100 flex items-center gap-2">
            <UserCheck className="w-5 h-5 text-indigo-400" />
            Incoming Mentorship Requests ({data?.pending_mentor_requests?.length || 0})
          </h3>

          <div className="space-y-4 max-h-[480px] overflow-y-auto pr-1">
            {(data?.pending_mentor_requests || []).map(req => (
              <div key={req.id} className="p-4 rounded-2xl bg-slate-950/60 border border-slate-800 space-y-3">
                <div className="flex items-start justify-between">
                  <div>
                    <h4 className="text-sm font-bold text-white">{req.student_name}</h4>
                    <p className="text-xs text-purple-300 font-semibold mt-0.5">{req.topic}</p>
                  </div>
                  <span className={`text-[10px] font-bold px-2 py-0.5 rounded-full uppercase ${
                    req.status === 'accepted' ? 'bg-emerald-500/20 text-emerald-300' :
                    req.status === 'rejected' ? 'bg-red-500/20 text-red-300' :
                    'bg-amber-500/20 text-amber-300'
                  }`}>
                    {req.status}
                  </span>
                </div>

                <p className="text-xs text-slate-300 bg-slate-900 p-2.5 rounded-xl border border-slate-800">{req.message}</p>

                {req.ai_match_rationale && (
                  <p className="text-[10px] text-purple-300 italic flex items-center gap-1">
                    <Sparkles className="w-3 h-3 text-amber-300" /> {req.ai_match_rationale}
                  </p>
                )}

                {req.status === 'pending' && (
                  <div className="flex gap-2 pt-1">
                    <button
                      onClick={() => handleMentorAction(req.id, 'accepted')}
                      className="flex-1 py-1.5 rounded-xl bg-emerald-600 hover:bg-emerald-500 text-white text-xs font-bold flex items-center justify-center gap-1 transition-all"
                    >
                      <CheckCircle className="w-3.5 h-3.5" /> Accept
                    </button>

                    <button
                      onClick={() => handleMentorAction(req.id, 'rejected')}
                      className="flex-1 py-1.5 rounded-xl bg-red-950/60 hover:bg-red-900 text-red-300 border border-red-800 text-xs font-bold flex items-center justify-center gap-1 transition-all"
                    >
                      <XCircle className="w-3.5 h-3.5" /> Decline
                    </button>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Message Student Modal */}
      {showMessageModal && selectedStudent && (
        <div className="fixed inset-0 z-50 bg-slate-950/80 backdrop-blur-md flex items-center justify-center p-4">
          <div className="w-full max-w-md bg-slate-900 border border-purple-500/30 rounded-3xl p-6 space-y-4 shadow-2xl">
            <h3 className="text-lg font-bold text-white">Send Department Message</h3>
            <p className="text-xs text-slate-400">Recipient: <span className="text-purple-300 font-semibold">{selectedStudent.name}</span> ({selectedStudent.department} Dept)</p>

            <form onSubmit={handleSendMessage} className="space-y-3">
              <div>
                <label className="block text-xs text-slate-300 mb-1">Subject Title</label>
                <input
                  type="text"
                  value={msgTitle}
                  onChange={e => setMsgTitle(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-100 rounded-xl p-2.5 outline-none"
                />
              </div>

              <div>
                <label className="block text-xs text-slate-300 mb-1">Message Content</label>
                <textarea
                  rows={4}
                  value={msgBody}
                  onChange={e => setMsgBody(e.target.value)}
                  className="w-full bg-slate-950 border border-slate-800 text-xs text-slate-100 rounded-xl p-2.5 outline-none"
                />
              </div>

              <div className="flex gap-2 justify-end pt-2">
                <button
                  type="button"
                  onClick={() => setShowMessageModal(false)}
                  className="px-4 py-2 rounded-xl bg-slate-800 text-xs text-slate-300"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={sendingMsg}
                  className="px-4 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 text-xs text-white font-semibold"
                >
                  {sendingMsg ? 'Delivering...' : 'Send Message'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
