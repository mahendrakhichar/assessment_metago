'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';

type Priority = 'high' | 'medium' | 'low';
type Category = 'question' | 'complaint' | 'testimonial' | 'mention' | 'dm';

interface Message {
  id: string;
  platform: string;
  author: string;
  content: string;
  time: string;
  category: Category;
  priority: Priority;
  replied: boolean;
}

const MOCK_MESSAGES: Message[] = [
  {
    id: '1',
    platform: 'instagram',
    author: '@patient_journey_india',
    content: 'Is the GLP-1 program covered by insurance? I have a family floater plan.',
    time: '2 min ago',
    category: 'question',
    priority: 'high',
    replied: false,
  },
  {
    id: '2',
    platform: 'youtube',
    author: 'Dr. Priya Mehta',
    content: 'Great video on metabolic health! Could you share the clinical references for the semaglutide data?',
    time: '15 min ago',
    category: 'question',
    priority: 'high',
    replied: false,
  },
  {
    id: '3',
    platform: 'x',
    author: '@healthtech_india',
    content: 'Just started the Metago program. Week 2 and already feeling the difference!',
    time: '1 hr ago',
    category: 'testimonial',
    priority: 'medium',
    replied: false,
  },
  {
    id: '4',
    platform: 'instagram',
    author: '@wellness_mumbai',
    content: 'Where can I find a Metago provider in Pune?',
    time: '2 hr ago',
    category: 'question',
    priority: 'medium',
    replied: true,
  },
  {
    id: '5',
    platform: 'instagram',
    author: '@healthylife2026',
    content: 'The app keeps crashing when I try to log my meals. Please fix!',
    time: '3 hr ago',
    category: 'complaint',
    priority: 'high',
    replied: false,
  },
];

const PLATFORM_ICONS: Record<string, string> = {
  youtube: '▶️',
  instagram: '📸',
  x: '𝕏',
};

const CATEGORY_COLORS: Record<Category, string> = {
  question: 'var(--brand-primary-light)',
  complaint: 'var(--brand-danger)',
  testimonial: 'var(--brand-success)',
  mention: 'var(--brand-warning)',
  dm: 'var(--text-muted)',
};

const PRIORITY_BADGE: Record<Priority, string> = {
  high: 'badge-blocked',
  medium: 'badge-medical_review',
  low: 'badge-draft',
};

export default function CommunityPage() {
  const [messages, setMessages] = useState<Message[]>(MOCK_MESSAGES);
  const [filter, setFilter] = useState<'all' | 'unread' | Category>('all');
  const [selected, setSelected] = useState<Message | null>(null);
  const [reply, setReply] = useState('');

  const filtered = messages.filter((m) => {
    if (filter === 'all') return true;
    if (filter === 'unread') return !m.replied;
    return m.category === filter;
  });

  const unreadCount = messages.filter((m) => !m.replied).length;

  const markReplied = (id: string) => {
    setMessages((prev) => prev.map((m) => (m.id === id ? { ...m, replied: true } : m)));
    setSelected(null);
    setReply('');
  };

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Community Inbox
          </div>
          <div className="demo-banner">🧪 Demo Mode — Sample messages shown</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Community Inbox</h1>
              <p className="page-subtitle">
                Manage comments, messages, and mentions across all social platforms
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem', alignItems: 'center' }}>
              {unreadCount > 0 && (
                <span
                  style={{
                    background: 'var(--brand-danger)',
                    color: 'white',
                    borderRadius: 20,
                    padding: '0.25rem 0.75rem',
                    fontSize: '0.8rem',
                    fontWeight: 700,
                  }}
                >
                  {unreadCount} unread
                </span>
              )}
              <button className="btn btn-secondary btn-sm">⚙️ Auto-reply Settings</button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1.6fr', gap: '1.5rem' }}>
            {/* Message List */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {/* Filters */}
              <div
                style={{
                  padding: '1rem',
                  borderBottom: '1px solid var(--bg-border)',
                  display: 'flex',
                  gap: '0.4rem',
                  flexWrap: 'wrap',
                }}
              >
                {(['all', 'unread', 'question', 'complaint', 'testimonial'] as const).map((f) => (
                  <button
                    key={f}
                    className={`btn ${filter === f ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                    onClick={() => setFilter(f)}
                    style={{ fontSize: '0.75rem' }}
                  >
                    {f === 'all' ? '🌐 All' : f === 'unread' ? `📬 Unread (${unreadCount})` : f}
                  </button>
                ))}
              </div>

              {/* Messages */}
              <div style={{ overflowY: 'auto', maxHeight: 520 }}>
                {filtered.length === 0 ? (
                  <div className="empty-state" style={{ padding: '3rem' }}>
                    <div className="empty-icon">💬</div>
                    <p style={{ color: 'var(--text-muted)' }}>No messages in this filter</p>
                  </div>
                ) : (
                  filtered.map((msg) => (
                    <div
                      key={msg.id}
                      onClick={() => setSelected(msg)}
                      style={{
                        padding: '0.875rem 1rem',
                        borderBottom: '1px solid var(--bg-border)',
                        cursor: 'pointer',
                        background:
                          selected?.id === msg.id
                            ? 'var(--bg-elevated)'
                            : msg.replied
                            ? 'transparent'
                            : 'rgba(108, 99, 255, 0.04)',
                        transition: 'background 0.15s',
                      }}
                    >
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                          <span>{PLATFORM_ICONS[msg.platform] || '💬'}</span>
                          <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>
                            {msg.author}
                          </span>
                          {!msg.replied && (
                            <span
                              style={{
                                width: 7,
                                height: 7,
                                borderRadius: '50%',
                                background: 'var(--brand-primary)',
                                display: 'inline-block',
                              }}
                            />
                          )}
                        </div>
                        <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{msg.time}</span>
                      </div>
                      <p
                        className="truncate"
                        style={{
                          fontSize: '0.78rem',
                          color: 'var(--text-secondary)',
                          overflow: 'hidden',
                          whiteSpace: 'nowrap',
                          textOverflow: 'ellipsis',
                        }}
                      >
                        {msg.content}
                      </p>
                      <div style={{ display: 'flex', gap: '0.4rem', marginTop: '0.4rem' }}>
                        <span
                          style={{
                            fontSize: '0.65rem',
                            padding: '1px 6px',
                            borderRadius: 99,
                            border: `1px solid ${CATEGORY_COLORS[msg.category]}`,
                            color: CATEGORY_COLORS[msg.category],
                            textTransform: 'capitalize',
                          }}
                        >
                          {msg.category}
                        </span>
                        <span className={`badge ${PRIORITY_BADGE[msg.priority]}`} style={{ fontSize: '0.65rem' }}>
                          {msg.priority}
                        </span>
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>

            {/* Reply Pane */}
            <div className="card">
              {selected ? (
                <>
                  <div style={{ marginBottom: '1.25rem' }}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', marginBottom: '0.5rem' }}>
                      <span style={{ fontSize: '1.5rem' }}>{PLATFORM_ICONS[selected.platform]}</span>
                      <div>
                        <div style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{selected.author}</div>
                        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                          via {selected.platform} · {selected.time}
                        </div>
                      </div>
                      <div style={{ marginLeft: 'auto', display: 'flex', gap: '0.4rem' }}>
                        <span
                          style={{
                            fontSize: '0.7rem',
                            padding: '2px 8px',
                            borderRadius: 99,
                            border: `1px solid ${CATEGORY_COLORS[selected.category]}`,
                            color: CATEGORY_COLORS[selected.category],
                            textTransform: 'capitalize',
                          }}
                        >
                          {selected.category}
                        </span>
                        <span className={`badge ${PRIORITY_BADGE[selected.priority]}`}>
                          {selected.priority} priority
                        </span>
                      </div>
                    </div>
                    <div
                      style={{
                        padding: '1rem',
                        background: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--bg-border)',
                        fontSize: '0.875rem',
                        color: 'var(--text-primary)',
                        lineHeight: 1.6,
                      }}
                    >
                      {selected.content}
                    </div>
                  </div>

                  <div className="alert alert-info" style={{ marginBottom: '1rem' }}>
                    <span>🤖</span>
                    <div style={{ fontSize: '0.78rem' }}>
                      <strong>AI Suggestion:</strong> This looks like a {selected.category}. Suggested response
                      template available. Medical claims or specific treatment advice should be reviewed before sending.
                    </div>
                  </div>

                  <div style={{ marginBottom: '0.75rem' }}>
                    <label style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '0.4rem', display: 'block' }}>
                      Your Reply
                    </label>
                    <textarea
                      value={reply}
                      onChange={(e) => setReply(e.target.value)}
                      placeholder="Type your reply here... In Demo mode, replies are simulated."
                      rows={4}
                      style={{
                        width: '100%',
                        padding: '0.75rem',
                        background: 'var(--bg-elevated)',
                        border: '1px solid var(--bg-border)',
                        borderRadius: 'var(--radius-sm)',
                        color: 'var(--text-primary)',
                        fontSize: '0.875rem',
                        resize: 'vertical',
                        outline: 'none',
                        fontFamily: 'inherit',
                        boxSizing: 'border-box',
                      }}
                    />
                  </div>

                  <div style={{ display: 'flex', gap: '0.75rem', justifyContent: 'flex-end' }}>
                    <button className="btn btn-ghost btn-sm" onClick={() => setSelected(null)}>
                      Cancel
                    </button>
                    <button
                      className="btn btn-secondary btn-sm"
                      onClick={() => markReplied(selected.id)}
                    >
                      Mark as Handled
                    </button>
                    <button
                      className="btn btn-primary btn-sm"
                      onClick={() => markReplied(selected.id)}
                      disabled={!reply.trim()}
                    >
                      📤 Send Reply (Demo)
                    </button>
                  </div>
                </>
              ) : (
                <div className="empty-state" style={{ padding: '4rem 2rem' }}>
                  <div className="empty-icon">💬</div>
                  <h3>Select a message</h3>
                  <p style={{ color: 'var(--text-muted)', textAlign: 'center', maxWidth: 300 }}>
                    Click on a message from the inbox to view and reply. Real community management requires
                    platform API credentials.
                  </p>
                </div>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
