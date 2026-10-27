'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { content } from '@/lib/api';
import type { CanonicalAsset, ContentPillar } from '@/lib/api';

const STATUS_ORDER = [
  'draft', 'fact_check', 'medical_review', 'brand_review',
  'approved', 'scheduled', 'published', 'blocked',
];

export default function ContentStudioPage() {
  const [assets, setAssets] = useState<CanonicalAsset[]>([]);
  const [pillars, setPillars] = useState<ContentPillar[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('all');

  useEffect(() => {
    Promise.allSettled([
      content.assets(),
      content.pillars(),
    ]).then(([assetsRes, pillarsRes]) => {
      if (assetsRes.status === 'fulfilled') setAssets(assetsRes.value);
      if (pillarsRes.status === 'fulfilled') setPillars(pillarsRes.value);
    }).finally(() => setLoading(false));
  }, []);

  const filtered = statusFilter === 'all'
    ? assets
    : assets.filter((a) => a.status === statusFilter);

  const counts = STATUS_ORDER.reduce<Record<string, number>>((acc, s) => {
    acc[s] = assets.filter((a) => a.status === s).length;
    return acc;
  }, {});

  const riskIcon: Record<string, string> = {
    low: '🟢', medium: '🟡', high: '🔴', critical: '💀',
  };

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Content Studio
          </div>
          <div className="demo-banner">🧪 Demo Mode</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Content Studio</h1>
              <p className="page-subtitle">
                Manage content assets, platform variants, and approval workflow
              </p>
            </div>
            <div style={{ display: 'flex', gap: '0.75rem' }}>
              <button className="btn btn-secondary">📋 Content Ideas</button>
              <button className="btn btn-primary">✨ New Asset</button>
            </div>
          </div>

          {/* Status pipeline visualization */}
          <div
            style={{
              display: 'flex',
              gap: '0.5rem',
              marginBottom: '1.5rem',
              overflowX: 'auto',
              padding: '0.25rem 0',
            }}
          >
            <button
              className={`btn ${statusFilter === 'all' ? 'btn-primary' : 'btn-secondary'} btn-sm`}
              onClick={() => setStatusFilter('all')}
            >
              All ({assets.length})
            </button>
            {STATUS_ORDER.map((s) => (
              <button
                key={s}
                className={`btn ${statusFilter === s ? 'btn-primary' : 'btn-ghost'} btn-sm`}
                onClick={() => setStatusFilter(s)}
                style={{ whiteSpace: 'nowrap' }}
              >
                <span className={`badge badge-${s}`} style={{ marginRight: '0.25rem' }}>
                  {counts[s] || 0}
                </span>
                {s.replace('_', ' ')}
              </button>
            ))}
          </div>

          {/* Content Grid */}
          {loading ? (
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))', gap: '1rem' }}>
              {[...Array(6)].map((_, i) => (
                <div key={i} className="skeleton" style={{ height: 180, borderRadius: 'var(--radius-lg)' }} />
              ))}
            </div>
          ) : filtered.length === 0 ? (
            <div className="card">
              <div className="empty-state">
                <div className="empty-icon">✍️</div>
                <h3>No content assets yet</h3>
                <p style={{ color: 'var(--text-muted)', maxWidth: 400, textAlign: 'center' }}>
                  Content assets are the canonical pieces of content that get adapted into platform-specific
                  variants for YouTube, Instagram, and X.
                </p>
                <div className="alert alert-info" style={{ maxWidth: 500, textAlign: 'left', marginTop: '1rem' }}>
                  <span>💡</span>
                  <div style={{ fontSize: '0.8rem' }}>
                    Seed the database first:{' '}
                    <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0 4px', borderRadius: 3 }}>
                      cd backend && python -m app.db.init_db
                    </code>
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(340px, 1fr))',
                gap: '1rem',
              }}
            >
              {filtered.map((asset, i) => (
                <div
                  key={asset.id}
                  className="card animate-fade-in"
                  style={{ animationDelay: `${i * 40}ms`, cursor: 'pointer' }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.75rem' }}>
                    <span className={`badge badge-${asset.status}`}>
                      {asset.status.replace('_', ' ')}
                    </span>
                    <span title={`Medical risk: ${asset.medical_risk}`}>
                      {riskIcon[asset.medical_risk]}
                    </span>
                  </div>
                  <h4 style={{ marginBottom: '0.5rem', color: 'var(--text-primary)', lineHeight: 1.3 }}>
                    {asset.title}
                  </h4>
                  {asset.summary && (
                    <p
                      className="truncate"
                      style={{
                        fontSize: '0.8rem',
                        color: 'var(--text-muted)',
                        marginBottom: '0.75rem',
                        WebkitLineClamp: 2,
                        display: '-webkit-box',
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                        whiteSpace: 'normal',
                      }}
                    >
                      {asset.summary}
                    </p>
                  )}
                  <div
                    style={{
                      display: 'flex',
                      justifyContent: 'space-between',
                      alignItems: 'center',
                      marginTop: '0.75rem',
                      paddingTop: '0.75rem',
                      borderTop: '1px solid var(--bg-border)',
                    }}
                  >
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <span className="badge badge-draft">{asset.language.toUpperCase()}</span>
                      <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                        v{asset.version}
                      </span>
                    </div>
                    <div style={{ display: 'flex', gap: '0.5rem' }}>
                      <button className="btn btn-ghost btn-sm">Edit</button>
                      <button className="btn btn-secondary btn-sm">Variants →</button>
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
