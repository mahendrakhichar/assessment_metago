'use client';

import React, { useState } from 'react';
import Sidebar from '@/components/Sidebar';

// ── Minimal calendar data types ──────────────────────────────────────────
interface CalendarEvent {
  id: string;
  title: string;
  platform: string;
  status: 'scheduled' | 'published' | 'draft' | 'review';
  time: string;
  day: number; // 1-31
}

const PLATFORM_ICONS: Record<string, string> = {
  youtube: '▶️',
  instagram: '📸',
  x: '𝕏',
  all: '📱',
};

const STATUS_COLORS: Record<string, string> = {
  scheduled: 'var(--brand-primary-light)',
  published: 'var(--brand-success)',
  draft: 'var(--text-muted)',
  review: 'var(--brand-warning)',
};

// Demo events seeded across the month
const DEMO_EVENTS: CalendarEvent[] = [
  { id: 'e1', title: 'GLP-1 Explainer — YouTube Short', platform: 'youtube', status: 'scheduled', time: '10:00 AM', day: 28 },
  { id: 'e2', title: 'Patient Success Story — Instagram', platform: 'instagram', status: 'scheduled', time: '12:00 PM', day: 28 },
  { id: 'e3', title: 'Myth vs Evidence Thread', platform: 'x', status: 'review', time: '03:00 PM', day: 29 },
  { id: 'e4', title: 'Metabolic Health Reel', platform: 'instagram', status: 'draft', time: '11:00 AM', day: 30 },
  { id: 'e5', title: 'Doctor FAQ Video', platform: 'youtube', status: 'published', time: '09:00 AM', day: 27 },
  { id: 'e6', title: 'Weekly Wellness Tips', platform: 'x', status: 'scheduled', time: '08:00 AM', day: 31 },
  { id: 'e7', title: 'Obesity Awareness Post', platform: 'instagram', status: 'scheduled', time: '06:00 PM', day: 31 },
];

const DAYS_OF_WEEK = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function getCalendarGrid(year: number, month: number) {
  const firstDay = new Date(year, month, 1).getDay();
  const daysInMonth = new Date(year, month + 1, 0).getDate();
  const grid: (number | null)[] = Array(firstDay).fill(null);
  for (let d = 1; d <= daysInMonth; d++) grid.push(d);
  while (grid.length % 7 !== 0) grid.push(null);
  return grid;
}

export default function CalendarPage() {
  const now = new Date();
  const [year, setYear] = useState(now.getFullYear());
  const [month, setMonth] = useState(now.getMonth());
  const [platformFilter, setPlatformFilter] = useState<string>('all');
  const [selectedDay, setSelectedDay] = useState<number | null>(now.getDate());

  const grid = getCalendarGrid(year, month);
  const monthName = new Date(year, month).toLocaleString('en-IN', { month: 'long', year: 'numeric' });

  const filteredEvents = DEMO_EVENTS.filter(
    (e) => platformFilter === 'all' || e.platform === platformFilter
  );

  const eventsForDay = (day: number) => filteredEvents.filter((e) => e.day === day);

  const selectedEvents = selectedDay ? eventsForDay(selectedDay) : [];

  const navigate = (dir: -1 | 1) => {
    let m = month + dir;
    let y = year;
    if (m < 0) { m = 11; y--; }
    if (m > 11) { m = 0; y++; }
    setMonth(m);
    setYear(y);
    setSelectedDay(null);
  };

  return (
    <div className="layout">
      <Sidebar operatingMode="demo" />
      <div className="main-content">
        <header className="topbar">
          <div style={{ flex: 1, fontWeight: 700, fontSize: '1rem', color: 'var(--text-primary)' }}>
            Editorial Calendar
          </div>
          <div className="demo-banner">🧪 Demo Mode</div>
        </header>

        <div className="page-content">
          <div className="page-header">
            <div>
              <h1 className="page-title">Editorial Calendar</h1>
              <p className="page-subtitle">Plan and track content publication across all platforms</p>
            </div>
            <button className="btn btn-primary">+ Schedule Content</button>
          </div>

          {/* Platform filter + Navigation */}
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '1.25rem' }}>
            <div style={{ display: 'flex', gap: '0.5rem' }}>
              {['all', 'youtube', 'instagram', 'x'].map((p) => (
                <button
                  key={p}
                  className={`btn ${platformFilter === p ? 'btn-primary' : 'btn-secondary'} btn-sm`}
                  onClick={() => setPlatformFilter(p)}
                >
                  {PLATFORM_ICONS[p]} {p === 'all' ? 'All' : p.charAt(0).toUpperCase() + p.slice(1)}
                </button>
              ))}
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate(-1)}>‹</button>
              <span style={{ fontWeight: 700, color: 'var(--text-primary)', fontSize: '0.95rem', minWidth: 160, textAlign: 'center' }}>
                {monthName}
              </span>
              <button className="btn btn-ghost btn-sm" onClick={() => navigate(1)}>›</button>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: '1fr 300px', gap: '1.5rem' }}>
            {/* Calendar Grid */}
            <div className="card" style={{ padding: 0, overflow: 'hidden' }}>
              {/* Day headers */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)', background: 'var(--bg-elevated)', borderBottom: '1px solid var(--bg-border)' }}>
                {DAYS_OF_WEEK.map((d) => (
                  <div key={d} style={{ padding: '0.625rem', textAlign: 'center', fontSize: '0.75rem', fontWeight: 700, color: 'var(--text-muted)' }}>
                    {d}
                  </div>
                ))}
              </div>

              {/* Day cells */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(7, 1fr)' }}>
                {grid.map((day, i) => {
                  const isToday = day === now.getDate() && month === now.getMonth() && year === now.getFullYear();
                  const isSelected = day === selectedDay;
                  const events = day ? eventsForDay(day) : [];

                  return (
                    <div
                      key={i}
                      onClick={() => day && setSelectedDay(day)}
                      style={{
                        minHeight: 90,
                        padding: '0.5rem',
                        borderRight: (i + 1) % 7 !== 0 ? '1px solid var(--bg-border)' : 'none',
                        borderBottom: '1px solid var(--bg-border)',
                        cursor: day ? 'pointer' : 'default',
                        background: isSelected
                          ? 'rgba(108, 99, 255, 0.1)'
                          : day
                          ? 'transparent'
                          : 'rgba(0,0,0,0.02)',
                        transition: 'background 0.15s',
                      }}
                    >
                      {day && (
                        <>
                          <div
                            style={{
                              width: 26,
                              height: 26,
                              borderRadius: '50%',
                              background: isToday ? 'var(--brand-primary)' : 'transparent',
                              display: 'flex',
                              alignItems: 'center',
                              justifyContent: 'center',
                              fontSize: '0.8rem',
                              fontWeight: isToday ? 700 : 400,
                              color: isToday ? 'white' : 'var(--text-secondary)',
                              marginBottom: '0.3rem',
                            }}
                          >
                            {day}
                          </div>
                          {events.slice(0, 2).map((evt) => (
                            <div
                              key={evt.id}
                              style={{
                                fontSize: '0.65rem',
                                padding: '2px 4px',
                                borderRadius: 3,
                                background: `${STATUS_COLORS[evt.status]}22`,
                                borderLeft: `2px solid ${STATUS_COLORS[evt.status]}`,
                                color: 'var(--text-secondary)',
                                marginBottom: '0.2rem',
                                overflow: 'hidden',
                                whiteSpace: 'nowrap',
                                textOverflow: 'ellipsis',
                              }}
                            >
                              {PLATFORM_ICONS[evt.platform]} {evt.title}
                            </div>
                          ))}
                          {events.length > 2 && (
                            <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)' }}>
                              +{events.length - 2} more
                            </div>
                          )}
                        </>
                      )}
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Day Detail Panel */}
            <div className="card">
              <h3 style={{ marginBottom: '1rem', color: 'var(--text-primary)', fontSize: '0.95rem' }}>
                {selectedDay
                  ? `${new Date(year, month, selectedDay).toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}`
                  : 'Select a day'}
              </h3>

              {selectedDay && selectedEvents.length === 0 && (
                <div className="empty-state" style={{ padding: '2rem 0' }}>
                  <div className="empty-icon" style={{ fontSize: '1.5rem' }}>📭</div>
                  <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textAlign: 'center' }}>
                    Nothing scheduled for this day
                  </p>
                </div>
              )}

              {selectedEvents.map((evt) => (
                <div
                  key={evt.id}
                  style={{
                    padding: '0.75rem',
                    background: 'var(--bg-elevated)',
                    borderRadius: 'var(--radius-sm)',
                    border: `1px solid ${STATUS_COLORS[evt.status]}55`,
                    borderLeft: `3px solid ${STATUS_COLORS[evt.status]}`,
                    marginBottom: '0.75rem',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '0.3rem' }}>
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{evt.time}</span>
                    <span style={{ fontSize: '0.7rem', color: STATUS_COLORS[evt.status], fontWeight: 600, textTransform: 'capitalize' }}>
                      {evt.status}
                    </span>
                  </div>
                  <div style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-primary)', marginBottom: '0.3rem' }}>
                    {evt.title}
                  </div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>
                    {PLATFORM_ICONS[evt.platform]} {evt.platform.charAt(0).toUpperCase() + evt.platform.slice(1)}
                  </div>
                </div>
              ))}

              {/* Legend */}
              <div style={{ marginTop: '1.5rem', paddingTop: '1rem', borderTop: '1px solid var(--bg-border)' }}>
                <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)', marginBottom: '0.5rem', fontWeight: 600 }}>Legend</div>
                {Object.entries(STATUS_COLORS).map(([s, c]) => (
                  <div key={s} style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.3rem' }}>
                    <div style={{ width: 10, height: 10, borderRadius: 2, background: c, flexShrink: 0 }} />
                    <span style={{ fontSize: '0.7rem', color: 'var(--text-muted)', textTransform: 'capitalize' }}>{s}</span>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
