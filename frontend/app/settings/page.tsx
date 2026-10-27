'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';

type Tab = 'general' | 'llm' | 'platforms' | 'compliance' | 'team';

interface SettingRow {
  label: string;
  desc: string;
  value: string;
  type: 'text' | 'select' | 'toggle';
  options?: string[];
}

const GENERAL_SETTINGS: SettingRow[] = [
  { label: 'Operating Mode', desc: 'Controls whether real publishing is active', value: 'demo', type: 'select', options: ['demo', 'assisted', 'controlled'] },
  { label: 'App Environment', desc: 'Current deployment environment', value: 'development', type: 'select', options: ['development', 'staging', 'production'] },
  { label: 'Primary Language', desc: 'Default content language', value: 'en', type: 'select', options: ['en', 'hi', 'en-IN'] },
  { label: 'Debug Mode', desc: 'Enable verbose logging and API docs', value: 'true', type: 'toggle' },
];

const LLM_SETTINGS: SettingRow[] = [
  { label: 'Default LLM Model', desc: 'Used for standard content tasks', value: 'anthropic/claude-3-haiku', type: 'select', options: ['anthropic/claude-3-haiku', 'anthropic/claude-3-5-sonnet', 'openai/gpt-4o-mini', 'google/gemini-flash-1.5'] },
  { label: 'Strong LLM Model', desc: 'Used for complex agent reasoning', value: 'anthropic/claude-3-5-sonnet', type: 'select', options: ['anthropic/claude-3-5-sonnet', 'openai/gpt-4o', 'google/gemini-pro-1.5'] },
  { label: 'Daily LLM Budget (USD)', desc: 'Maximum spend on LLM calls per day', value: '$10.00', type: 'text' },
  { label: 'Monthly LLM Budget (USD)', desc: 'Monthly cap to prevent runaway costs', value: '$200.00', type: 'text' },
];

const PLATFORM_SETTINGS: SettingRow[] = [
  { label: 'YouTube Client ID', desc: 'OAuth 2.0 client for YouTube Data API v3', value: '(not configured)', type: 'text' },
  { label: 'Instagram App ID', desc: 'Meta Business App ID', value: '(not configured)', type: 'text' },
  { label: 'X API Key', desc: 'Twitter Developer API key', value: '(not configured)', type: 'text' },
  { label: 'S3 Bucket', desc: 'Media asset storage bucket (Phase 5+)', value: 'metago-media', type: 'text' },
];

const COMPLIANCE_SETTINGS: SettingRow[] = [
  { label: 'Medical Review Gate', desc: 'HIGH/CRITICAL risk content requires human medical approval', value: 'true', type: 'toggle' },
  { label: 'AI Review Bypasses Gate', desc: 'Allows AI approvals to satisfy medical gate (NOT recommended)', value: 'false', type: 'toggle' },
  { label: 'Auto-archive Blocked Content', desc: 'Automatically archive content blocked for 30+ days', value: 'false', type: 'toggle' },
  { label: 'Audit Log Retention (days)', desc: 'How long to keep audit event records', value: '365', type: 'text' },
];

const TABS: { id: Tab; label: string; icon: string }[] = [
  { id: 'general', label: 'General', icon: '⚙️' },
  { id: 'llm', label: 'LLM / AI', icon: '🤖' },
  { id: 'platforms', label: 'Platform APIs', icon: '🔌' },
  { id: 'compliance', label: 'Compliance', icon: '🏥' },
  { id: 'team', label: 'Team & Roles', icon: '👥' },
];

const TAB_DATA: Record<Exclude<Tab, 'team'>, { title: string; desc: string; rows: SettingRow[] }> = {
  general: { title: 'General Settings', desc: 'Operating mode, environment, and application defaults.', rows: GENERAL_SETTINGS },
  llm: { title: 'LLM & AI Configuration', desc: 'Model selection and cost budgets for AI operations.', rows: LLM_SETTINGS },
  platforms: { title: 'Platform API Credentials', desc: 'OAuth credentials for social platform integrations. Stored encrypted at rest.', rows: PLATFORM_SETTINGS },
  compliance: { title: 'Compliance & Medical Safety', desc: 'Medical gate configuration and content governance rules.', rows: COMPLIANCE_SETTINGS },
};

function SettingField({ row }: { row: SettingRow }) {
  const [val, setVal] = useState(row.value);

  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        padding: '1rem 0',
        borderBottom: '1px solid var(--bg-border)',
      }}
    >
      <div style={{ flex: 1, paddingRight: '2rem' }}>
        <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)', marginBottom: '0.2rem' }}>
          {row.label}
        </div>
        <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{row.desc}</div>
      </div>
      <div style={{ flexShrink: 0 }}>
        {row.type === 'toggle' ? (
          <button
            onClick={() => setVal(v => v === 'true' ? 'false' : 'true')}
            style={{
              width: 48,
              height: 26,
              borderRadius: 13,
              border: 'none',
              background: val === 'true' ? 'var(--brand-primary)' : 'var(--bg-elevated)',
              cursor: 'pointer',
              position: 'relative',
              transition: 'background 0.2s',
              outline: '1px solid var(--bg-border)',
            }}
          >
            <span
              style={{
                position: 'absolute',
                top: 3,
                left: val === 'true' ? 25 : 3,
                width: 20,
                height: 20,
                borderRadius: '50%',
                background: 'white',
                transition: 'left 0.2s',
                boxShadow: '0 1px 3px rgba(0,0,0,0.3)',
              }}
            />
          </button>
        ) : row.type === 'select' && row.options ? (
          <select
            value={val}
            onChange={(e) => setVal(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--bg-border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              padding: '0.375rem 0.625rem',
              fontSize: '0.8rem',
              outline: 'none',
              cursor: 'pointer',
            }}
          >
            {row.options.map((o) => (
              <option key={o} value={o}>{o}</option>
            ))}
          </select>
        ) : (
          <input
            type="text"
            value={val}
            onChange={(e) => setVal(e.target.value)}
            style={{
              background: 'var(--bg-elevated)',
              border: '1px solid var(--bg-border)',
              borderRadius: 'var(--radius-sm)',
              color: 'var(--text-primary)',
              padding: '0.375rem 0.625rem',
              fontSize: '0.8rem',
              outline: 'none',
              width: 200,
            }}
          />
        )}
      </div>
    </div>
  );
}

const TEAM_ROLES = [
  { email: 'admin@metago.in', name: 'Metago Admin', role: 'SUPER_ADMIN', status: 'active' },
  { email: 'dr.sharma@metago.in', name: 'Dr. Priya Sharma', role: 'MEDICAL_REVIEWER', status: 'pending' },
  { email: 'content@metago.in', name: 'Content Team', role: 'CONTENT_MANAGER', status: 'active' },
  { email: 'analyst@metago.in', name: 'Analytics Team', role: 'ANALYST', status: 'active' },
];

const ROLE_COLORS: Record<string, string> = {
  SUPER_ADMIN: 'var(--brand-primary-light)',
  ADMIN: 'var(--brand-primary)',
  MEDICAL_REVIEWER: 'var(--brand-success)',
  CONTENT_MANAGER: 'var(--brand-warning)',
  ANALYST: 'var(--text-secondary)',
  VIEWER: 'var(--text-muted)',
};

export default function SettingsPage() {
  const [activeTab, setActiveTab] = useState<Tab>('general');

  const tabData = activeTab !== 'team' ? TAB_DATA[activeTab as Exclude<Tab, 'team'>] : null;

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Settings
          </div>
          <div className="demo-banner">🧪 Demo Mode</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Platform Settings</h1>
              <p className="page-subtitle">Configure operating mode, API credentials, and compliance rules</p>
            </div>
            <button className="btn btn-primary">💾 Save Changes</button>
          </div>

          <div className="alert alert-warning" style={{ marginBottom: '1.5rem' }}>
            <span>⚠️</span>
            <div style={{ fontSize: '0.8rem' }}>
              Settings changes take effect on server restart. In Demo mode, changes here are for preview only —
              they do not modify the running <code style={{ background: 'rgba(0,0,0,0.3)', padding: '0 4px', borderRadius: 3 }}>.env</code> file.
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '200px 1fr', gap: '1.5rem' }}>
            {/* Tab Nav */}
            <div className="card" style={{ padding: '0.5rem', height: 'fit-content' }}>
              {TABS.map((tab) => (
                <button
                  key={tab.id}
                  onClick={() => setActiveTab(tab.id)}
                  style={{
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.625rem',
                    width: '100%',
                    padding: '0.625rem 0.75rem',
                    borderRadius: 'var(--radius-sm)',
                    border: 'none',
                    background: activeTab === tab.id ? 'rgba(108, 99, 255, 0.15)' : 'transparent',
                    color: activeTab === tab.id ? 'var(--brand-primary-light)' : 'var(--text-secondary)',
                    fontSize: '0.8rem',
                    fontWeight: activeTab === tab.id ? 600 : 400,
                    cursor: 'pointer',
                    textAlign: 'left',
                    transition: 'all 0.15s',
                  }}
                >
                  <span>{tab.icon}</span>
                  {tab.label}
                </button>
              ))}
            </div>

            {/* Tab Content */}
            <div className="card">
              {tabData ? (
                <>
                  <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                    {tabData.title}
                  </h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                    {tabData.desc}
                  </p>
                  {tabData.rows.map((row) => (
                    <SettingField key={row.label} row={row} />
                  ))}
                </>
              ) : (
                /* Team tab */
                <>
                  <h2 style={{ fontSize: '1rem', fontWeight: 700, color: 'var(--text-primary)', marginBottom: '0.25rem' }}>
                    Team &amp; Role Management
                  </h2>
                  <p style={{ fontSize: '0.8rem', color: 'var(--text-muted)', marginBottom: '1.25rem' }}>
                    Manage team member access and role assignments.
                  </p>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                    {TEAM_ROLES.map((member) => (
                      <div
                        key={member.email}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '1rem',
                          padding: '0.875rem',
                          background: 'var(--bg-elevated)',
                          borderRadius: 'var(--radius-sm)',
                          border: '1px solid var(--bg-border)',
                        }}
                      >
                        <div
                          style={{
                            width: 36,
                            height: 36,
                            borderRadius: '50%',
                            background: 'var(--gradient-brand)',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontWeight: 700,
                            fontSize: '0.875rem',
                            color: 'white',
                            flexShrink: 0,
                          }}
                        >
                          {member.name.charAt(0)}
                        </div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--text-primary)' }}>
                            {member.name}
                          </div>
                          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>{member.email}</div>
                        </div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
                          <span
                            style={{
                              fontSize: '0.7rem',
                              padding: '2px 8px',
                              borderRadius: 99,
                              border: `1px solid ${ROLE_COLORS[member.role] ?? 'var(--text-muted)'}`,
                              color: ROLE_COLORS[member.role] ?? 'var(--text-muted)',
                              fontWeight: 600,
                            }}
                          >
                            {member.role.replace('_', ' ')}
                          </span>
                          <span
                            style={{
                              fontSize: '0.7rem',
                              color: member.status === 'active' ? 'var(--brand-success)' : 'var(--brand-warning)',
                            }}
                          >
                            ● {member.status}
                          </span>
                          <button className="btn btn-ghost btn-sm" style={{ fontSize: '0.75rem' }}>
                            Edit
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                  <div style={{ marginTop: '1.25rem' }}>
                    <button className="btn btn-primary btn-sm">+ Invite Team Member</button>
                  </div>
                </>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
