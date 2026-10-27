'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';

interface OverviewStats {
  total_assets: number;
  published_assets: number;
  pending_review: number;
  total_posts: number;
  connected_accounts: number;
}

interface MetricCard {
  label: string;
  value: string | number;
  icon: string;
  note?: string;
}

function KpiCard({ label, value, icon, note }: MetricCard) {
  return (
    <div className="stat-card animate-fade-in">
      <div className="stat-icon">{icon}</div>
      <div className="stat-value">{value}</div>
      <div className="stat-label">{label}</div>
      {note && <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.3rem' }}>{note}</div>}
    </div>
  );
}

const FUNNEL_STAGES = ['Awareness', 'Education', 'Consideration', 'Conversion', 'Retention'];

export default function AnalyticsPage() {
  const [stats, setStats] = useState<OverviewStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api/v1';
    fetch(`${API}/analytics/overview`, {
      headers: { 'Content-Type': 'application/json' },
    })
      .then((r) => (r.ok ? r.json() : Promise.reject()))
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, []);

  // Mock chart bars from the stats available
  const barData = stats
    ? [
        { label: 'Total', value: stats.total_assets, max: Math.max(stats.total_assets, 1) },
        { label: 'Published', value: stats.published_assets, max: Math.max(stats.total_assets, 1) },
        { label: 'Pending', value: stats.pending_review, max: Math.max(stats.total_assets, 1) },
        { label: 'Posts', value: stats.total_posts, max: Math.max(stats.total_posts, 1) },
      ]
    : [];

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Analytics
          </div>
          <div className="demo-banner">🧪 Demo Mode</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Analytics &amp; Performance</h1>
              <p className="page-subtitle">Content performance metrics and publishing intelligence</p>
            </div>
            <button className="btn btn-secondary">📊 Export Report</button>
          </div>

          {/* KPI Grid */}
          {loading ? (
            <div className="stat-grid" style={{ marginBottom: '2rem' }}>
              {[...Array(5)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 140, borderRadius: 'var(--radius-lg)' }} />
              ))}
            </div>
          ) : (
            <div className="stat-grid" style={{ marginBottom: '2rem' }}>
              <KpiCard icon="📝" value={stats?.total_assets ?? 0} label="Total Assets" />
              <KpiCard icon="🚀" value={stats?.published_assets ?? 0} label="Published" note="Live on platforms" />
              <KpiCard icon="⏳" value={stats?.pending_review ?? 0} label="Pending Review" note="Awaiting approval" />
              <KpiCard icon="📤" value={stats?.total_posts ?? 0} label="Total Posts" />
              <KpiCard icon="🔗" value={stats?.connected_accounts ?? 0} label="Connected Accounts" />
            </div>
          )}

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1.5rem', marginBottom: '1.5rem' }}>
            {/* Content Status Distribution */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">📊 Content Status Distribution</h3>
              </div>
              {barData.length === 0 ? (
                <div className="empty-state" style={{ padding: '2rem' }}>
                  <div className="empty-icon">📊</div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.875rem' }}>Connect the backend to see metrics</p>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '0.875rem', padding: '0.5rem 0' }}>
                  {barData.map((bar) => (
                    <div key={bar.label}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.25rem' }}>
                        <span style={{ fontSize: '0.8rem', color: 'var(--text-secondary)' }}>{bar.label}</span>
                        <span style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}>{bar.value}</span>
                      </div>
                      <div style={{ height: 8, borderRadius: 4, background: 'var(--bg-elevated)', overflow: 'hidden' }}>
                        <div
                          style={{
                            height: '100%',
                            width: `${Math.round((bar.value / bar.max) * 100)}%`,
                            background: 'var(--gradient-brand)',
                            borderRadius: 4,
                            transition: 'width 0.6s ease',
                          }}
                        />
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>

            {/* Content Funnel */}
            <div className="card">
              <div className="card-header">
                <h3 className="card-title">🔽 Content Funnel Coverage</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem', padding: '0.5rem 0' }}>
                {FUNNEL_STAGES.map((stage, i) => {
                  const width = 100 - i * 15;
                  return (
                    <div key={stage} style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                      <div
                        style={{
                          height: 36,
                          width: `${width}%`,
                          background: `hsl(${240 + i * 20}, 70%, ${30 + i * 5}%)`,
                          borderRadius: 'var(--radius-sm)',
                          display: 'flex',
                          alignItems: 'center',
                          paddingLeft: '0.75rem',
                          fontSize: '0.75rem',
                          fontWeight: 600,
                          color: 'white',
                          transition: 'width 0.4s ease',
                        }}
                      >
                        {stage}
                      </div>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', whiteSpace: 'nowrap' }}>
                        {width}%
                      </span>
                    </div>
                  );
                })}
                <p style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  * Illustrative distribution — will reflect real data when content is created.
                </p>
              </div>
            </div>
          </div>

          {/* Platform Performance */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div className="card-header">
              <h3 className="card-title">📱 Platform Performance Overview</h3>
              <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Demo — real metrics require platform API credentials</span>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '1rem' }}>
              {[
                { platform: 'YouTube', icon: '▶️', reach: '—', views: '—', subs: '—' },
                { platform: 'Instagram', icon: '📸', reach: '—', views: '—', subs: '—' },
                { platform: 'X (Twitter)', icon: '𝕏', reach: '—', views: '—', subs: '—' },
              ].map((p) => (
                <div
                  key={p.platform}
                  style={{
                    padding: '1rem',
                    background: 'var(--bg-elevated)',
                    borderRadius: 'var(--radius-sm)',
                    border: '1px solid var(--bg-border)',
                  }}
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.75rem' }}>
                    <span style={{ fontSize: '1.25rem' }}>{p.icon}</span>
                    <span style={{ fontWeight: 600, color: 'var(--text-primary)', fontSize: '0.875rem' }}>{p.platform}</span>
                  </div>
                  {[['Reach', p.reach], ['Impressions', p.views], ['Followers', p.subs]].map(([label, val]) => (
                    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.375rem' }}>
                      <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{label}</span>
                      <span style={{ fontSize: '0.75rem', fontWeight: 500, color: 'var(--text-secondary)' }}>{val}</span>
                    </div>
                  ))}
                </div>
              ))}
            </div>
          </div>

          {/* Medical compliance summary */}
          <div className="alert alert-info">
            <span>🏥</span>
            <div>
              <div style={{ fontWeight: 600, marginBottom: '0.25rem' }}>Compliance Monitoring</div>
              <div style={{ fontSize: '0.8rem', opacity: 0.85 }}>
                Medical review gate is enforced in the content pipeline. No HIGH or CRITICAL risk content
                can be published without a human medical reviewer approval — tracked in audit logs.
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
