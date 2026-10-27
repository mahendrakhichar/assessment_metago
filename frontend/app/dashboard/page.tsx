'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { analytics, content, trends, accounts } from '@/lib/api';
import type { OverviewStats, ContentIdea, Topic, SocialAccount } from '@/lib/api';

// ── Stat Card Component ────────────────────────────────────────────
function StatCard({
  icon,
  value,
  label,
  delta,
  positive,
}: {
  icon: string;
  value: number | string;
  label: string;
  delta?: string;
  positive?: boolean;
}) {
  return (
    <div className="stat-card animate-fade-in">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {delta && (
        <div className={`stat-delta ${positive ? 'positive' : 'negative'}`}>{delta}</div>
      )}
    </div>
  );
}

// ── Content Idea Row ────────────────────────────────────────────────
function IdeaRow({ idea }: { idea: ContentIdea }) {
  const statusClass = `badge badge-${idea.status.toLowerCase()}`;
  return (
    <tr>
      <td>
        <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{idea.title}</div>
        {idea.audience && (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {idea.audience}
          </div>
        )}
      </td>
      <td>
        <span className={statusClass}>{idea.status.replace('_', ' ')}</span>
      </td>
      <td>
        <span
          style={{
            fontWeight: 600,
            color: idea.priority_score > 7 ? 'var(--brand-success)' : 'var(--text-secondary)',
          }}
        >
          {idea.priority_score.toFixed(1)}
        </span>
      </td>
      <td style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
        {new Date(idea.created_at).toLocaleDateString('en-IN')}
      </td>
    </tr>
  );
}

// ── Topic Row ────────────────────────────────────────────────────────
function TopicRow({ topic }: { topic: Topic }) {
  const riskClass = `badge badge-${topic.medical_risk}`;
  return (
    <tr>
      <td>
        <div style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{topic.title}</div>
        {topic.category && (
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.2rem' }}>
            {topic.category}
          </div>
        )}
      </td>
      <td>
        <div style={{ display: 'flex', gap: '0.5rem', flexWrap: 'wrap' }}>
          {topic.is_trending && <span className="badge badge-published">Trending</span>}
          {topic.is_evergreen && <span className="badge badge-scheduled">Evergreen</span>}
        </div>
      </td>
      <td>
        <span className={riskClass}>{topic.medical_risk} risk</span>
      </td>
      <td>
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
          }}
        >
          <div
            style={{
              height: 6,
              borderRadius: 3,
              background: 'var(--bg-elevated)',
              flex: 1,
              overflow: 'hidden',
            }}
          >
            <div
              style={{
                height: '100%',
                width: `${Math.round(topic.final_score * 10)}%`,
                background: 'var(--gradient-brand)',
                borderRadius: 3,
              }}
            />
          </div>
          <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)', width: 28 }}>
            {topic.final_score.toFixed(1)}
          </span>
        </div>
      </td>
    </tr>
  );
}

// ── Account Status Badge ────────────────────────────────────────────
function AccountCard({ account }: { account: SocialAccount }) {
  const platformIcons: Record<string, string> = {
    youtube: '▶️',
    instagram: '📸',
    x: '𝕏',
  };

  return (
    <div
      style={{
        display: 'flex',
        alignItems: 'center',
        gap: '0.75rem',
        padding: '0.75rem',
        background: 'var(--bg-elevated)',
        borderRadius: 'var(--radius-sm)',
        border: '1px solid var(--bg-border)',
      }}
    >
      <span style={{ fontSize: '1.25rem' }}>
        {platformIcons[account.platform] || '📱'}
      </span>
      <div style={{ flex: 1, overflow: 'hidden' }}>
        <div
          className="truncate"
          style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}
        >
          {account.display_name || account.account_name}
        </div>
        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
          {account.platform}
        </div>
      </div>
      <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: '0.25rem' }}>
        <span className={`badge badge-${account.platform}`}>
          {account.platform}
        </span>
        {account.is_mock && (
          <span style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>DEMO</span>
        )}
      </div>
    </div>
  );
}

// ── Main Dashboard Page ─────────────────────────────────────────────
export default function DashboardPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [ideas, setIdeas] = useState<ContentIdea[]>([]);
  const [topTopics, setTopTopics] = useState<Topic[]>([]);
  const [socialAccounts, setSocialAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [isConnected, setIsConnected] = useState(false);

  useEffect(() => {
    // Try to load data from backend
    const load = async () => {
      try {
        // Health check first
        const health = await fetch('http://localhost:8000/health');
        if (!health.ok) throw new Error('Backend offline');
        setIsConnected(true);

        // Load data (no auth in demo mode for overview)
        const [overviewData, ideasData, topicsData, accountsData] = await Promise.allSettled([
          analytics.overview().catch(() => null),
          content.ideas().catch(() => []),
          trends.topics().catch(() => []),
          accounts.list().catch(() => []),
        ]);

        if (overviewData.status === 'fulfilled' && overviewData.value) {
          setStats(overviewData.value);
        }
        if (ideasData.status === 'fulfilled') setIdeas((ideasData.value as ContentIdea[]).slice(0, 5));
        if (topicsData.status === 'fulfilled') setTopTopics((topicsData.value as Topic[]).slice(0, 5));
        if (accountsData.status === 'fulfilled') setSocialAccounts(accountsData.value as SocialAccount[]);
      } catch {
        setError('Backend is not connected. Start the server with: cd backend && uvicorn app.main:app --reload');
        // Show demo data anyway
        setStats({
          total_assets: 0,
          published_assets: 0,
          pending_review: 0,
          total_posts: 0,
          connected_accounts: 0,
        });
      } finally {
        setLoading(false);
      }
    };
    load();
  }, []);

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        {/* Topbar */}
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Marketing Command Center
          </div>
          <div className="demo-banner">
            🧪 Demo Mode — No real publishing active
          </div>
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              fontSize: '0.8rem',
              color: isConnected ? 'var(--brand-success)' : 'var(--brand-danger)',
            }}
          >
            <span>{isConnected ? '●' : '○'}</span>
            {isConnected ? 'Backend Connected' : 'Backend Offline'}
          </div>
        </header>

        <div className="page-content">
          {/* Error alert */}
          {error && (
            <div className="alert alert-warning" style={{ marginBottom: '1.5rem' }}>
              <span>⚠️</span>
              <div>
                <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Backend not connected</div>
                <div style={{ fontSize: '0.8rem', opacity: 0.9 }}>
                  Start with: <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0 4px', borderRadius: 3 }}>cd backend && ..\..venv\Scripts\uvicorn app.main:app --reload</code>
                </div>
              </div>
            </div>
          )}

          {/* Page Header */}
          <div className="page-header">
            <div>
              <h1 className="page-title">Overview</h1>
              <p className="page-subtitle">
                {new Date().toLocaleDateString('en-IN', {
                  weekday: 'long',
                  year: 'numeric',
                  month: 'long',
                  day: 'numeric',
                })}
              </p>
            </div>
            <button className="btn btn-primary">
              ✨ Create Content
            </button>
          </div>

          {/* Stats Grid */}
          {loading ? (
            <div className="stat-grid" style={{ marginBottom: '2rem' }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 140, borderRadius: 'var(--radius-lg)' }} />
              ))}
            </div>
          ) : (
            <div className="stat-grid" style={{ marginBottom: '2rem' }}>
              <StatCard icon="📝" value={stats?.total_assets ?? 0} label="Total Content Assets" />
              <StatCard icon="🚀" value={stats?.published_assets ?? 0} label="Published Assets" positive />
              <StatCard
                icon="⏳"
                value={stats?.pending_review ?? 0}
                label="Pending Review"
                delta={stats?.pending_review ? `${stats.pending_review} need attention` : undefined}
                positive={false}
              />
              <StatCard icon="📤" value={stats?.total_posts ?? 0} label="Total Posts Published" />
              <StatCard icon="🔗" value={stats?.connected_accounts ?? 0} label="Connected Accounts" />
            </div>
          )}

          {/* Main content grid */}
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Content Ideas */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">📋 Content Ideas Pipeline</h3>
                <a href="/content" className="btn btn-ghost btn-sm">View All →</a>
              </div>
              {ideas.length === 0 ? (
                <div className="empty-state" style={{ padding: '2rem' }}>
                  <div className="empty-icon">💡</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    No content ideas yet. Connect the backend to see ideas.
                  </div>
                </div>
              ) : (
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Idea</th>
                        <th>Status</th>
                        <th>Score</th>
                        <th>Date</th>
                      </tr>
                    </thead>
                    <tbody>
                      {ideas.map((idea) => (
                        <IdeaRow key={idea.id} idea={idea} />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>

            {/* Trending Topics */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">📈 Top Trending Topics</h3>
                <a href="/trends" className="btn btn-ghost btn-sm">Explore →</a>
              </div>
              {topTopics.length === 0 ? (
                <div className="empty-state" style={{ padding: '2rem' }}>
                  <div className="empty-icon">🔍</div>
                  <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                    No topics discovered yet. The trend intelligence agent will populate this.
                  </div>
                </div>
              ) : (
                <div className="table-container">
                  <table>
                    <thead>
                      <tr>
                        <th>Topic</th>
                        <th>Type</th>
                        <th>Risk</th>
                        <th>Score</th>
                      </tr>
                    </thead>
                    <tbody>
                      {topTopics.map((topic) => (
                        <TopicRow key={topic.id} topic={topic} />
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </div>

          {/* Connected Accounts */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">🔗 Connected Social Accounts</h3>
              <a href="/publishing" className="btn btn-ghost btn-sm">Manage →</a>
            </div>
            {socialAccounts.length === 0 ? (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <div className="empty-icon">📱</div>
                <div style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>
                  No accounts connected. They will appear after seeding the demo database.
                </div>
              </div>
            ) : (
              <div
                style={{
                  display: 'grid',
                  gridTemplateColumns: 'repeat(auto-fill, minmax(220px, 1fr))',
                  gap: '0.75rem',
                }}
              >
                {socialAccounts.map((acc) => (
                  <AccountCard key={acc.id} account={acc} />
                ))}
              </div>
            )}
          </div>

          {/* Medical compliance notice */}
          <div
            className="alert alert-info"
            style={{ marginTop: '1.5rem' }}
          >
            <span>🏥</span>
            <div>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>
                Medical Compliance Gate Active
              </div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85 }}>
                All content with HIGH or CRITICAL medical risk requires a human medical reviewer before
                publication. No AI confidence score bypasses this gate.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
