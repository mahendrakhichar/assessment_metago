'use client';

import React, { useEffect, useState } from 'react';
import Sidebar from '@/components/Sidebar';
import { accounts } from '@/lib/api';
import type { SocialAccount } from '@/lib/api';

const PLATFORM_CONFIG = {
  youtube: { icon: '▶️', color: '#FF4444', name: 'YouTube' },
  instagram: { icon: '📸', color: '#E1306C', name: 'Instagram' },
  x: { icon: '𝕏', color: '#FFFFFF', name: 'X (Twitter)' },
};

export default function PublishingPage() {
  const [socialAccounts, setSocialAccounts] = useState<SocialAccount[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    accounts.list()
      .then(setSocialAccounts)
      .catch(() => setSocialAccounts([]))
      .finally(() => setLoading(false));
  }, []);

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Publishing Center
          </div>
          <div className="demo-banner">🧪 Demo Mode — Publishing disabled</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Publishing Center</h1>
              <p className="page-subtitle">Manage connected accounts, schedules, and publishing status</p>
            </div>
          </div>

          {/* Operating Mode Warning */}
          <div className="alert alert-warning" style={{ marginBottom: '1.5rem' }}>
            <span>⚠️</span>
            <div>
              <div style={{ fontWeight: 600, marginBottom: '0.2rem' }}>Demo Mode Active</div>
              <div style={{ fontSize: '0.8rem' }}>
                Real publishing is disabled. Switch to <strong>Assisted</strong> or <strong>Controlled</strong>{' '}
                mode in settings after configuring real API credentials.
              </div>
            </div>
          </div>

          {/* Connected Accounts */}
          <div className="card" style={{ marginBottom: '1.5rem' }}>
            <div className="card-header">
              <h3 className="card-title">🔗 Connected Social Accounts</h3>
              <button className="btn btn-secondary btn-sm">+ Connect Account</button>
            </div>

            {loading ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {[...Array(3)].map((_, i) => (
                  <div key={i} className="skeleton" style={{ height: 80, borderRadius: 'var(--radius-sm)' }} />
                ))}
              </div>
            ) : socialAccounts.length === 0 ? (
              <div className="empty-state" style={{ padding: '2rem' }}>
                <div className="empty-icon">📱</div>
                <p style={{ color: 'var(--text-muted)' }}>No accounts connected. Seed the database to see demo accounts.</p>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {socialAccounts.map((account) => {
                  const config = PLATFORM_CONFIG[account.platform as keyof typeof PLATFORM_CONFIG];
                  return (
                    <div
                      key={account.id}
                      style={{
                        display: 'flex',
                        alignItems: 'center',
                        gap: '1rem',
                        padding: '1rem',
                        background: 'var(--bg-elevated)',
                        borderRadius: 'var(--radius-sm)',
                        border: '1px solid var(--bg-border)',
                      }}
                    >
                      <div
                        style={{
                          width: 48,
                          height: 48,
                          borderRadius: 'var(--radius-sm)',
                          background: 'var(--bg-card)',
                          display: 'flex',
                          alignItems: 'center',
                          justifyContent: 'center',
                          fontSize: '1.5rem',
                          flexShrink: 0,
                          border: '1px solid var(--bg-border)',
                        }}
                      >
                        {config?.icon || '📱'}
                      </div>
                      <div style={{ flex: 1 }}>
                        <div style={{ fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
                          {account.display_name || account.account_name}
                        </div>
                        <div style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                          {config?.name || account.platform} · @{account.account_name}
                        </div>
                        {account.follower_count && (
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                            {account.follower_count.toLocaleString()} followers
                          </div>
                        )}
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                        {account.is_mock && (
                          <span
                            className="badge"
                            style={{
                              background: 'rgba(108, 99, 255, 0.15)',
                              color: 'var(--brand-primary-light)',
                            }}
                          >
                            DEMO
                          </span>
                        )}
                        <span
                          style={{
                            display: 'flex',
                            alignItems: 'center',
                            gap: '0.4rem',
                            fontSize: '0.8rem',
                            color: account.is_paused
                              ? 'var(--brand-danger)'
                              : account.health_status === 'healthy'
                              ? 'var(--brand-success)'
                              : 'var(--text-muted)',
                          }}
                        >
                          <span>{account.is_paused ? '⏸' : '●'}</span>
                          {account.is_paused ? 'PAUSED' : account.health_status}
                        </span>
                        <button className="btn btn-ghost btn-sm">
                          {account.is_paused ? 'Resume' : 'Pause'}
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

          {/* Upcoming Schedule (placeholder) */}
          <div className="card">
            <div className="card-header">
              <h3 className="card-title">📅 Upcoming Scheduled Posts</h3>
            </div>
            <div className="empty-state" style={{ padding: '3rem' }}>
              <div className="empty-icon">📤</div>
              <h3>No posts scheduled</h3>
              <p style={{ color: 'var(--text-muted)', textAlign: 'center', maxWidth: 400 }}>
                Approved content variants can be scheduled here. Posts will only be published
                after all required reviews pass.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
