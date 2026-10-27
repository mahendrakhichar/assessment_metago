'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { trends } from '@/lib/api';
import type { Topic } from '@/lib/api';

export default function TrendsPage() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<'all' | 'trending' | 'evergreen'>('all');

  useEffect(() => {
    trends
      .topics()
      .then(setTopics)
      .catch(() => setTopics([]))
      .finally(() => setLoading(false));
  }, []);

  const filtered = topics.filter((t) => {
    if (filter === 'trending') return t.is_trending;
    if (filter === 'evergreen') return t.is_evergreen;
    return true;
  });

  const riskColors: Record<string, string> = {
    low: 'var(--brand-success)',
    medium: 'var(--brand-warning)',
    high: 'var(--brand-danger)',
    critical: 'var(--brand-danger)',
  };

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Trend Explorer
          </div>
          <div className="demo-banner">🧪 Demo Mode</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Trend Explorer</h1>
              <p className="page-subtitle">Discover and score topics for GLP-1, obesity, and metabolic health content</p>
            </div>
            <button className="btn btn-primary">+ Add Topic</button>
          </div>

          {/* Filters */}
          <div style={{ display: 'flex', gap: '0.5rem', marginBottom: '1.5rem' }}>
            {(['all', 'trending', 'evergreen'] as const).map((f) => (
              <button
                key={f}
                className={`btn ${filter === f ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                onClick={() => setFilter(f)}
              >
                {f === 'all' ? '🌐 All Topics' : f === 'trending' ? '🔥 Trending' : '🌲 Evergreen'}
              </button>
            ))}
            <div style={{ marginLeft: 'auto', color: 'var(--text-muted)', fontSize: '0.8rem', display: 'flex', alignItems: 'center' }}>
              {filtered.length} topics
            </div>
          </div>

          {loading ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 80, borderRadius: 'var(--radius-lg)' }} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="card">
              <div className="empty-state">
                <div className="empty-icon">📊</div>
                <h3>No topics yet</h3>
                <p style={{ color: 'var(--text-muted)', maxWidth: 400, textAlign: 'center' }}>
                  The Trend Intelligence Agent will discover and score topics automatically.
                  In Demo mode, you can manually add topics using the API.
                </p>
                <div className="alert alert-info" style={{ maxWidth: 500, textAlign: 'left', marginTop: '1rem' }}>
                  <span>💡</span>
                  <div style={{ fontSize: '0.8rem' }}>
                    <strong>Try it:</strong> POST to <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0 4px', borderRadius: 3 }}>/api/v1/trends/topics</code> to add a topic manually.
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
              {filtered.map((topic, i) => (
                <div
                  key={topic.id}
                  className="card animate-fade-in"
                  style={{ animationDelay: `${i * 50}ms`, cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1rem' }}>
                    {/* Score indicator */}
                    <div
                      style={{
                        width: 50,
                        height: 50,
                        borderRadius: 'var(--radius-sm)',
                        background: 'var(--bg-elevated)',
                        display: 'flex',
                        flexDirection: 'column',
                        alignItems: 'center',
                        justifyContent: 'center',
                        flexShrink: 0,
                        border: '1px solid var(--bg-border)',
                      }}
                    >
                      <span style={{ fontSize: '1.25rem', lineHeight: 1, fontWeight: 800, color: 'var(--text-primary)' }}>
                        {topic.final_score.toFixed(0)}
                      </span>
                      <span style={{ fontSize: '0.6rem', color: 'var(--text-muted)' }}>score</span>
                    </div>

                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.25rem', flexWrap: 'wrap' }}>
                        <h4 style={{ margin: 0, color: 'var(--text-primary)' }}>{topic.title}</h4>
                        {topic.is_trending && <span className="badge badge-published">🔥 Trending</span>}
                        {topic.is_evergreen && <span className="badge badge-scheduled">🌲 Evergreen</span>}
                        <span
                          className={`badge badge-${topic.medical_risk}`}
                          style={{ color: riskColors[topic.medical_risk] }}
                        >
                          {topic.medical_risk} risk
                        </span>
                      </div>
                      {topic.category && (
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>{topic.category}</div>
                      )}
                    </div>

                    <div style={{ display: 'flex', gap: '0.5rem', flexShrink: 0 }}>
                      <button className="btn btn-secondary btn-sm">View Details</button>
                      <button className="btn btn-primary btn-sm">Create Content</button>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
