'use client';

import React from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

interface NavItem {
  href: string;
  icon: string;
  label: string;
  badge?: number;
}

const navItems: NavItem[] = [
  { href: '/dashboard', icon: '⚡', label: 'Overview' },
  { href: '/trends', icon: '📈', label: 'Trend Explorer' },
  { href: '/content', icon: '✍️', label: 'Content Studio' },
  { href: '/calendar', icon: '📅', label: 'Editorial Calendar' },
  { href: '/publishing', icon: '🚀', label: 'Publishing Center' },
  { href: '/community', icon: '💬', label: 'Community Inbox' },
  { href: '/analytics', icon: '📊', label: 'Analytics' },
  { href: '/settings', icon: '⚙️', label: 'Settings' },
];

interface SidebarProps {
  user?: { full_name: string; role: string; email: string } | null;
  operatingMode?: string;
}

export default function Sidebar({ user, operatingMode = 'demo' }: SidebarProps) {
  const pathname = usePathname();

  return (
    <aside className="sidebar">
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="logo-icon">🧬</div>
        <div>
          <div className="logo-text">Metago</div>
        </div>
        <span className="logo-badge">AI</span>
      </div>

      {/* Mode indicator */}
      <div style={{ padding: '0.75rem 1.25rem' }}>
        <div className={`mode-indicator mode-${operatingMode}`}>
          <span className="mode-dot" />
          {operatingMode.toUpperCase()} MODE
        </div>
      </div>

      {/* Navigation */}
      <nav className="nav-section">
        <div className="nav-section-label">Platform</div>
        {navItems.map((item) => (
          <Link
            key={item.href}
            href={item.href}
            className={`nav-item${pathname === item.href || pathname?.startsWith(item.href + '/') ? ' active' : ''}`}
          >
            <span className="nav-icon">{item.icon}</span>
            {item.label}
            {item.badge ? (
              <span className="nav-badge">{item.badge}</span>
            ) : null}
          </Link>
        ))}
      </nav>

      {/* User info at bottom */}
      {user && (
        <div
          style={{
            marginTop: 'auto',
            padding: '1rem 1.25rem',
            borderTop: '1px solid var(--bg-border)',
          }}
        >
          <div
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.625rem',
            }}
          >
            <div
              style={{
                width: 32,
                height: 32,
                borderRadius: '50%',
                background: 'var(--gradient-brand)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                fontSize: '0.875rem',
                fontWeight: 700,
                flexShrink: 0,
              }}
            >
              {user.full_name.charAt(0).toUpperCase()}
            </div>
            <div style={{ overflow: 'hidden' }}>
              <div
                className="truncate"
                style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)' }}
              >
                {user.full_name}
              </div>
              <div
                className="truncate"
                style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}
              >
                {user.role.replace('_', ' ')}
              </div>
            </div>
          </div>
        </div>
      )}
    </aside>
  );
}
