import React, { useState, useRef, useEffect } from 'react';
import { agentChatApi } from '../services/api';
import { MessageSquare, X, Send, Bot, User, Sparkles, FileText, Minimize2 } from 'lucide-react';

export const ChatbotWidget = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState([
    {
      sender: 'bot',
      text: 'Hello! I am EduNexus Site-Wide RAG Assistant. Ask me about campus placements, academic policies, faculty research mentors, or assignment rules!',
      agent: 'system'
    }
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const chatEndRef = useRef(null);

  const samplePrompts = [
    "What is the minimum CGPA for placement?",
    "Recommend a mentor for Deep Learning & NLP",
    "What is the penalty for late assignment submission?",
    "Predict next year's placement outlook"
  ];

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, loading]);

  const handleSend = async (queryText = input) => {
    const textToSend = queryText.trim();
    if (!textToSend || loading) return;

    const userMsg = { sender: 'user', text: textToSend };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await agentChatApi(textToSend);
      const botMsg = {
        sender: 'bot',
        text: res.response,
        agent: res.agent_used,
        grounding_docs: res.grounding_docs || []
      };
      setMessages(prev => [...prev, botMsg]);
    } catch (err) {
      setMessages(prev => [
        ...prev,
        {
          sender: 'bot',
          text: `I handled your request via system fallback: ${err.message}`,
          agent: 'fallback'
        }
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="fixed bottom-6 right-6 z-50">
      {!isOpen && (
        <button
          onClick={() => setIsOpen(true)}
          className="flex items-center gap-2.5 px-4 py-3 rounded-2xl bg-gradient-to-r from-purple-600 via-indigo-600 to-purple-700 text-white font-semibold shadow-xl shadow-purple-600/30 hover:scale-105 transition-all cursor-pointer border border-purple-400/30"
        >
          <Sparkles className="w-5 h-5 text-amber-300 animate-pulse" />
          <span>Ask EduNexus AI</span>
          <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping"></span>
        </button>
      )}

      {isOpen && (
        <div className="w-[360px] sm:w-[420px] h-[520px] rounded-2xl bg-slate-950/95 border border-purple-500/30 shadow-2xl flex flex-col overflow-hidden backdrop-blur-xl animate-in fade-in slide-in-from-bottom-4 duration-300">
          {/* Header */}
          <div className="px-4 py-3.5 bg-gradient-to-r from-purple-950 to-indigo-950 border-b border-purple-500/20 flex items-center justify-between">
            <div className="flex items-center gap-2.5">
              <div className="w-8 h-8 rounded-lg bg-purple-600 flex items-center justify-center text-white shadow-md">
                <Bot className="w-5 h-5" />
              </div>
              <div>
                <h3 className="text-sm font-bold text-slate-100 flex items-center gap-1.5">
                  EduNexus AI Chatbot
                  <span className="text-[10px] bg-purple-500/30 text-purple-200 px-1.5 py-0.5 rounded font-mono">LangGraph</span>
                </h3>
                <p className="text-[11px] text-purple-300/70">Grounded RAG & Academic Decision Support</p>
              </div>
            </div>
            <button
              onClick={() => setIsOpen(false)}
              className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800/60 transition-colors"
            >
              <Minimize2 className="w-4 h-4" />
            </button>
          </div>

          {/* Messages Body */}
          <div className="flex-1 overflow-y-auto p-4 space-y-3.5 text-xs">
            {messages.map((m, idx) => (
              <div
                key={idx}
                className={`flex gap-2.5 ${m.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                {m.sender === 'bot' && (
                  <div className="w-6 h-6 rounded-md bg-purple-900/60 text-purple-300 flex items-center justify-center shrink-0 border border-purple-500/30 mt-0.5">
                    <Bot className="w-3.5 h-3.5" />
                  </div>
                )}
                <div
                  className={`max-w-[85%] p-3 rounded-xl leading-relaxed ${
                    m.sender === 'user'
                      ? 'bg-purple-600 text-white rounded-tr-none font-medium'
                      : 'bg-slate-900 text-slate-200 border border-slate-800 rounded-tl-none'
                  }`}
                >
                  <p className="whitespace-pre-wrap">{m.text}</p>
                  
                  {m.grounding_docs && m.grounding_docs.length > 0 && (
                    <div className="mt-2 pt-2 border-t border-slate-800/80 flex flex-wrap gap-1 text-[10px] text-purple-300">
                      <span className="flex items-center gap-1 font-semibold text-slate-400">
                        <FileText className="w-3 h-3 text-purple-400" /> Sources:
                      </span>
                      {m.grounding_docs.map((doc, dIdx) => (
                        <span key={dIdx} className="bg-purple-950/80 border border-purple-800/50 px-1.5 py-0.5 rounded text-purple-200">
                          {doc}
                        </span>
                      ))}
                    </div>
                  )}

                  {m.agent && (
                    <div className="mt-1 text-[9px] text-slate-400 font-mono text-right">
                      agent: {m.agent}
                    </div>
                  )}
                </div>
              </div>
            ))}

            {loading && (
              <div className="flex gap-2.5 justify-start">
                <div className="w-6 h-6 rounded-md bg-purple-900/60 text-purple-300 flex items-center justify-center shrink-0 border border-purple-500/30">
                  <Bot className="w-3.5 h-3.5 animate-spin" />
                </div>
                <div className="bg-slate-900 text-slate-400 px-3 py-2 rounded-xl text-xs flex items-center gap-2 border border-slate-800">
                  <span className="w-1.5 h-1.5 rounded-full bg-purple-400 animate-ping"></span>
                  <span>Reasoning over ERP database & RAG docs...</span>
                </div>
              </div>
            )}
            <div ref={chatEndRef} />
          </div>

          {/* Sample Starter Prompts */}
          <div className="px-3 py-2 bg-slate-900/40 border-t border-slate-800 flex gap-1.5 overflow-x-auto no-scrollbar">
            {samplePrompts.map((p, idx) => (
              <button
                key={idx}
                onClick={() => handleSend(p)}
                className="shrink-0 text-[10px] bg-purple-950/40 hover:bg-purple-900/60 border border-purple-800/40 text-purple-200 px-2.5 py-1 rounded-full transition-all cursor-pointer whitespace-nowrap"
              >
                {p}
              </button>
            ))}
          </div>

          {/* Input Footer */}
          <div className="p-3 bg-slate-950 border-t border-slate-800 flex gap-2">
            <input
              type="text"
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyDown={e => e.key === 'Enter' && handleSend()}
              placeholder="Ask a question..."
              className="flex-1 bg-slate-900 border border-slate-800 focus:border-purple-500 text-slate-100 placeholder-slate-500 text-xs rounded-xl px-3 py-2 outline-none transition-all"
            />
            <button
              onClick={() => handleSend()}
              disabled={loading || !input.trim()}
              className="px-3 py-2 rounded-xl bg-purple-600 hover:bg-purple-500 disabled:opacity-50 text-white transition-all cursor-pointer"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </div>
      )}
    </div>
  );
};
