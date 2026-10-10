import { useState, useEffect, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';
import { useTheme } from '../context/ThemeContext';

const DAYS = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];
const PERIODS = ['P1', 'P2', 'P3', 'P4', 'P5'];

// Convert "HH:MM" 24h to "h:MM AM/PM"
const to12hr = (time24) => {
  if (!time24) return '';
  const [hStr, mStr] = time24.split(':');
  let h = parseInt(hStr, 10);
  const m = mStr || '00';
  const ampm = h >= 12 ? 'PM' : 'AM';
  h = h % 12 || 12;
  return `${h}:${m} ${ampm}`;
};

const YEAR_LABELS = { '1': '1st Year', '2': '2nd Year', '3': '3rd Year' };
const YEAR_FULL = { '1': '1st Year', '2': '2nd Year', '3': '3rd Year' };
const YEAR_ICONS = { '1': '🎓', '2': '🚀', '3': '🏆' };

const makeTheme = (isDark) => ({
  acc: '#7C3AED', accLight: isDark ? '#9F67FF' : '#6D28D9',
  grad: 'linear-gradient(135deg, #7C3AED 0%, #EC4899 100%)',
  gradHover: 'linear-gradient(135deg, #6D28D9 0%, #DB2777 100%)',
  bg: isDark ? '#080810' : '#F4F3FF',
  surface: isDark ? '#0F0F1A' : '#FFFFFF',
  surface2: isDark ? '#161625' : '#F0EEFF',
  surface3: isDark ? '#1C1C2E' : '#E9E5FF',
  border: isDark ? 'rgba(124,58,237,0.18)' : 'rgba(124,58,237,0.2)',
  borderStrong: isDark ? 'rgba(124,58,237,0.4)' : 'rgba(124,58,237,0.5)',
  textPrimary: isDark ? '#FFFFFF' : '#0A0A1A',
  textSec: isDark ? 'rgba(255,255,255,0.55)' : 'rgba(10,10,26,0.6)',
  textMuted: isDark ? 'rgba(255,255,255,0.3)' : 'rgba(10,10,26,0.4)',
  navBg: isDark ? 'rgba(8,8,16,0.85)' : 'rgba(255,255,255,0.92)',
  inputBg: isDark ? '#1C1C2E' : '#FFFFFF',
  cardShadow: isDark ? '0 8px 32px rgba(0,0,0,0.4)' : '0 8px 32px rgba(124,58,237,0.08)',
});

// ─── Toast ───────────────────────────────────────────────────────────────────
function Toast({ toasts }) {
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  return (
    <div style={{ position: 'fixed', bottom: 24, right: 24, zIndex: 9999, display: 'flex', flexDirection: 'column', gap: 12 }}>
      {toasts.map(t => (
        <div key={t.id} style={{
          background: s.surface2, border: `1px solid ${t.type === 'success' ? '#10B981' : '#EF4444'}`,
          borderLeft: `4px solid ${t.type === 'success' ? '#10B981' : '#EF4444'}`,
          color: s.textPrimary, padding: '14px 20px', borderRadius: 12, fontSize: '0.88rem', fontWeight: 600,
          display: 'flex', alignItems: 'center', gap: 10, boxShadow: '0 10px 40px rgba(0,0,0,0.6)',
          animation: 'slideIn 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          backdropFilter: 'blur(12px)', maxWidth: 360,
        }}>
          <span style={{ fontSize: '1.1rem' }}>{t.type === 'success' ? '✅' : '❌'}</span>
          <span>{t.text}</span>
        </div>
      ))}
    </div>
  );
}

// ─── Student List Modal ──────────────────────────────────────────────────────
function StudentListModal({ title, subtitle, icon, students, color, onClose }) {
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9998,
      background: 'rgba(0,0,0,0.82)', backdropFilter: 'blur(16px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }} onClick={onClose}>
      <div style={{
        background: s.surface, border: `1px solid ${s.border}`,
        borderRadius: 24, padding: '36px 32px', maxWidth: 520, width: '100%',
        boxShadow: '0 32px 80px rgba(0,0,0,0.8)', position: 'relative',
        animation: 'modalIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
        maxHeight: '80vh', overflowY: 'auto',
      }} onClick={e => e.stopPropagation()}>
        <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: color, borderRadius: '24px 24px 0 0' }} />
        <button onClick={onClose} style={{
          position: 'absolute', top: 16, right: 16, background: theme === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
          border: `1px solid ${s.border}`, borderRadius: '50%',
          width: 34, height: 34, cursor: 'pointer', color: s.textSec,
          fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>✕</button>
        <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 8 }}>
          <div style={{
            width: 48, height: 48, borderRadius: 14, background: 'rgba(124,58,237,0.12)',
            border: `1px solid ${s.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center',
            fontSize: '1.5rem',
          }}>{icon}</div>
          <div>
            <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.2rem', fontWeight: 800, color: s.textPrimary }}>{title}</div>
            <div style={{ fontSize: '0.78rem', color: s.textSec }}>{subtitle}</div>
          </div>
        </div>
        <div style={{
          display: 'inline-flex', alignItems: 'center', gap: 6, marginBottom: 20,
          background: 'rgba(124,58,237,0.1)', border: `1px solid ${s.border}`,
          borderRadius: 99, padding: '4px 14px',
          fontSize: '0.75rem', fontWeight: 700, color: s.accLight,
        }}>
          {students.length} student{students.length !== 1 ? 's' : ''} found
        </div>
        {students.length === 0 ? (
          <div style={{ textAlign: 'center', padding: '32px 0', color: s.textSec }}>
            <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>🎉</div>
            <div style={{ fontWeight: 600 }}>No students in this category</div>
          </div>
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
            {students.map((st, i) => (
              <div key={i} style={{
                background: s.surface2, border: `1px solid ${s.border}`, borderRadius: 14,
                padding: '14px 18px', display: 'flex', alignItems: 'center', gap: 14,
                transition: 'border-color 0.2s',
              }}
                onMouseEnter={e => e.currentTarget.style.borderColor = s.borderStrong}
                onMouseLeave={e => e.currentTarget.style.borderColor = s.border}
              >
                <div style={{
                  width: 36, height: 36, borderRadius: '50%',
                  background: s.grad, display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '0.85rem', color: '#fff',
                  flexShrink: 0,
                }}>{(st.name || 'S')[0].toUpperCase()}</div>
                <div style={{ flex: 1 }}>
                  <div style={{ fontWeight: 700, fontSize: '0.92rem', color: s.textPrimary }}>{st.name}</div>
                  <div style={{ fontSize: '0.72rem', color: s.textSec, fontFamily: 'monospace', marginTop: 1 }}>{st.regno}</div>
                </div>
              </div>
            ))}
          </div>
        )}
        <style>{`@keyframes modalIn { from { transform: scale(0.88) translateY(20px); opacity:0; } to { transform: scale(1) translateY(0); opacity:1; } }`}</style>
      </div>
    </div>
  );
}

// ─── Weak % Bar ────────────────────────────────────────────────────────────────
function WeakPercentBar({ total, weak }) {
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  const pct = total > 0 ? Math.round((weak / total) * 100) : 0;
  const color = pct >= 50 ? '#EF4444' : pct >= 30 ? '#F59E0B' : '#10B981';
  return (
    <div style={{
      background: s.surface, border: `1px solid ${s.border}`, borderRadius: 18, padding: '20px 24px',
      boxShadow: s.cardShadow, marginBottom: 28,
      position: 'relative', overflow: 'hidden',
    }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: `linear-gradient(90deg, ${color}, transparent)` }} />
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 12 }}>
        <div>
          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: s.textSec, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 3 }}>Overall Weak Percentage</div>
          <div style={{ fontSize: '0.82rem', color: s.textMuted }}>Students scoring below 50% in this year</div>
        </div>
        <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '2.2rem', fontWeight: 900, color }}>{pct}%</div>
      </div>
      <div style={{ height: 10, background: theme === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)', borderRadius: 99, overflow: 'hidden' }}>
        <div style={{
          height: '100%', width: `${pct}%`, background: `linear-gradient(90deg, ${color}, ${color}aa)`,
          borderRadius: 99, transition: 'width 0.8s cubic-bezier(0.16,1,0.3,1)',
          boxShadow: `0 0 12px ${color}55`,
        }} />
      </div>
      <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 8 }}>
        <span style={{ fontSize: '0.68rem', color: s.textMuted }}>{weak} weak of {total} total students</span>
        <span style={{ fontSize: '0.68rem', color, fontWeight: 700 }}>
          {pct >= 50 ? '🔴 Critical' : pct >= 30 ? '🟡 Moderate' : '🟢 Healthy'}
        </span>
      </div>
    </div>
  );
}

// ─── Metric Card ─────────────────────────────────────────────────────────────
function MetricCard({ label, value, desc, color, onClick, clickable }) {
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  const accentColor = color || s.grad;
  return (
    <div
      onClick={onClick}
      style={{
        background: s.surface, border: `1px solid ${s.border}`, borderRadius: 18, padding: '24px 28px',
        boxShadow: s.cardShadow, position: 'relative', overflow: 'hidden',
        transition: 'transform 0.3s, border-color 0.3s, box-shadow 0.3s',
        cursor: clickable ? 'pointer' : 'default',
      }}
      onMouseEnter={e => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.borderColor = s.borderStrong;
        if (clickable) e.currentTarget.style.boxShadow = '0 16px 48px rgba(124,58,237,0.2)';
      }}
      onMouseLeave={e => {
        e.currentTarget.style.transform = '';
        e.currentTarget.style.borderColor = s.border;
        e.currentTarget.style.boxShadow = s.cardShadow;
      }}>
      <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: accentColor }} />
      <div style={{ fontSize: '0.7rem', fontWeight: 700, color: s.textSec, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 10 }}>{label}</div>
      <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '2.6rem', fontWeight: 900, lineHeight: 1, marginBottom: 8, background: accentColor, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>{value}</div>
      <div style={{ fontSize: '0.8rem', color: s.textMuted, lineHeight: 1.4 }}>{desc}</div>
      {clickable && (
        <div style={{
          position: 'absolute', bottom: 14, right: 14,
          fontSize: '0.65rem', fontWeight: 700, color: s.accLight,
          background: 'rgba(124,58,237,0.1)', border: `1px solid ${s.border}`,
          padding: '3px 9px', borderRadius: 99,
        }}>View List →</div>
      )}
    </div>
  );
}

// ─── Manual Question Form (per-question entry) ────────────────────────────────
function QuestionForm({ qIndex, total, qType, typeLabel, typeIcon, s, theme, onAdd, onCancel }) {
  const initDraft = () => {
    if (qType === 'MCQ') return { type: 'MCQ', q: '', a: '', options: ['', '', '', ''] };
    if (qType === 'TF') return { type: 'TF', q: '', a: 'True', options: ['True', 'False'] };
    if (qType === 'SHORT') return { type: 'SHORT', q: '', a: '', options: null };
    return { type: 'FILL', q: '', a: '', options: null };
  };
  const [draft, setDraft] = useState(initDraft);

  // Reset draft when question index OR type changes (moving to any next/prev question)
  useEffect(() => { setDraft(initDraft()); }, [qType, qIndex]); // eslint-disable-line

  const inputStyle = {
    background: s.surface3, border: `1px solid ${s.border}`, color: s.textPrimary,
    padding: '11px 14px', borderRadius: 10, fontSize: '0.88rem',
    fontFamily: "'Inter', sans-serif", outline: 'none', width: '100%',
    boxSizing: 'border-box', transition: 'border-color 0.2s',
  };

  const handleSubmit = () => {
    if (!draft.q.trim()) return alert('Please enter the question.');
    if (qType === 'MCQ') {
      if (draft.options.some(o => !o.trim())) return alert('Please fill all 4 options.');
      if (!draft.a.trim()) return alert('Please select the correct answer.');
      if (!draft.options.includes(draft.a)) return alert('Correct answer must be one of the options.');
    }
    if (qType === 'FILL' && !draft.a.trim()) return alert('Please enter the correct answer.');
    if (qType === 'SHORT' && !draft.a.trim()) return alert('Please enter the model answer.');
    onAdd({ ...draft });
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 18 }}>
      {/* Question type badge */}
      <div style={{
        display: 'inline-flex', alignItems: 'center', gap: 8,
        background: 'rgba(124,58,237,0.1)', border: `1px solid rgba(124,58,237,0.3)`,
        borderRadius: 99, padding: '6px 16px', alignSelf: 'flex-start',
      }}>
        <span style={{ fontSize: '1rem' }}>{typeIcon[qType]}</span>
        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: '#7C3AED' }}>
          Question {qIndex + 1} of {total} — {typeLabel[qType]}
        </span>
      </div>

      {/* Question text */}
      <div>
        <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 7 }}>
          Question
        </label>
        <textarea
          rows={3}
          placeholder={
            qType === 'FILL' ? 'Write sentence with ______ for the blank...' :
              qType === 'SHORT' ? 'Type your short-answer question here...' :
                'Type your question here...'
          }
          value={draft.q}
          onChange={e => setDraft(d => ({ ...d, q: e.target.value }))}
          style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.5 }}
        />
      </div>

      {/* MCQ options */}
      {qType === 'MCQ' && (
        <div>
          <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 10 }}>
            Answer Options
          </label>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
            {['A', 'B', 'C', 'D'].map((opt, oi) => (
              <div key={oi} style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <div style={{
                  width: 30, height: 30, borderRadius: '50%', flexShrink: 0,
                  background: draft.a === draft.options[oi] && draft.options[oi] ? 'rgba(124,58,237,0.8)' : s.surface3,
                  border: `2px solid ${draft.a === draft.options[oi] && draft.options[oi] ? '#7C3AED' : s.border}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '0.75rem', fontWeight: 800,
                  color: draft.a === draft.options[oi] && draft.options[oi] ? '#fff' : s.textSec,
                  cursor: draft.options[oi] ? 'pointer' : 'default',
                  transition: 'all 0.15s',
                }}
                  onClick={() => { if (draft.options[oi]) setDraft(d => ({ ...d, a: d.options[oi] })); }}
                >{opt}</div>
                <input
                  type="text"
                  placeholder={`Option ${opt}`}
                  value={draft.options[oi]}
                  onChange={e => {
                    const newOpts = [...draft.options];
                    newOpts[oi] = e.target.value;
                    setDraft(d => ({
                      ...d,
                      options: newOpts,
                      a: d.a === d.options[oi] ? e.target.value : d.a,
                    }));
                  }}
                  style={inputStyle}
                />
                {draft.options[oi] && (
                  <button
                    type="button"
                    onClick={() => setDraft(d => ({ ...d, a: d.options[oi] }))}
                    style={{
                      flexShrink: 0, padding: '6px 12px', fontSize: '0.65rem', fontWeight: 700,
                      borderRadius: 8, cursor: 'pointer', fontFamily: 'inherit',
                      background: draft.a === draft.options[oi] ? 'rgba(16,185,129,0.15)' : 'transparent',
                      border: `1px solid ${draft.a === draft.options[oi] ? '#10B981' : s.border}`,
                      color: draft.a === draft.options[oi] ? '#10B981' : s.textSec,
                      transition: 'all 0.15s',
                    }}
                  >{draft.a === draft.options[oi] ? '✓ Correct' : 'Set Correct'}</button>
                )}
              </div>
            ))}
          </div>
          {draft.a && (
            <div style={{ marginTop: 10, fontSize: '0.72rem', color: '#10B981', fontWeight: 700 }}>
              ✓ Correct answer: {draft.a}
            </div>
          )}
        </div>
      )}

      {/* TF answer chooser */}
      {qType === 'TF' && (
        <div>
          <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 10 }}>
            Correct Answer
          </label>
          <div style={{ display: 'flex', gap: 12 }}>
            {['True', 'False'].map(tf => (
              <button
                key={tf}
                type="button"
                onClick={() => setDraft(d => ({ ...d, a: tf }))}
                style={{
                  flex: 1, padding: '12px', borderRadius: 12, cursor: 'pointer',
                  fontWeight: 800, fontSize: '0.9rem', fontFamily: 'inherit',
                  background: draft.a === tf
                    ? (tf === 'True' ? 'rgba(16,185,129,0.15)' : 'rgba(239,68,68,0.15)')
                    : s.surface3,
                  border: `2px solid ${draft.a === tf
                    ? (tf === 'True' ? '#10B981' : '#EF4444')
                    : s.border}`,
                  color: draft.a === tf ? (tf === 'True' ? '#10B981' : '#EF4444') : s.textSec,
                  transition: 'all 0.15s',
                }}
              >{tf === 'True' ? '✅ True' : '❌ False'}</button>
            ))}
          </div>
        </div>
      )}

      {/* Fill in the blank answer */}
      {qType === 'FILL' && (
        <div>
          <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 7 }}>
            Correct Answer (fill word/phrase)
          </label>
          <input
            type="text"
            placeholder="e.g. compilation, recursion, binary tree..."
            value={draft.a}
            onChange={e => setDraft(d => ({ ...d, a: e.target.value }))}
            style={inputStyle}
          />
        </div>
      )}

      {/* Short Answer — model answer textarea */}
      {qType === 'SHORT' && (
        <div>
          <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 7 }}>
            Model Answer
          </label>
          <div style={{ fontSize: '0.68rem', color: s.textMuted, marginBottom: 6 }}>
            Write the expected answer. Students' answers will be compared against this.
          </div>
          <textarea
            rows={4}
            placeholder="Type the expected/model answer here..."
            value={draft.a}
            onChange={e => setDraft(d => ({ ...d, a: e.target.value }))}
            style={{ ...inputStyle, resize: 'vertical', lineHeight: 1.55 }}
          />
        </div>
      )}

      {/* Actions */}
      <div style={{ display: 'flex', gap: 12, marginTop: 4 }}>
        <button
          type="button"
          onClick={onCancel}
          style={{
            flex: 1, padding: '12px', borderRadius: 12, cursor: 'pointer',
            background: s.surface3, border: `1px solid ${s.border}`,
            color: s.textSec, fontWeight: 700, fontSize: '0.88rem', fontFamily: 'inherit',
          }}
        >← Back</button>
        <button
          type="button"
          onClick={handleSubmit}
          style={{
            flex: 2, padding: '12px', borderRadius: 12, cursor: 'pointer',
            background: 'linear-gradient(135deg,#7C3AED,#EC4899)', border: 'none',
            color: '#fff', fontWeight: 800, fontSize: '0.92rem', fontFamily: 'inherit',
          }}
        >Add Question →</button>
      </div>
    </div>
  );
}

// ─── Sidebar Timetable View ───────────────────────────────────────────────────
function SidebarTimetable({ timetable, year, editMode, setTimetable, onSave, saving }) {
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  const inputBase = {
    background: 'transparent', border: 'none', color: s.textPrimary,
    width: '100%', fontFamily: "'Inter', sans-serif", outline: 'none', padding: '1px 0',
  };

  if (!editMode) {
    // Professional read-only view
    return (
      <div style={{ overflowX: 'auto', borderRadius: 12, border: `1px solid ${s.border}`, background: s.surface2 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 240 }}>
          <thead>
            <tr style={{ background: 'rgba(124,58,237,0.12)' }}>
              <th style={{
                fontSize: '0.62rem', color: s.textMuted, fontWeight: 800, textAlign: 'center',
                padding: '8px 6px', textTransform: 'uppercase', letterSpacing: '0.08em',
                borderBottom: `1px solid ${s.border}`, borderRight: `1px solid ${s.border}`,
                whiteSpace: 'nowrap',
              }}>Per \ Day</th>
              {DAYS.map(d => (
                <th key={d} style={{
                  fontSize: '0.65rem', color: '#fff', fontWeight: 800, textAlign: 'center',
                  padding: '8px 4px', textTransform: 'uppercase', letterSpacing: '0.06em',
                  borderBottom: `1px solid ${s.border}`,
                  borderRight: `1px solid rgba(124,58,237,0.1)`,
                }}>{d}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PERIODS.map((p, pi) => (
              <tr key={p} style={{ background: pi % 2 === 0 ? 'transparent' : 'rgba(124,58,237,0.03)' }}>
                <td style={{
                  background: 'rgba(124,58,237,0.1)', textAlign: 'center',
                  fontSize: '0.62rem', fontWeight: 800, color: s.accLight, padding: '8px 6px',
                  borderRight: `1px solid ${s.border}`,
                  borderBottom: pi < PERIODS.length - 1 ? `1px solid rgba(124,58,237,0.08)` : 'none',
                  whiteSpace: 'nowrap',
                }}>{p}</td>
                {DAYS.map((d, di) => {
                  const key = `${d}-${p}`;
                  const cell = timetable[key];
                  const isLast = di === DAYS.length - 1;
                  return (
                    <td key={d} style={{
                      borderRight: isLast ? 'none' : `1px solid rgba(124,58,237,0.08)`,
                      borderBottom: pi < PERIODS.length - 1 ? `1px solid rgba(124,58,237,0.06)` : 'none',
                      padding: '6px 5px', verticalAlign: 'top', minWidth: 56,
                    }}>
                      {cell?.subject ? (
                        <div style={{
                          background: 'rgba(124,58,237,0.08)', borderRadius: 6,
                          border: `1px solid rgba(124,58,237,0.18)`,
                          padding: '5px 5px',
                        }}>
                          <div style={{ fontSize: '0.6rem', fontWeight: 800, color: s.accLight, lineHeight: 1.3, marginBottom: 2 }} title={cell.subject}>
                            {cell.subject.length > 8 ? cell.subject.slice(0, 8) + '…' : cell.subject}
                          </div>
                          {cell.topic && (
                            <div style={{ fontSize: '0.52rem', color: s.textSec, lineHeight: 1.3 }} title={cell.topic}>
                              {cell.topic.length > 9 ? cell.topic.slice(0, 9) + '…' : cell.topic}
                            </div>
                          )}
                        </div>
                      ) : (
                        <div style={{ fontSize: '0.55rem', color: s.textMuted, textAlign: 'center', padding: '4px 0' }}>–</div>
                      )}
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // Edit mode — professional
  return (
    <div>
      <div style={{ overflowX: 'auto', borderRadius: 12, border: `1px solid ${s.border}`, background: s.surface2 }}>
        <table style={{ width: '100%', borderCollapse: 'collapse', minWidth: 240 }}>
          <thead>
            <tr style={{ background: 'rgba(124,58,237,0.12)' }}>
              <th style={{ fontSize: '0.62rem', color: s.textMuted, fontWeight: 800, textAlign: 'center', padding: '8px 6px', textTransform: 'uppercase', letterSpacing: '0.08em', borderBottom: `1px solid ${s.border}`, borderRight: `1px solid ${s.border}` }}></th>
              {DAYS.map(d => (
                <th key={d} style={{ fontSize: '0.65rem', color: s.textPrimary, fontWeight: 800, textAlign: 'center', padding: '8px 4px', textTransform: 'uppercase', letterSpacing: '0.06em', borderBottom: `1px solid ${s.border}`, borderRight: `1px solid rgba(124,58,237,0.1)` }}>{d}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {PERIODS.map((p, pi) => (
              <tr key={p}>
                <td style={{ background: 'rgba(124,58,237,0.1)', textAlign: 'center', fontSize: '0.62rem', fontWeight: 800, color: s.accLight, padding: '6px 4px', borderRight: `1px solid ${s.border}`, borderBottom: pi < PERIODS.length - 1 ? `1px solid rgba(124,58,237,0.08)` : 'none', whiteSpace: 'nowrap' }}>{p}</td>
                {DAYS.map((d, di) => {
                  const key = `${d}-${p}`;
                  const isLast = di === DAYS.length - 1;
                  return (
                    <td key={d} style={{ background: s.surface3, borderRight: isLast ? 'none' : `1px solid rgba(124,58,237,0.1)`, borderBottom: pi < PERIODS.length - 1 ? `1px solid rgba(124,58,237,0.08)` : 'none', padding: '5px', verticalAlign: 'top', minWidth: 52 }}>
                      <input type="text" placeholder="Subj" value={timetable[key]?.subject || ''}
                        onChange={e => setTimetable(t => ({ ...t, [key]: { ...(t[key] || {}), subject: e.target.value } }))}
                        style={{ ...inputBase, fontSize: '0.58rem', fontWeight: 700, color: s.accLight, borderBottom: `1px dashed rgba(124,58,237,0.3)`, marginBottom: 3, paddingBottom: 2 }} />
                      <input type="text" placeholder="Topic" value={timetable[key]?.topic || ''}
                        onChange={e => setTimetable(t => ({ ...t, [key]: { ...(t[key] || {}), topic: e.target.value } }))}
                        style={{ ...inputBase, fontSize: '0.52rem', color: s.textSec }} />
                    </td>
                  );
                })}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
      <button onClick={onSave} disabled={saving}
        style={{
          marginTop: 10, width: '100%', background: saving ? s.surface3 : s.grad, color: '#fff', border: 'none',
          borderRadius: 8, padding: '11px', fontWeight: 700, fontSize: '0.82rem', cursor: saving ? 'not-allowed' : 'pointer',
          fontFamily: 'inherit', opacity: saving ? 0.7 : 1, transition: 'opacity 0.2s',
          display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
        }}>
        {saving ? '⌛ Saving…' : '💾 Save Timetable'}
      </button>
    </div>
  );
}

// ─── Main Component ───────────────────────────────────────────────────────────
export default function MentorDashboardPage() {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const s = makeTheme(theme === 'dark');
  const [year, setYear] = useState(() => sessionStorage.getItem('mentor_selected_year') || null);
  const [students, setStudents] = useState([]);
  const [metrics, setMetrics] = useState({ total: 0, weak: 0, missed: 0 });
  const [toasts, setToasts] = useState([]);
  const [timetable, setTimetable] = useState({});
  const [timetableEditMode, setTimetableEditMode] = useState(false);
  const [savingTimetable, setSavingTimetable] = useState(false);
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [timetableModal, setTimetableModal] = useState(false);
  const [overrideForm, setOverrideForm] = useState({ subject: '', topic: '', mcq: 0, tf: 0, fill: 0, shortanswer: 0, dueDate: new Date().toISOString().split('T')[0], dueTime: '00:00' });
  const [submitting, setSubmitting] = useState(false);
  const [availableSubjects, setAvailableSubjects] = useState([]);
  const [timetableTopics, setTimetableTopics] = useState([]);
  const [yearSubjects, setYearSubjects] = useState([]);
  const [todayActive, setTodayActive] = useState(null);
  const [actionLoading, setActionLoading] = useState(null);
  const [loadingCohort, setLoadingCohort] = useState(false);
  const [modal, setModal] = useState(null); // null | 'weak' | 'missed'
  const [historyTab, setHistoryTab] = useState('performance'); // 'performance' | 'history'
  const [topicHistory, setTopicHistory] = useState([]);
  const [topicPerformance, setTopicPerformance] = useState(null);
  const [selectedHistoryItem, setSelectedHistoryItem] = useState(null);
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [loadingPerf, setLoadingPerf] = useState(false);
  const [sendingReport, setSendingReport] = useState(false);
  const [showHistory, setShowHistory] = useState(false);
  const [weakReportData, setWeakReportData] = useState(null); // null | { total_weak, students[] }
  const [showWeakReport, setShowWeakReport] = useState(false);
  const [historyYear, setHistoryYear] = useState(null); // track which year's history is shown
  const [historyCleared, setHistoryCleared] = useState(false); // UI-only cleared state
  const [clearingHistory, setClearingHistory] = useState(false); // API delete in progress
  const [quizPreview, setQuizPreview] = useState(null);   // { historyId, questions[], generatedBy } — Fix #4
  const [loadingQuizPreview, setLoadingQuizPreview] = useState(null); // historyId being loaded
  const [quizAnswerModal, setQuizAnswerModal] = useState(null); // { student, data } — mentor views student Q&A
  const [loadingAnswers, setLoadingAnswers] = useState(null); // regno being loaded
  const [expandedStudents, setExpandedStudents] = useState({}); // { regno: true/false }
  const [showAllStudents, setShowAllStudents] = useState(false); // all students list modal
  const [qModeModal, setQModeModal] = useState(false);       // question mode chooser modal
  const [qBuilderModal, setQBuilderModal] = useState(false); // manual question builder modal
  const [manualQuestions, setManualQuestions] = useState([]); // mentor-created questions

  const mentorName = sessionStorage.getItem('mentorName') || 'Professor';
  const mentorToken = sessionStorage.getItem('mentorToken');
  const isReturningMentor = sessionStorage.getItem('mentorIsReturning') === '1';

  /* Auth guard */
  useEffect(() => {
    if (sessionStorage.getItem('userRole') !== 'mentor') {
      alert('Access Denied. Please log in as a mentor.');
      navigate('/mentor-login');
    }
  }, [navigate]);

  const addToast = useCallback((text, type = 'success') => {
    const id = Date.now();
    setToasts(ts => [...ts, { id, text, type }]);
    setTimeout(() => setToasts(ts => ts.filter(t => t.id !== id)), 4000);
  }, []);

  const authHeaders = useCallback((extra = {}) => ({
    ...extra,
    ...(mentorToken ? { 'Authorization': `Bearer ${mentorToken}` } : {}),
  }), [mentorToken]);

  /* Normalize a timetable subject name to the canonical name from yearSubjects */
  const normalizeSubject = useCallback((raw, canonicalList) => {
    if (!raw) return raw;
    const trimmed = raw.trim();
    // Exact match first
    const exact = canonicalList.find(s => s.toLowerCase() === trimmed.toLowerCase());
    if (exact) return exact;
    // Fuzzy: find best overlap (remove spaces, compare)
    const clean = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
    const rawClean = clean(trimmed);
    const best = canonicalList.find(s => {
      const sc = clean(s);
      // Check if one contains the other, or either starts with the other (any length)
      return sc.includes(rawClean) || rawClean.includes(sc) ||
        sc.startsWith(rawClean) || rawClean.startsWith(sc);
    });
    return best || trimmed;
  }, []);

  /* Extract available subjects from the timetable — only what the mentor actually saved */
  useEffect(() => {
    // Collect every unique non-empty subject directly from timetable cells, no fuzzy/canonical expansion
    const rawSubjects = [...new Set(
      Object.values(timetable)
        .map(v => v.subject?.trim())
        .filter(s => s && s.length >= 1)
    )];

    setAvailableSubjects(rawSubjects);
    // Reset selected subject if it no longer exists in the timetable
    if (rawSubjects.length > 0 && overrideForm.subject &&
      !rawSubjects.some(s => s.toLowerCase() === overrideForm.subject.toLowerCase())) {
      setOverrideForm(f => ({ ...f, subject: '', topic: '' }));
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [timetable, yearSubjects]);


  /* Load cohort */
  const loadCohort = useCallback(async (yr) => {
    setLoadingCohort(true);
    try {
      const res = await fetch(`/api/mentors/cohort?year=${yr}`, { headers: authHeaders() });
      const data = await res.json();
      setStudents(data.students || []);
      setMetrics({ total: data.total || data.students?.length || 0, weak: data.weak || 0, missed: data.missed || 0 });
    } catch {
      setStudents([]);
      setMetrics({ total: 0, weak: 0, missed: 0 });
    } finally {
      setLoadingCohort(false);
    }
  }, [authHeaders]);

  /* Fix #4: Load quiz preview — prefer mentor-created questions from history, else call AI */
  const loadQuizPreview = useCallback(async (h) => {
    if (quizPreview?.historyId === h.id) {
      setQuizPreview(null);
      return;
    }
    setLoadingQuizPreview(h.id);
    try {
      // If history row has manual_questions (mentor-created), use them directly — no API call
      if (h.manual_questions && h.manual_questions.length > 0) {
        setQuizPreview({ historyId: h.id, topic: h.topic, questions: h.manual_questions, generatedBy: 'mentor' });
        setLoadingQuizPreview(null);
        return;
      }
      // Otherwise call AI preview
      const counts = h.counts || { mcq: 0, tf: 0, fill: 0 };
      const res = await fetch('/api/mentors/preview-quiz', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          topic: h.topic,
          subject: h.subject,
          counts: { mcq: counts.mcq || 0, tf: counts.tf || 0, fill: counts.fill || 0 }
        })
      });
      if (!res.ok) {
        const err = await res.json();
        addToast('Quiz preview failed: ' + (err.detail || res.statusText), 'error');
        return;
      }
      const data = await res.json();
      setQuizPreview({
        historyId: h.id,
        topic: h.topic,
        questions: data.questions || [],
        generatedBy: data.generated_by || 'gemini'
      });
    } catch (e) {
      addToast('Failed to load quiz preview: ' + e.message, 'error');
    } finally {
      setLoadingQuizPreview(null);
    }
  }, [quizPreview, authHeaders, addToast]);

  /* Load topic assignment history */
  const loadTopicHistory = useCallback(async (yr) => {
    setLoadingHistory(true);
    try {
      const res = await fetch(`/api/timetable/history?year=${yr}&limit=50`, { headers: authHeaders() });
      const data = await res.json();
      setTopicHistory(data.history || []);
    } catch {
      setTopicHistory([]);
    } finally {
      setLoadingHistory(false);
    }
  }, [authHeaders]);

  /* Load per-topic student performance */
  const loadTopicPerformance = useCallback(async (yr, topic, subject, date) => {
    setLoadingPerf(true);
    setTopicPerformance(null);
    try {
      const params = new URLSearchParams({ year: yr, topic, subject: subject || '', date: date || '' });
      const res = await fetch(`/api/mentors/topic-performance?${params}`, { headers: authHeaders() });
      const data = await res.json();
      setTopicPerformance(data);
    } catch {
      setTopicPerformance(null);
    } finally {
      setLoadingPerf(false);
    }
  }, [authHeaders]);

  /* Load year-specific canonical subject list */
  const loadYearSubjects = useCallback(async (yr) => {
    try {
      const res = await fetch(`/api/timetable/subjects?year=${yr}`);
      const data = await res.json();
      if (data.subjects) setYearSubjects(data.subjects);
    } catch { }
  }, []);

  /* Load timetable */
  const loadTimetable = useCallback(async (yr) => {
    try {
      const res = await fetch(`/api/timetable/weekly?year=${yr}`);
      const result = await res.json();
      if (result.success && result.schedule) {
        setTimetable(result.schedule);
      }
    } catch { }
  }, []);

  /* Helper: check if a topic object is expired based on due_date + due_time */
  const isExpired = (d) => {
    if (!d || !d.due_time) return false;
    const now = new Date();
    const [h, m] = d.due_time.split(':').map(Number);
    let dueDt = new Date();
    if (d.due_date) {
      const [dy, dm, dd] = d.due_date.split('-').map(Number);
      dueDt = new Date(dy, dm - 1, dd, h, m, 0);
    } else {
      dueDt.setHours(h, m, 0, 0);
    }
    return now > dueDt;
  };

  /* Load today's topic — only set active if NOT expired */
  const loadTodayTopic = useCallback(async (yr) => {
    try {
      const res = await fetch(`/api/timetable/get-today?year=${yr}`);
      const result = await res.json();
      if (result.success && result.data) {
        const d = result.data;
        // Only show as active if not expired — expired ones live in history only
        if (d.is_expired || isExpired(d)) {
          // Quiz expired: reset counts to 0, keep subject/topic for reference but no active quiz
          setOverrideForm(f => ({ ...f, subject: '', topic: '', mcq: 0, tf: 0, fill: 0, shortanswer: 0, dueDate: new Date().toISOString().split('T')[0], dueTime: '00:00' }));
          setTodayActive(null);
        } else {
          // Quiz still active: restore saved counts (default 0 if not set)
          setOverrideForm(f => ({ ...f, subject: '', topic: '', mcq: d.counts?.mcq ?? 0, tf: d.counts?.tf ?? 0, fill: d.counts?.fill ?? 0, shortanswer: d.counts?.short ?? 0, dueDate: d.due_date || new Date().toISOString().split('T')[0], dueTime: d.due_time || '00:00' }));
          setTodayActive(d);
        }
      }
    } catch { }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  /* Auto-clear todayActive the moment it expires (check every 30 seconds) */
  useEffect(() => {
    if (!todayActive) return;
    const timer = setInterval(() => {
      if (isExpired(todayActive)) {
        setTodayActive(null);
      }
    }, 30000); // check every 30s
    return () => clearInterval(timer);
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [todayActive]);

  /* Recalculate available topics when subject or timetable changes.
     The selected overrideForm.subject may be the canonical name while the timetable
     cell may have an abbreviation (e.g. "SE" vs "Software Engineering").
     We match both directions so topics always populate correctly. */
  useEffect(() => {
    if (!overrideForm.subject) { setTimetableTopics([]); return; }
    const cleanStr = s => s.toLowerCase().replace(/[^a-z0-9]/g, '');
    const selClean = cleanStr(overrideForm.subject);

    const topics = [...new Set(
      Object.values(timetable)
        .filter(v => {
          if (!v.subject || !v.topic || !v.topic.trim()) return false;
          const cellClean = cleanStr(v.subject.trim());
          // Exact match OR one is a prefix/substring of the other (handles "SE" ↔ "softwareengineering")
          return cellClean === selClean ||
            cellClean.startsWith(selClean) || selClean.startsWith(cellClean) ||
            cellClean.includes(selClean) || selClean.includes(cellClean);
        })
        .map(v => v.topic.trim())
        .filter(Boolean)
    )];

    setTimetableTopics(topics);
    if (topics.length > 0 && !topics.includes(overrideForm.topic)) {
      setOverrideForm(f => ({ ...f, topic: topics[0] }));
    }
  }, [overrideForm.subject, timetable]);



  const selectYear = useCallback((yr) => {
    sessionStorage.setItem('mentor_selected_year', yr);
    setYear(yr);
    setTimetableEditMode(false);
    setTodayActive(null);
    setModal(null);
    setOverrideForm({ subject: '', topic: '', mcq: 0, tf: 0, fill: 0, shortanswer: 0, dueDate: new Date().toISOString().split('T')[0], dueTime: '00:00' });
    setAvailableSubjects([]);
    setYearSubjects([]);
    setTopicHistory([]);
    setTopicPerformance(null);
    setSelectedHistoryItem(null);
    loadYearSubjects(yr);
    loadCohort(yr);
    loadTimetable(yr);
    loadTodayTopic(yr);
    loadTopicHistory(yr);
  }, [loadCohort, loadTimetable, loadTodayTopic, loadYearSubjects, loadTopicHistory]);

  /* On mount: if a year was saved in sessionStorage, auto-restore data */
  useEffect(() => {
    const saved = sessionStorage.getItem('mentor_selected_year');
    if (saved) {
      loadYearSubjects(saved);
      loadCohort(saved);
      loadTimetable(saved);
      loadTodayTopic(saved);
      loadTopicHistory(saved);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // Derived modal student lists — includes not_understood as weak
  const weakStudents = students.filter(st => st.status === 'weak' || st.status === 'not_understood');
  const missedStudents = students.filter(st => st.status === 'missed');
  const displayWeak = todayActive ? metrics.weak : 0;
  const displayMissed = todayActive ? metrics.missed : 0;
  const hasNoStudents = metrics.total === 0 && !loadingCohort; // Fix #2
  const noQuizActive = !todayActive; // Quick Actions & Performance Monitor require active quiz

  const handleSaveTimetable = useCallback(async () => {
    setSavingTimetable(true);
    try {
      const res = await fetch('/api/timetable/weekly', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({ year, schedule: timetable })
      });
      const result = await res.json();
      if (result.success) {
        addToast(`✅ Timetable for ${YEAR_FULL[year]} saved!`, 'success');
        setTimetableEditMode(false);
        // Fix #3: Reload both timetable AND subjects so Subject dropdown refreshes correctly
        await loadTimetable(year);
        await loadYearSubjects(year);
        // Reset subject/topic if currently selected subject no longer exists
        setOverrideForm(f => ({ ...f, subject: '', topic: '' }));
      } else {
        addToast('Error: ' + (result.detail || 'Unknown error'), 'error');
      }
    } catch (e) {
      addToast('Network error: ' + e.message, 'error');
    } finally {
      setSavingTimetable(false);
    }
  }, [year, timetable, authHeaders, addToast, loadTimetable, loadYearSubjects]);

  // Step 1: validate form, open mode chooser
  const handleSetTopic = useCallback((e) => {
    e.preventDefault();
    if (!overrideForm.subject || !overrideForm.topic) { addToast('Please fill in subject and topic.', 'error'); return; }
    if (!(overrideForm.mcq + overrideForm.tf + overrideForm.fill + overrideForm.shortanswer > 0)) { addToast('Specify at least 1 question.', 'error'); return; }
    setManualQuestions([]); // reset
    setQModeModal(true);    // open mode chooser
  }, [overrideForm, addToast]);

  // Step 2: actually activate topic (called from mode chooser or builder)
  const handleActivateTopic = useCallback(async (manualQs = null) => {
    setQModeModal(false);
    setQBuilderModal(false);
    setSubmitting(true);
    const localDate = new Date();
    const localDateStr = `${localDate.getFullYear()}-${String(localDate.getMonth() + 1).padStart(2, '0')}-${String(localDate.getDate()).padStart(2, '0')}`;
    try {
      const res = await fetch('/api/timetable/set-today', {
        method: 'POST',
        headers: authHeaders({ 'Content-Type': 'application/json' }),
        body: JSON.stringify({
          year, subject: overrideForm.subject, topic: overrideForm.topic,
          counts: { mcq: overrideForm.mcq, tf: overrideForm.tf, fill: overrideForm.fill, shortanswer: overrideForm.shortanswer },
          date: localDateStr,
          due_date: overrideForm.dueDate || null,
          due_time: overrideForm.dueTime || null,
          manual_questions: manualQs && manualQs.length > 0 ? manualQs : null,
        })
      });
      const result = await res.json();
      if (result.success) {
        const modeLabel = manualQs && manualQs.length > 0 ? '✍️ Manual questions saved!' : '🤖 AI will generate questions!';
        addToast(`Today's topic activated! ${modeLabel}`, 'success');
        setTodayActive({
          subject: overrideForm.subject,
          topic: overrideForm.topic,
          date: localDateStr,
          due_date: overrideForm.dueDate || null,
          due_time: overrideForm.dueTime || null,
          question_mode: manualQs && manualQs.length > 0 ? 'manual' : 'ai',
        });
        loadCohort(year);
        loadTopicHistory(year);
      } else {
        addToast('Error: ' + (result.detail || 'Failed'), 'error');
      }
    } catch (err) {
      addToast('Network error: ' + err.message, 'error');
    } finally {
      setSubmitting(false);
    }
  }, [overrideForm, year, authHeaders, addToast, loadCohort, loadTopicHistory]);

  /* Quick Actions */
  const handleAlertWeak = useCallback(async () => {
    if (!todayActive) {
      addToast('🚫 No quiz active now! Activate a topic first.', 'error');
      return;
    }
    if (hasNoStudents) { addToast('No students found in ' + YEAR_FULL[year] + '.', 'error'); return; }
    setActionLoading('alert');
    try {
      const res = await fetch(`/api/mentors/alert-weak?year=${year}`, {
        method: 'POST', headers: authHeaders()
      });
      const data = await res.json();
      if (!res.ok) {
        addToast('Failed to send alerts: ' + (data.detail || res.statusText), 'error');
        return;
      }
      const count = data.student_count ?? 0;
      if (count === 0) {
        addToast(`✅ No weak students found in ${YEAR_FULL[year]} — everyone is doing well!`, 'success');
      } else {
        addToast(`📧 Alert emails sent to ${count} weak student(s) in ${YEAR_FULL[year]}!`, 'success');
      }
    } catch (e) {
      addToast('Failed to send alerts: ' + e.message, 'error');
    } finally {
      setActionLoading(null);
    }
  }, [todayActive, hasNoStudents, year, authHeaders, addToast]);

  const handleEmailInactive = useCallback(async () => {
    setActionLoading('email');
    try {
      const res = await fetch(`/api/mentors/email-inactive?year=${year}`, {
        method: 'POST', headers: authHeaders()
      });
      const data = await res.json();
      addToast(`📧 Emails sent to ${data.student_count ?? 0} inactive student(s) in ${YEAR_FULL[year]}!`, 'success');
    } catch (e) {
      addToast('Failed to send emails: ' + e.message, 'error');
    } finally {
      setActionLoading(null);
    }
  }, [year, authHeaders, addToast]);

  const handleGenerateReport = useCallback(async () => {
    if (!todayActive) {
      addToast('🚫 No quiz active now! Activate a topic first.', 'error');
      return;
    }
    if (hasNoStudents) { addToast('No students found in ' + YEAR_FULL[year] + '.', 'error'); return; }
    setActionLoading('report');
    try {
      const res = await fetch(`/api/mentors/weak-report?year=${year}`, { headers: authHeaders() });
      const data = await res.json();
      setWeakReportData(data);
      setShowWeakReport(true);
    } catch (e) {
      addToast('Failed to generate report: ' + e.message, 'error');
    } finally {
      setActionLoading(null);
    }
  }, [todayActive, hasNoStudents, year, authHeaders, addToast]);

  const handleSendReport = useCallback(async () => {
    if (!todayActive) {
      addToast('🚫 No quiz active now! Activate a topic first.', 'error');
      return;
    }
    if (hasNoStudents) { addToast('No students found in ' + YEAR_FULL[year] + '.', 'error'); return; }
    setSendingReport(true);
    setActionLoading('sendreport');
    try {
      const res = await fetch(`/api/mentors/send-report?year=${year}`, {
        method: 'POST', headers: authHeaders()
      });
      const data = await res.json();
      if (data.success) {
        addToast(`📊 Report emailed to ${data.mentor_email}! (${data.total_students} students, ${data.weak_count} weak)`, 'success');
      } else {
        addToast(`⚠️ Report generated but email failed: ${data.message}`, 'error');
      }
    } catch (e) {
      addToast('Failed to send report: ' + e.message, 'error');
    } finally {
      setSendingReport(false);
      setActionLoading(null);
    }
  }, [todayActive, hasNoStudents, year, authHeaders, addToast]);

  const inputStyle = {
    background: s.surface3, border: `1px solid ${s.border}`, color: s.textPrimary, padding: '11px 14px',
    borderRadius: 10, fontSize: '0.88rem', fontFamily: "'Inter', sans-serif", outline: 'none',
    width: '100%', transition: 'border-color 0.2s, box-shadow 0.2s', boxSizing: 'border-box',
  };
  const cardStyle = {
    background: s.surface, border: `1px solid ${s.border}`, borderRadius: 18, padding: 26,
    boxShadow: s.cardShadow, position: 'relative',
  };

  /* ── Cohort Selector Overlay ──────────────────────────────────────────────── */
  if (!year) {
    return (
      <div style={{
        position: 'fixed', inset: 0, background: s.bg,
        zIndex: 2000, display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center',
        padding: 40, fontFamily: "'Inter', sans-serif",
        color: s.textPrimary, transition: 'background 0.35s, color 0.35s',
      }}>
        {/* Background blobs */}
        <div style={{ position: 'absolute', top: '20%', left: '15%', width: 400, height: 400, borderRadius: '50%', background: 'radial-gradient(circle, rgba(124,58,237,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />
        <div style={{ position: 'absolute', bottom: '20%', right: '15%', width: 300, height: 300, borderRadius: '50%', background: 'radial-gradient(circle, rgba(236,72,153,0.08) 0%, transparent 70%)', pointerEvents: 'none' }} />

        {/* Back to Login + Home Buttons */}
        <div style={{ position: 'absolute', top: 24, left: 24, display: 'flex', gap: 10 }}>
          <button
            id="cohort-back-to-login"
            onClick={() => { sessionStorage.clear(); navigate('/mentor-login'); }}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: 'rgba(124,58,237,0.1)', border: `1px solid rgba(124,58,237,0.25)`,
              borderRadius: 99, padding: '8px 18px',
              color: s.accLight, fontSize: '0.82rem', fontWeight: 700, cursor: 'pointer',
              fontFamily: 'inherit', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.2)'; e.currentTarget.style.borderColor = s.acc; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.1)'; e.currentTarget.style.borderColor = 'rgba(124,58,237,0.25)'; }}
          >
            ← Back to Login
          </button>
          <Link
            to="/"
            id="cohort-home-btn"
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: theme === 'dark' ? 'rgba(255,255,255,0.04)' : 'rgba(0,0,0,0.04)',
              border: `1px solid ${s.border}`,
              borderRadius: 99, padding: '8px 18px', textDecoration: 'none',
              color: s.textSec, fontSize: '0.82rem', fontWeight: 600, transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.color = s.textPrimary; e.currentTarget.style.borderColor = s.borderStrong; }}
            onMouseLeave={e => { e.currentTarget.style.color = s.textSec; e.currentTarget.style.borderColor = s.border; }}
          >
            🏠 Home
          </Link>
        </div>

        {/* Theme Toggle — top right */}
        <div style={{ position: 'absolute', top: 24, right: 24 }}>
          <ThemeToggle />
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 16 }}>
          <svg width="36" height="36" viewBox="0 0 34 34" fill="none">
            <circle cx="17" cy="17" r="13" fill="none" stroke="url(#overlayG)" strokeWidth="2" />
            <path d="M9 22 Q17 9 25 22" stroke="url(#overlayG)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <circle cx="17" cy="14" r="2.8" fill="url(#overlayG)" />
            <defs><linearGradient id="overlayG" x1="0" y1="0" x2="34" y2="34"><stop offset="0%" stopColor="#7C3AED" /><stop offset="100%" stopColor="#EC4899" /></linearGradient></defs>
          </svg>
          <span style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 900, fontSize: '1.8rem', color: s.textPrimary }}>EduMentor <span style={{ background: s.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI</span></span>
        </div>
        <h1 style={{ fontFamily: "'Outfit', sans-serif", fontSize: 'clamp(1.6rem, 3.5vw, 2.4rem)', fontWeight: 900, marginBottom: 8, textAlign: 'center', background: s.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>
          Select Your Batch
        </h1>
        <p style={{ fontSize: '0.9rem', color: s.textSec, marginBottom: 32, textAlign: 'center' }}>Choose the cohort you manage to enter your dashboard</p>


        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 24, maxWidth: 860, width: '100%' }}>
          {[
            { yr: '1', icon: '🎓', name: '1st Year', color: 'linear-gradient(135deg,#7C3AED,#EC4899)' },
            { yr: '2', icon: '🚀', name: '2nd Year', color: 'linear-gradient(135deg,#2563EB,#7C3AED)' },
            { yr: '3', icon: '🏆', name: '3rd Year', color: 'linear-gradient(135deg,#0891B2,#2563EB)' },
          ].map(c => (
            <div key={c.yr} onClick={() => selectYear(c.yr)} style={{
              background: s.surface, border: `1px solid ${s.border}`, borderRadius: 22, padding: '36px 28px',
              textAlign: 'center', cursor: 'pointer', position: 'relative', overflow: 'hidden',
              boxShadow: s.cardShadow, transition: 'transform 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275), border-color 0.3s, box-shadow 0.4s',
            }}
              onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-8px) scale(1.02)'; e.currentTarget.style.borderColor = s.accLight; e.currentTarget.style.boxShadow = '0 24px 50px rgba(124,58,237,0.18)'; }}
              onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.borderColor = s.border; e.currentTarget.style.boxShadow = s.cardShadow; }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: c.color }} />
              <span style={{ fontSize: '3rem', display: 'inline-block', marginBottom: 20 }}>{c.icon}</span>
              <h3 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.35rem', fontWeight: 800, marginBottom: 10, color: s.textPrimary }}>{c.name}</h3>

              <div style={{ marginTop: 20, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.8rem', fontWeight: 700, color: s.accLight }}>
                Enter Dashboard <span style={{ fontSize: '0.9rem' }}>→</span>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  /* ── Main Dashboard ─────────────────────────────────────────────────────── */
  const SIDEBAR_W = sidebarCollapsed ? 56 : 300;

  return (
    <div style={{ minHeight: '100vh', background: s.bg, color: s.textPrimary, display: 'flex', flexDirection: 'column', fontFamily: "'Inter', sans-serif", transition: 'background 0.35s, color 0.35s' }}>

      {/* ── Nav Bar ──────────────────────────────────────────────────────── */}
      <nav style={{
        background: s.navBg, backdropFilter: 'blur(20px)',
        borderBottom: `1px solid ${s.border}`, padding: '14px 28px',
        display: 'flex', justifyContent: 'space-between', alignItems: 'center',
        position: 'sticky', top: 0, zIndex: 100,
        transition: 'background 0.35s, border-color 0.35s',
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <svg width="28" height="28" viewBox="0 0 34 34" fill="none">
            <circle cx="17" cy="17" r="13" fill="none" stroke="url(#navG)" strokeWidth="2" />
            <path d="M9 22 Q17 9 25 22" stroke="url(#navG)" strokeWidth="2.5" fill="none" strokeLinecap="round" />
            <circle cx="17" cy="14" r="2.8" fill="url(#navG)" />
            <defs><linearGradient id="navG" x1="0" y1="0" x2="34" y2="34"><stop offset="0%" stopColor="#7C3AED" /><stop offset="100%" stopColor="#EC4899" /></linearGradient></defs>
          </svg>
          <span style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1.15rem', color: s.textPrimary }}>
            EduMentor <span style={{ background: s.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI</span>
          </span>
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          {/* Home Button */}
          <Link to="/" id="mentor-dashboard-home-btn" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: 'rgba(124,58,237,0.08)', border: `1px solid rgba(124,58,237,0.2)`,
            borderRadius: 8, padding: '5px 14px', textDecoration: 'none',
            color: s.textSec, fontSize: '0.8rem', fontWeight: 600, transition: 'all 0.2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.15)'; e.currentTarget.style.color = '#fff'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.08)'; e.currentTarget.style.color = s.textSec; }}>
            🏠 Home
          </Link>
          {/* Switch Year Button */}
          <button
            id="btn-switch-year"
            onClick={() => {
              sessionStorage.removeItem('mentor_selected_year');
              setYear(null);
              setTodayActive(null);
              setStudents([]);
              setMetrics({ total: 0, weak: 0, missed: 0 });
              setTimetable({});
              setTopicHistory([]);
              setTopicPerformance(null);
              setSelectedHistoryItem(null);
              setShowHistory(false);
              setModal(null);
              setTimetableEditMode(false);
            }}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: 'rgba(124,58,237,0.08)', border: `1px solid rgba(124,58,237,0.25)`,
              borderRadius: 8, padding: '5px 14px',
              color: s.accLight, fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
              fontFamily: 'inherit', transition: 'all 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.2)'; e.currentTarget.style.borderColor = s.acc; e.currentTarget.style.color = '#fff'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.08)'; e.currentTarget.style.borderColor = 'rgba(124,58,237,0.25)'; e.currentTarget.style.color = s.accLight; }}
          >
            ⇄ Switch Year
          </button>
          {/* Active year badge */}
          <span style={{
            fontSize: '0.72rem', fontWeight: 800, letterSpacing: '0.06em', textTransform: 'uppercase',
            color: '#fff', background: s.grad,
            padding: '4px 14px', borderRadius: 99,
            display: 'inline-flex', alignItems: 'center', gap: 5,
          }}>
            {YEAR_ICONS[year]} {YEAR_LABELS[year]}
          </span>
          <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase', color: s.accLight, background: 'rgba(124,58,237,0.1)', border: `1px solid ${s.border}`, padding: '4px 12px', borderRadius: 99 }}>
            Mentor Portal
          </span>
          {/* History Button */}
          <button
            id="btn-history-nav"
            onClick={() => {
              const yr = year || '3';
              setShowHistory(true);
              setHistoryYear(yr);
              setHistoryCleared(false);
              setClearingHistory(false);
              loadTopicHistory(yr);
            }}
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 6,
              background: showHistory ? 'rgba(124,58,237,0.2)' : 'rgba(124,58,237,0.06)',
              border: `1px solid ${showHistory ? s.acc : s.border}`,
              borderRadius: 8, padding: '5px 16px',
              color: showHistory ? '#fff' : s.textSec,
              fontSize: '0.8rem', fontWeight: 700, cursor: 'pointer',
              fontFamily: 'inherit', transition: 'all 0.2s', letterSpacing: '0.02em',
            }}
            onMouseEnter={e => { if (!showHistory) { e.currentTarget.style.background = 'rgba(124,58,237,0.15)'; e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = s.borderStrong; } }}
            onMouseLeave={e => { if (!showHistory) { e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; e.currentTarget.style.color = s.textSec; e.currentTarget.style.borderColor = s.border; } }}>
            📜 History
          </button>
          <ThemeToggle minWidth="64px" />
          <button onClick={() => { sessionStorage.clear(); navigate('/mentor-login'); }} id="dashboard-logout-btn"
            style={{ background: 'none', border: 'none', color: s.textSec, cursor: 'pointer', fontSize: '0.85rem', fontWeight: 600, fontFamily: 'inherit', transition: 'color 0.2s' }}
            onMouseEnter={e => e.currentTarget.style.color = '#fff'}
            onMouseLeave={e => e.currentTarget.style.color = s.textSec}>
            Log Out
          </button>
        </div>
      </nav>

      {/* ── History Panel ─────────────────────────────────────────────────── */}
      {showHistory && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 500,
          background: 'rgba(4,4,12,0.7)', backdropFilter: 'blur(10px)',
          display: 'flex', justifyContent: 'flex-end',
        }} onClick={() => setShowHistory(false)}>
          <div style={{
            width: '100%', maxWidth: 680, height: '100vh',
            background: s.surface, borderLeft: `1px solid ${s.border}`,
            display: 'flex', flexDirection: 'column', overflow: 'hidden',
            animation: 'slideInRight 0.32s cubic-bezier(0.16,1,0.3,1)',
          }} onClick={e => e.stopPropagation()}>

            {/* Panel Header */}
            <div style={{
              padding: '24px 28px', borderBottom: `1px solid ${s.border}`,
              display: 'flex', alignItems: 'center', justifyContent: 'space-between',
              background: s.surface, flexShrink: 0,
            }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{
                  width: 42, height: 42, borderRadius: 12,
                  background: 'rgba(124,58,237,0.1)', border: `1px solid ${s.border}`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.25rem',
                }}>📜</div>
                <div>
                  <div style={{ fontFamily: "'Outfit',sans-serif", fontSize: '1.15rem', fontWeight: 800, color: s.textPrimary }}>Topic Assignment History</div>
                  <div style={{ fontSize: '0.75rem', color: s.textSec, marginTop: 2 }}>{YEAR_FULL[historyYear || year]}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <button onClick={() => { if (!historyCleared) loadTopicHistory(historyYear || year); }} style={{
                  background: s.surface2, border: `1px solid ${s.border}`, borderRadius: 8,
                  padding: '7px 16px', fontSize: '0.78rem', fontWeight: 600,
                  color: historyCleared ? s.textMuted : s.textSec,
                  cursor: historyCleared ? 'not-allowed' : 'pointer', fontFamily: 'inherit', transition: 'all 0.2s',
                  opacity: historyCleared ? 0.45 : 1,
                }}
                  onMouseEnter={e => { if (!historyCleared) { e.currentTarget.style.color = s.textPrimary; e.currentTarget.style.borderColor = s.borderStrong; } }}
                  onMouseLeave={e => { if (!historyCleared) { e.currentTarget.style.color = s.textSec; e.currentTarget.style.borderColor = s.border; } }}>
                  {loadingHistory ? '⌛' : '↻'} Refresh
                </button>
                {(topicHistory.length > 0 || historyCleared) && (
                  <button
                    disabled={historyCleared || clearingHistory}
                    onClick={async () => {
                      if (historyCleared || clearingHistory) return;
                      setClearingHistory(true);
                      try {
                        const res = await fetch(
                          `/api/timetable/history?year=${historyYear || year}`,
                          { method: 'DELETE', headers: authHeaders() }
                        );
                        if (!res.ok) throw new Error(`Server error: ${res.status}`);
                        // ✅ API success — now clear UI
                        setTopicHistory([]);
                        setSelectedHistoryItem(null);
                        setTopicPerformance(null);
                        setHistoryCleared(true);
                      } catch (err) {
                        addToast('Failed to clear history: ' + err.message, 'error');
                      } finally {
                        setClearingHistory(false);
                      }
                    }}
                    style={{
                      background: (historyCleared || clearingHistory) ? 'rgba(239,68,68,0.03)' : 'rgba(239,68,68,0.06)',
                      border: '1px solid rgba(239,68,68,0.25)', borderRadius: 8,
                      padding: '7px 14px', fontSize: '0.78rem', fontWeight: 700,
                      color: (historyCleared || clearingHistory) ? 'rgba(239,68,68,0.45)' : '#EF4444',
                      cursor: (historyCleared || clearingHistory) ? 'not-allowed' : 'pointer',
                      fontFamily: 'inherit', transition: 'all 0.2s',
                      opacity: (historyCleared || clearingHistory) ? 0.6 : 1,
                      display: 'flex', alignItems: 'center', gap: 5,
                    }}
                    onMouseEnter={e => { if (!historyCleared && !clearingHistory) { e.currentTarget.style.background = 'rgba(239,68,68,0.14)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.5)'; } }}
                    onMouseLeave={e => { if (!historyCleared && !clearingHistory) { e.currentTarget.style.background = 'rgba(239,68,68,0.06)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.25)'; } }}>
                    {clearingHistory ? '⌛' : '🗑'} {clearingHistory ? 'Clearing…' : 'Clear History'}
                  </button>
                )}
                <button onClick={() => setShowHistory(false)} style={{
                  width: 36, height: 36, borderRadius: '50%', background: 'rgba(255,255,255,0.06)',
                  border: `1px solid ${s.border}`, cursor: 'pointer', color: s.textSec,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: '1rem', fontWeight: 700, transition: 'all 0.2s',
                }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = s.textPrimary; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = s.textSec; }}>
                  ✕
                </button>
              </div>
            </div>




            {/* Stats strip */}
            <div style={{
              padding: '12px 28px', borderBottom: `1px solid ${s.border}`,
              display: 'flex', gap: 20, background: s.surface2, flexShrink: 0,
            }}>
              {[{ label: 'Total Topics', val: topicHistory.length, color: s.accLight },
              { val: YEAR_FULL[historyYear || year], color: s.textSec }].map(c => (
                <div key={c.label} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <span style={{ fontSize: '0.88rem', fontWeight: 800, color: c.color }}>{c.val}</span>
                  <span style={{ fontSize: '0.7rem', color: s.textMuted }}>{c.label}</span>
                </div>
              ))}
            </div>

            {/* Scrollable content */}
            <div style={{ flex: 1, overflowY: 'auto', padding: '20px 28px' }}>
              {loadingHistory ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 200, gap: 12 }}>
                  <div style={{ fontSize: '2rem' }}>⌛</div>
                  <div style={{ color: s.textSec, fontSize: '0.88rem' }}>Loading history…</div>
                </div>
              ) : historyCleared ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 260, gap: 12 }}>
                  <div style={{ fontSize: '3rem' }}>🗑</div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: s.textPrimary }}>History Cleared</div>
                  <div style={{ fontSize: '0.82rem', color: s.textMuted, textAlign: 'center', maxWidth: 280 }}>History has been cleared. Close and reopen to start fresh.</div>
                </div>
              ) : topicHistory.length === 0 ? (
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: 260, gap: 12 }}>
                  <div style={{ fontSize: '3rem' }}>📭</div>
                  <div style={{ fontWeight: 700, fontSize: '1rem', color: s.textPrimary }}>No History Yet</div>
                  <div style={{ fontSize: '0.82rem', color: s.textMuted, textAlign: 'center', maxWidth: 260 }}>No topics have been assigned for {YEAR_FULL[historyYear || year]} yet.</div>
                </div>
              ) : (
                <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
                  {topicHistory.map((h, i) => {
                    const isSelected = selectedHistoryItem?.id === h.id;
                    const totalQ = h.counts
                      ? (h.counts.mcq || 0) + (h.counts.tf || 0) + (h.counts.fill || 0) + (h.counts.shortanswer || h.counts.short || 0)
                      : 0;
                    return (
                      <div key={h.id} style={{ display: 'flex', gap: 0, position: 'relative' }}>
                        {/* Timeline spine */}
                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 32, flexShrink: 0, paddingTop: 18 }}>
                          <div style={{
                            width: 10, height: 10, borderRadius: '50%', flexShrink: 0,
                            background: i === 0 ? s.acc : 'rgba(124,58,237,0.35)',
                            border: `2px solid ${i === 0 ? s.acc : 'rgba(124,58,237,0.2)'}`,
                            boxShadow: i === 0 ? `0 0 10px ${s.acc}88` : 'none',
                            zIndex: 1,
                          }} />
                          {i < topicHistory.length - 1 && (
                            <div style={{ width: 1, flex: 1, background: 'rgba(124,58,237,0.12)', minHeight: 32 }} />
                          )}
                        </div>

                        {/* Card */}
                        <div style={{ flex: 1, paddingBottom: 16, paddingLeft: 12 }}>
                          <div
                            onClick={() => {
                              if (isSelected) { setSelectedHistoryItem(null); setTopicPerformance(null); setExpandedStudents({}); return; }
                              setSelectedHistoryItem(h);
                              setExpandedStudents({});
                              loadTopicPerformance(year, h.topic, h.subject, h.date);
                            }}
                            style={{
                              background: isSelected ? 'rgba(124,58,237,0.1)' : s.surface2,
                              border: `1px solid ${isSelected ? s.acc : s.border}`,
                              borderRadius: 14, padding: '14px 18px', cursor: 'pointer',
                              transition: 'all 0.2s',
                            }}
                            onMouseEnter={e => { if (!isSelected) { e.currentTarget.style.borderColor = s.borderStrong; e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; } }}
                            onMouseLeave={e => { if (!isSelected) { e.currentTarget.style.borderColor = s.border; e.currentTarget.style.background = s.surface2; } }}>

                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 10 }}>
                              <div style={{ flex: 1, minWidth: 0 }}>
                                <div style={{ display: 'flex', alignItems: 'center', gap: 8, flexWrap: 'wrap' }}>
                                  <div style={{ fontSize: '0.95rem', fontWeight: 700, color: s.textPrimary }}>{h.topic}</div>
                                  {i === 0 && (
                                    <span style={{ fontSize: '0.6rem', fontWeight: 700, color: '#10B981', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 99, padding: '2px 7px', letterSpacing: '0.04em' }}>LATEST</span>
                                  )}
                                </div>
                                <div style={{ fontSize: '0.75rem', color: s.accLight, marginTop: 3, fontWeight: 600 }}>{h.subject}</div>
                              </div>
                              <div style={{ textAlign: 'right', flexShrink: 0, marginLeft: 12 }}>
                                <div style={{ fontSize: '0.72rem', fontWeight: 700, color: s.textSec }}>{h.date || '—'}</div>
                                {h.set_by && <div style={{ fontSize: '0.65rem', color: s.textMuted, marginTop: 2 }}>by {h.set_by}</div>}
                              </div>
                            </div>

                            {/* Meta chips — Fix #4: Add Preview Quiz button */}
                            <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', alignItems: 'center' }}>
                              {totalQ > 0 && (
                                <span style={{ fontSize: '0.68rem', color: s.textMuted, background: s.surface3, border: `1px solid ${s.border}`, borderRadius: 6, padding: '3px 9px' }}>
                                  ❓ {totalQ} Questions{h.counts?.mcq > 0 ? ` · ${h.counts.mcq} MCQ` : ''}{h.counts?.tf > 0 ? ` · ${h.counts.tf} T/F` : ''}
                                </span>
                              )}
                              {h.due_time && (
                                <span style={{ fontSize: '0.68rem', color: s.textMuted, background: s.surface3, border: `1px solid ${s.border}`, borderRadius: 6, padding: '3px 9px' }}>
                                  ⏰ Due {h.due_date || h.date} {to12hr(h.due_time)}
                                </span>
                              )}
                              {/* Preview Quiz chip — Fix #4 */}
                              {totalQ > 0 && (
                                <button
                                  type="button"
                                  onClick={e => { e.stopPropagation(); loadQuizPreview(h); }}
                                  disabled={loadingQuizPreview === h.id}
                                  style={{
                                    fontSize: '0.65rem', fontWeight: 700,
                                    color: quizPreview?.historyId === h.id ? '#10B981' : s.accLight,
                                    background: quizPreview?.historyId === h.id ? 'rgba(16,185,129,0.1)' : 'rgba(124,58,237,0.08)',
                                    border: `1px solid ${quizPreview?.historyId === h.id ? 'rgba(16,185,129,0.3)' : 'rgba(124,58,237,0.2)'}`,
                                    borderRadius: 6, padding: '3px 10px', cursor: loadingQuizPreview === h.id ? 'default' : 'pointer',
                                    fontFamily: 'inherit', transition: 'all 0.2s',
                                    opacity: loadingQuizPreview === h.id ? 0.6 : 1,
                                  }}
                                >
                                  {loadingQuizPreview === h.id ? '⌛ Loading…' : quizPreview?.historyId === h.id ? '▲ Hide Quiz' : '🧠 Preview Quiz'}
                                </button>
                              )}
                              <span style={{
                                fontSize: '0.68rem', fontWeight: 700, marginLeft: 'auto',
                                color: isSelected ? s.accLight : s.textMuted,
                                cursor: 'pointer', padding: '3px 9px',
                              }}>
                                {isSelected ? '▲ Hide' : '▼ View'} Results
                              </span>
                            </div>
                          </div>

                          {/* Quiz Preview panel — shows mentor-created OR AI-generated questions + answers */}
                          {quizPreview?.historyId === h.id && quizPreview.questions.length > 0 && (
                            <div style={{
                              marginTop: 4, background: s.surface3,
                              border: `1px solid ${quizPreview.generatedBy === 'mentor' ? 'rgba(124,58,237,0.45)' : 'rgba(16,185,129,0.35)'}`,
                              borderRadius: 12, padding: '16px 18px',
                            }}>
                              {/* Header */}
                              <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
                                <span style={{ fontSize: '0.8rem', fontWeight: 800, color: quizPreview.generatedBy === 'mentor' ? s.accLight : '#10B981' }}>
                                  {quizPreview.generatedBy === 'mentor' ? '📝 Mentor-Created Quiz' : '🧠 AI-Generated Quiz Preview'}
                                </span>
                                <span style={{ fontSize: '0.65rem', color: s.textSec, fontWeight: 600 }}>
                                  {quizPreview.questions.length} question{quizPreview.questions.length !== 1 ? 's' : ''} · <em>{h.topic}</em>
                                </span>
                                {quizPreview.generatedBy === 'mentor' && (
                                  <span style={{ fontSize: '0.6rem', fontWeight: 700, color: s.accLight, background: 'rgba(124,58,237,0.1)', border: '1px solid rgba(124,58,237,0.3)', borderRadius: 99, padding: '2px 8px' }}>EXACT QUESTIONS STUDENTS SAW</span>
                                )}
                                {quizPreview.generatedBy !== 'mentor' && (
                                  <span style={{ fontSize: '0.6rem', fontWeight: 700, color: '#10B981', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 99, padding: '2px 8px' }}>SAMPLE PREVIEW · AI generates unique questions per student</span>
                                )}
                              </div>
                              {/* Question cards */}
                              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                                {quizPreview.questions.map((q, qi) => {
                                  const qType = (q.type || 'MCQ').toUpperCase();
                                  const typeColor = qType === 'MCQ' ? s.accLight : qType === 'TF' ? '#10B981' : '#F59E0B';
                                  const typeBg = qType === 'MCQ' ? 'rgba(124,58,237,0.12)' : qType === 'TF' ? 'rgba(16,185,129,0.12)' : 'rgba(245,158,11,0.12)';
                                  const typeBd = qType === 'MCQ' ? 'rgba(124,58,237,0.3)' : qType === 'TF' ? 'rgba(16,185,129,0.3)' : 'rgba(245,158,11,0.3)';
                                  return (
                                    <div key={qi} style={{ background: s.surface2, border: `1px solid ${s.border}`, borderRadius: 10, padding: '12px 14px' }}>
                                      <div style={{ display: 'flex', gap: 8, marginBottom: 8, alignItems: 'flex-start' }}>
                                        <span style={{ fontSize: '0.6rem', fontWeight: 800, textTransform: 'uppercase', padding: '2px 7px', borderRadius: 4, flexShrink: 0, marginTop: 2, background: typeBg, color: typeColor, border: `1px solid ${typeBd}` }}>
                                          Q{qi + 1} · {qType === 'TF' ? 'True/False' : qType === 'FILL' ? 'Fill Blank' : 'MCQ'}
                                        </span>
                                        <div style={{ fontSize: '0.82rem', fontWeight: 600, color: s.textPrimary, lineHeight: 1.55 }}>{q.q}</div>
                                      </div>
                                      {/* Options */}
                                      {q.options && q.options.length > 0 && (
                                        <div style={{ display: 'flex', flexDirection: 'column', gap: 4, marginBottom: 10, paddingLeft: 4 }}>
                                          {q.options.map((opt, oi) => {
                                            const correctAns = q.a || q.correct_answer || '';
                                            const isCorrect = opt === correctAns;
                                            return (
                                              <div key={oi} style={{
                                                display: 'flex', alignItems: 'center', gap: 8,
                                                fontSize: '0.73rem', padding: '5px 10px', borderRadius: 7,
                                                background: isCorrect ? 'rgba(16,185,129,0.1)' : 'transparent',
                                                border: `1px solid ${isCorrect ? 'rgba(16,185,129,0.4)' : s.border}`,
                                                color: isCorrect ? '#10B981' : s.textSec,
                                                fontWeight: isCorrect ? 700 : 400,
                                              }}>
                                                <span style={{ fontWeight: 700, minWidth: 18, color: isCorrect ? '#10B981' : s.textMuted }}>
                                                  {['A', 'B', 'C', 'D'][oi]}.
                                                </span>
                                                {opt}
                                                {isCorrect && <span style={{ marginLeft: 'auto', fontSize: '0.7rem' }}>✅ Correct</span>}
                                              </div>
                                            );
                                          })}
                                        </div>
                                      )}
                                      {/* Correct Answer badge */}
                                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                                        <span style={{ fontSize: '0.65rem', fontWeight: 700, color: '#10B981', background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 6, padding: '3px 10px' }}>
                                          ✓ Correct Answer: {q.a || q.correct_answer || '—'}
                                        </span>
                                      </div>
                                    </div>
                                  );
                                })}
                              </div>
                            </div>
                          )}

                          {/* Inline performance breakdown — includes quiz questions + per-student answers */}
                          {isSelected && (
                            <div style={{
                              marginTop: 4, background: s.surface3,
                              border: `1px solid ${s.acc}`,
                              borderRadius: 12, padding: '16px 18px',
                            }}>
                              {loadingPerf ? (
                                <div style={{ textAlign: 'center', padding: '20px 0', color: s.textSec, fontSize: '0.82rem' }}>
                                  <div style={{ fontSize: '1.5rem', marginBottom: 6 }}>⌛</div>
                                  Loading student performance…
                                </div>
                              ) : topicPerformance ? (
                                <>
                                  {/* Header label */}
                                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
                                    <span style={{ fontSize: '0.78rem', fontWeight: 800, color: s.accLight }}>📊 Student Results</span>
                                    <span style={{ fontSize: '0.65rem', color: s.textSec }}>— {h.topic}</span>
                                    {topicPerformance.generated_by === 'mentor' && (
                                      <span style={{ fontSize: '0.6rem', fontWeight: 700, color: s.accLight, background: 'rgba(124,58,237,0.1)', border: '1px solid rgba(124,58,237,0.3)', borderRadius: 99, padding: '2px 8px', marginLeft: 4 }}>Mentor Quiz</span>
                                    )}
                                  </div>

                                  {/* Summary row */}
                                  <div style={{ display: 'flex', gap: 8, marginBottom: 14 }}>
                                    {[
                                      { label: 'Total', val: topicPerformance.total, color: '#7C3AED', bg: 'rgba(124,58,237,0.08)' },
                                      { label: 'Attempted', val: topicPerformance.attempted, color: '#10B981', bg: 'rgba(16,185,129,0.08)' },
                                      { label: 'Weak', val: topicPerformance.weak_count, color: '#EF4444', bg: 'rgba(239,68,68,0.08)' },
                                      { label: 'Missed', val: topicPerformance.missed_count, color: '#F59E0B', bg: 'rgba(245,158,11,0.08)' },
                                    ].map(c => (
                                      <div key={c.label} style={{ flex: 1, textAlign: 'center', background: c.bg, borderRadius: 10, padding: '8px 4px' }}>
                                        <div style={{ fontSize: '1.1rem', fontWeight: 900, color: c.color, fontFamily: "'Outfit',sans-serif" }}>{c.val}</div>
                                        <div style={{ fontSize: '0.62rem', color: s.textMuted, marginTop: 1 }}>{c.label}</div>
                                      </div>
                                    ))}
                                  </div>

                                  {/* Quiz Questions (from performance data — mentor or AI) */}
                                  {topicPerformance.questions && topicPerformance.questions.length > 0 && (
                                    <div style={{ marginBottom: 16, border: `1px solid ${topicPerformance.generated_by === 'mentor' ? 'rgba(124,58,237,0.35)' : 'rgba(16,185,129,0.3)'}`, borderRadius: 10, padding: '12px 14px', background: s.surface2 }}>
                                      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                                        <span style={{ fontSize: '0.72rem', fontWeight: 800, color: topicPerformance.generated_by === 'mentor' ? s.accLight : '#10B981' }}>
                                          {topicPerformance.generated_by === 'mentor' ? '📝 Quiz Questions (Mentor Created)' : '🧠 Quiz Questions (AI Generated)'}
                                        </span>
                                        <span style={{ fontSize: '0.6rem', color: s.textMuted }}>{topicPerformance.questions.length} questions</span>
                                      </div>
                                      <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                        {topicPerformance.questions.map((q, qi) => {
                                          const qType = (q.type || 'MCQ').toUpperCase();
                                          const correctAns = q.a || q.correct_answer || '';
                                          const typeColor = qType === 'MCQ' ? s.accLight : qType === 'TF' ? '#10B981' : '#F59E0B';
                                          const typeBg = qType === 'MCQ' ? 'rgba(124,58,237,0.1)' : qType === 'TF' ? 'rgba(16,185,129,0.1)' : 'rgba(245,158,11,0.1)';
                                          return (
                                            <div key={qi} style={{ background: s.surface3, border: `1px solid ${s.border}`, borderRadius: 8, padding: '10px 12px' }}>
                                              <div style={{ display: 'flex', gap: 7, marginBottom: 6, alignItems: 'flex-start' }}>
                                                <span style={{ fontSize: '0.58rem', fontWeight: 700, textTransform: 'uppercase', padding: '2px 6px', borderRadius: 4, flexShrink: 0, marginTop: 2, background: typeBg, color: typeColor, border: `1px solid ${typeColor}44` }}>
                                                  Q{qi + 1} · {qType === 'TF' ? 'T/F' : qType === 'FILL' ? 'Fill' : 'MCQ'}
                                                </span>
                                                <span style={{ fontSize: '0.79rem', fontWeight: 600, color: s.textPrimary, lineHeight: 1.5 }}>{q.q}</span>
                                              </div>
                                              {q.options && q.options.length > 0 && (
                                                <div style={{ paddingLeft: 4, display: 'flex', flexDirection: 'column', gap: 3, marginBottom: 6 }}>
                                                  {q.options.map((opt, oi) => (
                                                    <div key={oi} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.7rem', padding: '3px 8px', borderRadius: 6, background: opt === correctAns ? 'rgba(16,185,129,0.08)' : 'transparent', border: `1px solid ${opt === correctAns ? 'rgba(16,185,129,0.3)' : s.border}`, color: opt === correctAns ? '#10B981' : s.textSec, fontWeight: opt === correctAns ? 700 : 400 }}>
                                                      <span style={{ fontWeight: 700, minWidth: 16 }}>{['A', 'B', 'C', 'D'][oi]}.</span>
                                                      {opt}
                                                      {opt === correctAns && <span style={{ marginLeft: 'auto' }}>✅</span>}
                                                    </div>
                                                  ))}
                                                </div>
                                              )}
                                              <span style={{ fontSize: '0.63rem', fontWeight: 700, color: '#10B981', background: 'rgba(16,185,129,0.07)', border: '1px solid rgba(16,185,129,0.2)', borderRadius: 5, padding: '2px 8px', display: 'inline-block' }}>
                                                ✓ Answer: {correctAns}
                                              </span>
                                            </div>
                                          );
                                        })}
                                      </div>
                                    </div>
                                  )}

                                  {/* Student rows — expandable to show individual answers */}
                                  <div style={{ fontSize: '0.72rem', fontWeight: 700, color: s.textMuted, marginBottom: 8, letterSpacing: '0.04em', textTransform: 'uppercase' }}>Student Responses</div>
                                  <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                                    {topicPerformance.students.map((st, si) => {
                                      const cfg = {
                                        good: { dot: '#10B981', label: 'Passed', badge: 'rgba(16,185,129,0.08)', bdClr: 'rgba(16,185,129,0.22)', txtClr: '#10B981' },
                                        weak: { dot: '#EF4444', label: 'Weak', badge: 'rgba(239,68,68,0.08)', bdClr: 'rgba(239,68,68,0.22)', txtClr: '#EF4444' },
                                        missed: { dot: '#F59E0B', label: 'Missed', badge: 'rgba(245,158,11,0.06)', bdClr: 'rgba(245,158,11,0.18)', txtClr: '#F59E0B' },
                                      };
                                      const c = cfg[st.status] || cfg.missed;
                                      const isExpanded = !!expandedStudents[st.regno];
                                      const hasAnswers = st.answers && st.answers.length > 0;
                                      return (
                                        <div key={si} style={{ borderRadius: 10, overflow: 'hidden', border: `1px solid ${isExpanded ? s.acc : s.border}`, background: s.surface2, transition: 'border-color 0.2s' }}>
                                          {/* Student summary row — click to expand */}
                                          <div
                                            onClick={() => hasAnswers && setExpandedStudents(prev => ({ ...prev, [st.regno]: !prev[st.regno] }))}
                                            style={{ display: 'flex', alignItems: 'center', gap: 10, padding: '10px 12px', cursor: hasAnswers ? 'pointer' : 'default' }}
                                          >
                                            {/* Avatar */}
                                            <div style={{ width: 32, height: 32, borderRadius: '50%', background: s.grad, flexShrink: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.8rem', fontWeight: 800, color: '#fff' }}>
                                              {(st.name || 'S')[0].toUpperCase()}
                                            </div>
                                            {/* Name & regno */}
                                            <div style={{ flex: 1, minWidth: 0 }}>
                                              <div style={{ fontSize: '0.85rem', fontWeight: 700, color: s.textPrimary, lineHeight: 1.2 }}>{st.name}</div>
                                              <div style={{ fontSize: '0.62rem', color: s.textMuted, fontFamily: 'monospace', marginTop: 1 }}>{st.regno}</div>
                                            </div>
                                            {/* Score */}
                                            {st.score && (
                                              <div style={{ fontSize: '0.77rem', color: s.textSec, fontFamily: 'monospace', flexShrink: 0 }}>{st.score}</div>
                                            )}
                                            {/* Percentage */}
                                            {st.percentage != null && (
                                              <div style={{ fontSize: '0.88rem', fontWeight: 800, minWidth: 38, textAlign: 'right', color: st.percentage >= 50 ? '#10B981' : '#EF4444' }}>{st.percentage}%</div>
                                            )}
                                            {/* Status chip */}
                                            <div style={{ display: 'flex', alignItems: 'center', gap: 5, background: c.badge, border: `1px solid ${c.bdClr}`, borderRadius: 8, padding: '3px 10px', flexShrink: 0 }}>
                                              <div style={{ width: 6, height: 6, borderRadius: '50%', background: c.dot }} />
                                              <span style={{ fontSize: '0.68rem', fontWeight: 700, color: c.txtClr }}>{c.label}</span>
                                            </div>
                                            {/* Expand arrow */}
                                            {hasAnswers && (
                                              <span style={{ fontSize: '0.65rem', color: s.textMuted, flexShrink: 0, transition: 'transform 0.2s', display: 'inline-block', transform: isExpanded ? 'rotate(180deg)' : 'none' }}>▼</span>
                                            )}
                                          </div>

                                          {/* Expanded: per-student Q&A answers */}
                                          {isExpanded && hasAnswers && (
                                            <div style={{ borderTop: `1px solid ${s.border}`, padding: '12px 14px', background: s.surface3 }}>
                                              <div style={{ fontSize: '0.68rem', fontWeight: 800, color: s.textMuted, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: 10 }}>📋 {st.name}'s Answers</div>
                                              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                                {st.answers.map((ans, ai) => {
                                                  const ansType = (ans.type || 'MCQ').toUpperCase();
                                                  const stuAns = ans.student_answer || '';
                                                  const corrAns = ans.correct_answer || ans.a || '';
                                                  const isCorrect = ans.is_correct || (stuAns && corrAns && stuAns.toLowerCase() === corrAns.toLowerCase());
                                                  return (
                                                    <div key={ai} style={{ background: isCorrect ? 'rgba(16,185,129,0.05)' : 'rgba(239,68,68,0.05)', border: `1px solid ${isCorrect ? 'rgba(16,185,129,0.25)' : 'rgba(239,68,68,0.2)'}`, borderRadius: 8, padding: '10px 12px' }}>
                                                      {/* Question */}
                                                      <div style={{ display: 'flex', gap: 6, marginBottom: 7, alignItems: 'flex-start' }}>
                                                        <span style={{ fontSize: '0.55rem', fontWeight: 700, textTransform: 'uppercase', flexShrink: 0, marginTop: 2, padding: '1px 5px', borderRadius: 3, background: 'rgba(124,58,237,0.1)', color: s.accLight, border: '1px solid rgba(124,58,237,0.2)' }}>
                                                          Q{ai + 1}
                                                        </span>
                                                        <span style={{ fontSize: '0.78rem', fontWeight: 600, color: s.textPrimary, lineHeight: 1.45 }}>{ans.q}</span>
                                                      </div>
                                                      {/* Options for MCQ */}
                                                      {ans.options && ans.options.length > 0 && (
                                                        <div style={{ paddingLeft: 4, display: 'flex', flexDirection: 'column', gap: 3, marginBottom: 8 }}>
                                                          {ans.options.map((opt, oi) => {
                                                            const isStudentChoice = opt === stuAns;
                                                            const isCorrectOpt = opt === corrAns;
                                                            let optBg = 'transparent', optBd = s.border, optColor = s.textSec;
                                                            if (isCorrectOpt && isStudentChoice) { optBg = 'rgba(16,185,129,0.12)'; optBd = 'rgba(16,185,129,0.4)'; optColor = '#10B981'; }
                                                            else if (isCorrectOpt) { optBg = 'rgba(16,185,129,0.07)'; optBd = 'rgba(16,185,129,0.3)'; optColor = '#10B981'; }
                                                            else if (isStudentChoice) { optBg = 'rgba(239,68,68,0.08)'; optBd = 'rgba(239,68,68,0.35)'; optColor = '#EF4444'; }
                                                            return (
                                                              <div key={oi} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: '0.7rem', padding: '3px 8px', borderRadius: 6, background: optBg, border: `1px solid ${optBd}`, color: optColor, fontWeight: (isStudentChoice || isCorrectOpt) ? 700 : 400 }}>
                                                                <span style={{ fontWeight: 700, minWidth: 16 }}>{['A', 'B', 'C', 'D'][oi]}.</span>
                                                                {opt}
                                                                {isStudentChoice && !isCorrectOpt && <span style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>← Student</span>}
                                                                {isCorrectOpt && <span style={{ marginLeft: 'auto', fontSize: '0.65rem' }}>✅ Correct</span>}
                                                              </div>
                                                            );
                                                          })}
                                                        </div>
                                                      )}
                                                      {/* Student answer vs correct answer */}
                                                      <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', alignItems: 'center' }}>
                                                        <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '3px 9px', borderRadius: 6, background: isCorrect ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${isCorrect ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`, color: isCorrect ? '#10B981' : '#EF4444' }}>
                                                          {isCorrect ? '✓' : '✗'} Student: {stuAns || '(no answer)'}
                                                        </span>
                                                        {!isCorrect && corrAns && (
                                                          <span style={{ fontSize: '0.65rem', fontWeight: 700, padding: '3px 9px', borderRadius: 6, background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.25)', color: '#10B981' }}>
                                                            ✓ Correct: {corrAns}
                                                          </span>
                                                        )}
                                                      </div>
                                                    </div>
                                                  );
                                                })}
                                              </div>
                                            </div>
                                          )}
                                        </div>
                                      );
                                    })}
                                  </div>
                                </>
                              ) : (
                                <div style={{ textAlign: 'center', color: s.textSec, padding: '16px 0', fontSize: '0.82rem' }}>
                                  No performance data found for this topic.
                                </div>
                              )}
                            </div>
                          )}
                        </div>
                      </div>
                    );
                  })}
                </div>
              )}
            </div>
          </div>
        </div>
      )}

      {/* ── Body: Sidebar + Main ─────────────────────────────────────────── */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden' }}>

        {/* ──────────── LEFT SIDEBAR ───────────────────────────────────── */}
        <aside style={{
          width: SIDEBAR_W, minWidth: SIDEBAR_W, background: s.surface,
          borderRight: `1px solid ${s.border}`,
          display: 'flex', flexDirection: 'column', overflow: 'hidden',
          transition: 'width 0.3s ease, min-width 0.3s ease',
          position: 'sticky', top: 57, height: 'calc(100vh - 57px)', overflowY: 'auto',
        }}>
          {/* Collapse toggle */}
          <button onClick={() => setSidebarCollapsed(c => !c)} title={sidebarCollapsed ? 'Expand sidebar' : 'Collapse sidebar'}
            style={{
              position: 'absolute', top: 16, right: -13, zIndex: 10,
              width: 26, height: 26, borderRadius: '50%',
              background: s.surface2, border: `1px solid ${s.border}`,
              cursor: 'pointer', color: s.textSec, fontSize: '0.7rem', fontWeight: 800,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>
            {sidebarCollapsed ? '›' : '‹'}
          </button>

          {sidebarCollapsed ? (
            /* Collapsed: show only year icon */
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 24, paddingTop: 24 }}>
              {['1', '2', '3'].map(yr => (
                <button key={yr} onClick={() => selectYear(yr)} title={YEAR_FULL[yr]}
                  style={{
                    background: year === yr ? 'rgba(124,58,237,0.2)' : 'transparent',
                    border: `1px solid ${year === yr ? s.acc : 'transparent'}`,
                    borderRadius: 10, width: 36, height: 36, cursor: 'pointer',
                    fontSize: '1.1rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
                    transition: 'all 0.2s',
                  }}>
                  {YEAR_ICONS[yr]}
                </button>
              ))}
              <div style={{ width: 1, height: 40, background: s.border }} />
              <span title="Timetable" style={{ fontSize: '1.2rem' }}>📅</span>
            </div>
          ) : (
            /* Expanded sidebar content */
            <div style={{ padding: '20px 16px', display: 'flex', flexDirection: 'column', gap: 0, flex: 1 }}>

              {/* Mentor info */}
              <div style={{ marginBottom: 20 }}>
                <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: s.textMuted, marginBottom: 8 }}>Logged in as</div>
                <div style={{ fontWeight: 700, fontSize: '0.9rem', color: s.textPrimary, marginBottom: 2 }}>{mentorName}</div>
                <div style={{ fontSize: '0.72rem', color: s.textSec }}>Mentor · Computer Science</div>
              </div>

              <div style={{ height: 1, background: s.border, marginBottom: 18 }} />

              {/* Active Topic indicator */}
              {todayActive && (
                <div style={{ marginBottom: 16 }}>
                  <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: s.textMuted, marginBottom: 8 }}>
                    📌 Today's Active Topic
                  </div>
                  <div style={{
                    background: 'rgba(124,58,237,0.08)',
                    border: `1px solid ${s.border}`,
                    borderRadius: 10, padding: '12px 14px',
                    position: 'relative',
                  }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', gap: 6, marginBottom: 6 }}>
                      <span style={{
                        fontSize: '0.58rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.08em',
                        padding: '2px 7px', borderRadius: 99,
                        background: 'rgba(16,185,129,0.1)',
                        border: '1px solid rgba(16,185,129,0.3)',
                        color: '#10B981',
                      }}>● ACTIVE</span>
                      {/* Deactivate button */}
                      <button
                        id="btn-deactivate-topic"
                        title="End active topic now"
                        onClick={async () => {
                          if (!window.confirm(`Deactivate "${todayActive.topic}" now? Students won't be able to take this quiz anymore.`)) return;
                          try {
                            const res = await fetch(
                              `/api/timetable/clear-today?year=${year}`,
                              { method: 'DELETE', headers: authHeaders() }
                            );
                            if (!res.ok) throw new Error('Failed');
                            setTodayActive(null);
                            addToast('✅ Topic deactivated. No active quiz now.', 'success');
                          } catch {
                            addToast('❌ Could not deactivate topic.', 'error');
                          }
                        }}
                        style={{
                          fontSize: '0.58rem', fontWeight: 800,
                          background: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)',
                          borderRadius: 6, padding: '3px 8px', cursor: 'pointer',
                          color: '#EF4444', fontFamily: 'inherit', transition: 'all 0.2s',
                          whiteSpace: 'nowrap', display: 'flex', alignItems: 'center', gap: 4,
                        }}
                        onMouseEnter={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.18)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.6)'; }}
                        onMouseLeave={e => { e.currentTarget.style.background = 'rgba(239,68,68,0.08)'; e.currentTarget.style.borderColor = 'rgba(239,68,68,0.3)'; }}
                      >
                        ⏹ End
                      </button>
                    </div>
                    <div style={{ fontSize: '0.78rem', fontWeight: 700, color: s.textPrimary, marginBottom: 3 }}>{todayActive.subject}</div>
                    <div style={{ fontSize: '0.72rem', color: s.textSec }}>{todayActive.topic}</div>
                    <div style={{ fontSize: '0.62rem', color: s.textMuted, marginTop: 4 }}>
                      {todayActive.date}
                      {todayActive.due_time && (
                        <span style={{ marginLeft: 6 }}>⏰ Until {to12hr(todayActive.due_time)}</span>
                      )}
                    </div>
                  </div>
                </div>
              )}


              <div style={{ height: 1, background: s.border, marginBottom: 18 }} />

              {/* ── Quick Actions in Sidebar ── Fix #2: disabled when 0 students */}
              <div style={{ fontSize: '0.62rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.1em', color: s.textMuted, marginBottom: 12 }}>⚡ Quick Actions</div>

              {/* Fix #2: Banner when no students in this year */}
              {hasNoStudents && (
                <div style={{
                  background: 'rgba(245,158,11,0.07)', border: '1px solid rgba(245,158,11,0.25)',
                  borderRadius: 10, padding: '10px 12px', marginBottom: 10,
                  fontSize: '0.72rem', color: '#F59E0B', fontWeight: 600, lineHeight: 1.5,
                  display: 'flex', alignItems: 'flex-start', gap: 8,
                }}>
                  <span style={{ fontSize: '1rem', flexShrink: 0 }}>⚠️</span>
                  <span>No students in <strong>{YEAR_FULL[year]}</strong>. Actions are unavailable.</span>
                </div>
              )}

              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>



                {/* Generate Report */}
                <button id="sidebar-btn-gen-report"
                  onClick={handleGenerateReport}
                  disabled={!!actionLoading}
                  style={{
                    background: 'rgba(124,58,237,0.06)', border: `1px solid ${s.border}`, color: s.textPrimary,
                    borderRadius: 10, padding: '11px 13px', fontWeight: 600, fontSize: '0.82rem',
                    textAlign: 'left', cursor: actionLoading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s', fontFamily: 'inherit',
                    opacity: (actionLoading && actionLoading !== 'report') || noQuizActive ? 0.38 : 1,
                    display: 'flex', alignItems: 'center', gap: 10,
                  }}
                  onMouseEnter={e => { if (!actionLoading) { e.currentTarget.style.background = 'rgba(124,58,237,0.14)'; e.currentTarget.style.borderColor = s.borderStrong; } }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.06)'; e.currentTarget.style.borderColor = s.border; }}>
                  <span style={{ fontSize: '1rem' }}>{actionLoading === 'report' ? '⌛' : '📄'}</span>
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700 }}>Generate Weak Report</div>
                    <div style={{ fontSize: '0.68rem', color: s.textSec, marginTop: 1 }}>
                      {noQuizActive ? 'No quiz active now' : hasNoStudents ? 'No students in this year' : 'View cohort weak summary'}
                    </div>
                  </div>
                </button>

                {/* Send Report Email */}
                <button id="sidebar-btn-send-report"
                  onClick={handleSendReport}
                  disabled={!!actionLoading}
                  style={{
                    background: 'rgba(16,185,129,0.06)', border: '1px solid rgba(16,185,129,0.2)', color: s.textPrimary,
                    borderRadius: 10, padding: '11px 13px', fontWeight: 600, fontSize: '0.82rem',
                    textAlign: 'left', cursor: actionLoading ? 'not-allowed' : 'pointer',
                    transition: 'all 0.2s', fontFamily: 'inherit',
                    opacity: (actionLoading && actionLoading !== 'sendreport') || noQuizActive ? 0.38 : 1,
                    display: 'flex', alignItems: 'center', gap: 10,
                  }}
                  onMouseEnter={e => { if (!actionLoading) { e.currentTarget.style.background = 'rgba(16,185,129,0.14)'; e.currentTarget.style.borderColor = '#10B981'; } }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(16,185,129,0.06)'; e.currentTarget.style.borderColor = 'rgba(16,185,129,0.2)'; }}>
                  <span style={{ fontSize: '1rem' }}>{actionLoading === 'sendreport' ? '⌛' : '📊'}</span>
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700 }}>Send Report to Email</div>
                    <div style={{ fontSize: '0.68rem', color: s.textSec, marginTop: 1 }}>
                      {noQuizActive ? 'No quiz active now' : hasNoStudents ? 'No students in this year' : 'Email full performance report'}
                    </div>
                  </div>
                </button>

                <div style={{ height: 1, background: s.border, margin: '4px 0' }} />

                {/* Timetable Settings → opens modal */}
                <button id="sidebar-btn-timetable"
                  onClick={() => setTimetableModal(true)}
                  style={{
                    background: 'rgba(124,58,237,0.08)', border: `1px solid rgba(124,58,237,0.3)`, color: s.accLight,
                    borderRadius: 10, padding: '11px 13px', fontWeight: 700, fontSize: '0.82rem',
                    textAlign: 'left', cursor: 'pointer', transition: 'all 0.2s', fontFamily: 'inherit',
                    display: 'flex', alignItems: 'center', gap: 10,
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.18)'; e.currentTarget.style.borderColor = s.acc; e.currentTarget.style.color = s.textPrimary; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.08)'; e.currentTarget.style.borderColor = 'rgba(124,58,237,0.3)'; e.currentTarget.style.color = s.accLight; }}>
                  <span style={{ fontSize: '1.1rem' }}>📅</span>
                  <div>
                    <div style={{ fontSize: '0.82rem', fontWeight: 700 }}>Timetable Settings</div>
                    <div style={{ fontSize: '0.68rem', color: s.textSec, marginTop: 1 }}>Edit weekly schedule</div>
                  </div>
                </button>

              </div>

            </div>
          )}
        </aside>

        {/* ── Timetable Full-Screen Modal ────────────────────────────────── */}
        {timetableModal && (
          <div style={{
            position: 'fixed', inset: 0, zIndex: 600,
            background: 'rgba(4,4,12,0.85)', backdropFilter: 'blur(14px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            padding: 24, animation: 'fadeInBg 0.3s ease',
          }} onClick={() => { if (!timetableEditMode) setTimetableModal(false); }}>
            <div style={{
              background: s.surface, border: `1px solid ${s.borderStrong}`,
              borderRadius: 24, width: '100%', maxWidth: 900,
              maxHeight: '90vh', overflowY: 'auto',
              boxShadow: '0 32px 100px rgba(0,0,0,0.8), 0 0 0 1px rgba(124,58,237,0.2)',
              animation: 'modalSlideUp 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
              position: 'relative',
            }} onClick={e => e.stopPropagation()}>

              {/* Top gradient bar */}
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '24px 24px 0 0' }} />

              {/* Modal Header */}
              <div style={{
                padding: '28px 32px 20px',
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                borderBottom: `1px solid ${s.border}`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                  <div style={{
                    width: 46, height: 46, borderRadius: 14,
                    background: 'rgba(124,58,237,0.12)', border: `1px solid ${s.border}`,
                    display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem',
                  }}>📅</div>
                  <div>
                    <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.2rem', fontWeight: 800, color: s.textPrimary }}>Weekly Timetable</div>
                    <div style={{ fontSize: '0.75rem', color: s.textSec, marginTop: 2 }}>{YEAR_FULL[year]} · Subject & Topic schedule</div>
                  </div>
                </div>
                <button onClick={() => { setTimetableEditMode(false); setTimetableModal(false); }}
                  style={{
                    width: 38, height: 38, borderRadius: '50%', background: 'rgba(255,255,255,0.06)',
                    border: `1px solid ${s.border}`, cursor: 'pointer', color: s.textSec,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: '1rem', fontWeight: 700, transition: 'all 0.2s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = s.textPrimary; }}
                  onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = s.textSec; }}>
                  ✕
                </button>
              </div>

              {/* Edit / View toggle */}
              <div style={{ padding: '16px 32px', display: 'flex', alignItems: 'center', justifyContent: 'space-between', borderBottom: `1px solid ${s.border}`, background: s.surface2 }}>
                <div style={{ fontSize: '0.75rem', color: s.textSec }}>
                  {timetableEditMode ? '✏️ Editing — fill in Subject & Topic for each slot, then save.' : '👁 View mode — click Edit to modify.'}
                </div>
                <button onClick={() => setTimetableEditMode(m => !m)}
                  style={{
                    background: timetableEditMode ? 'rgba(239,68,68,0.1)' : 'rgba(124,58,237,0.1)',
                    border: `1px solid ${timetableEditMode ? 'rgba(239,68,68,0.35)' : s.borderStrong}`,
                    borderRadius: 8, padding: '7px 18px', fontSize: '0.78rem', fontWeight: 700,
                    color: timetableEditMode ? '#EF4444' : s.accLight, cursor: 'pointer', fontFamily: 'inherit',
                    transition: 'all 0.2s',
                  }}>
                  {timetableEditMode ? '✕ Cancel Edit' : '✏️ Edit Timetable'}
                </button>
              </div>

              {/* Timetable body */}
              <div style={{ padding: '28px 32px' }}>
                <SidebarTimetable
                  timetable={timetable}
                  year={year}
                  editMode={timetableEditMode}
                  setTimetable={setTimetable}
                  onSave={async () => { await handleSaveTimetable(); setTimetableEditMode(false); setTimetableModal(false); }}
                  saving={savingTimetable}
                />
              </div>

            </div>
          </div>
        )}

        {/* ──────────── MAIN CONTENT ──────────────────────────────────── */}
        <main style={{ flex: 1, overflowY: 'auto', padding: '32px 28px', maxWidth: '100%' }}>

          {/* Welcome — first-time: "Welcome", returning: "Welcome Back" */}
          <div style={{ marginBottom: 32 }}>
            <h1 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.9rem', fontWeight: 800, marginBottom: 4 }}>
              {isReturningMentor ? 'Welcome Back, ' : 'Welcome, '}
              <span style={{ background: s.grad, WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>{mentorName}</span>
              {isReturningMentor ? ' ☕' : ' 🎉'}
            </h1>
            <p style={{ color: s.textSec, fontSize: '0.9rem' }}>
              {isReturningMentor
                ? <>Managing <strong style={{ color: s.textPrimary }}>{YEAR_FULL[year]}</strong> — curriculum, timetable, and performance.</>
                : <>You’re all set! Start by setting up your <strong style={{ color: s.textPrimary }}>Timetable</strong> and activating today’s topic.📚</>}
            </p>
          </div>

          {/* Metrics — Total Students clickable; Weak/Missed only when active topic */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 18, marginBottom: 20 }}>
            <MetricCard
              label="Total Students"
              value={metrics.total}
              desc={metrics.total > 0 ? 'Click to view all students' : 'learners in this year'}
              color="linear-gradient(135deg,#7C3AED,#EC4899)"
              clickable={metrics.total > 0}
              onClick={metrics.total > 0 ? () => setShowAllStudents(true) : undefined}
            />
            <MetricCard
              label="Flagged Weak"
              value={displayWeak}
              desc={todayActive ? 'Scoring below 50%' : 'Set a topic to track'}
              color="linear-gradient(135deg,#EF4444,#F97316)"
              clickable={todayActive && displayWeak > 0}
              onClick={todayActive && displayWeak > 0 ? () => setModal('weak') : undefined}
            />
            <MetricCard
              label="Missed Check-in"
              value={displayMissed}
              desc={todayActive ? 'No quiz submitted today' : 'Set a topic to track'}
              color="linear-gradient(135deg,#F59E0B,#EF4444)"
              clickable={todayActive && displayMissed > 0}
              onClick={todayActive && displayMissed > 0 ? () => setModal('missed') : undefined}
            />
          </div>

          {/* Overall Weak Percentage bar — only show when quiz is active */}
          {todayActive ? (
            <WeakPercentBar total={metrics.total} weak={metrics.weak} />
          ) : (
            <div style={{
              background: s.surface, border: `1px solid ${s.border}`, borderRadius: 18, padding: '16px 24px',
              boxShadow: s.cardShadow, marginBottom: 28,
              display: 'flex', alignItems: 'center', gap: 12,
            }}>
              <div style={{ fontSize: '1.4rem' }}>📊</div>
              <div>
                <div style={{ fontSize: '0.7rem', fontWeight: 700, color: s.textSec, textTransform: 'uppercase', letterSpacing: '0.1em', marginBottom: 2 }}>Overall Weak Percentage</div>
                <div style={{ fontSize: '0.8rem', color: s.textMuted }}>No quiz activated — set a topic to track student performance</div>
              </div>
            </div>
          )}

          {/* Today's Topic Override — full width */}
          <div style={{ marginBottom: 28 }}>
            <div style={{ ...cardStyle, display: 'flex', flexDirection: 'column' }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '18px 18px 0 0' }} />
              <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.1rem', fontWeight: 700, marginBottom: 18 }}>🚀 Set Today's Active Topic</h2>
              <form onSubmit={handleSetTopic} id="override-form" style={{ display: 'flex', flexDirection: 'column', gap: 14, flex: 1 }}>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 6 }}>
                      Subject
                      {availableSubjects.length > 0 && (
                        <span style={{ fontSize: '0.58rem', color: s.accLight, fontWeight: 600, marginLeft: 6, textTransform: 'none' }}>
                          · From your timetable
                        </span>
                      )}
                    </label>
                    <select id="override-subject" required value={overrideForm.subject}
                      onChange={e => setOverrideForm(f => ({ ...f, subject: e.target.value, topic: '' }))}
                      disabled={availableSubjects.length === 0}
                      style={{ ...inputStyle, appearance: 'none', opacity: availableSubjects.length === 0 ? 0.5 : 1, cursor: availableSubjects.length === 0 ? 'not-allowed' : 'pointer' }}>
                      {availableSubjects.length === 0
                        ? <option value="">Set timetable first ↑</option>
                        : <>
                          <option value="" disabled>Select Subject</option>
                          {availableSubjects.map(sub => <option key={sub} value={sub}>{sub}</option>)}
                        </>
                      }
                    </select>
                  </div>
                  <div>
                    <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 6 }}>
                      Topic
                      {timetableTopics.length > 0 && (
                        <span style={{ fontSize: '0.58rem', color: s.accLight, fontWeight: 600, marginLeft: 6, textTransform: 'none' }}>
                          · From your timetable
                        </span>
                      )}
                    </label>
                    {timetableTopics.length > 0 ? (
                      <select id="override-topic" required value={overrideForm.topic}
                        onChange={e => setOverrideForm(f => ({ ...f, topic: e.target.value }))}
                        style={{ ...inputStyle, appearance: 'none' }}>
                        <option value="" disabled>Select Topic</option>
                        {timetableTopics.map(tp => <option key={tp} value={tp}>{tp}</option>)}
                      </select>
                    ) : (
                      <input id="override-topic" type="text"
                        placeholder={overrideForm.subject ? 'Enter topic manually' : '— select subject first —'}
                        required value={overrideForm.topic}
                        onChange={e => setOverrideForm(f => ({ ...f, topic: e.target.value }))}
                        style={{ ...inputStyle, opacity: overrideForm.subject ? 1 : 0.5 }}
                        disabled={!overrideForm.subject} />
                    )}
                  </div>
                </div>
                <div>
                  <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 8 }}>Question Config</label>
                  <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 10 }}>
                    {[{ label: 'MCQ', key: 'mcq', id: 'override-count-mcq' }, { label: 'T/F', key: 'tf', id: 'override-count-tf' }, { label: 'Fill', key: 'fill', id: 'override-count-fill' }, { label: 'Short Ans', key: 'shortanswer', id: 'override-count-short' }].map(f => (
                      <div key={f.key}>
                        <label style={{ display: 'block', fontSize: '0.62rem', color: s.textSec, marginBottom: 5 }}>{f.label}</label>
                        <input type="number" id={f.id} min={0} max={15} value={overrideForm[f.key]}
                          onChange={e => setOverrideForm(prev => ({ ...prev, [f.key]: parseInt(e.target.value) || 0 }))}
                          style={inputStyle} />
                      </div>
                    ))}
                  </div>
                </div>
                {/* Due Date & Time */}
                <div>
                  <label style={{ display: 'block', fontSize: '0.65rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textSec, marginBottom: 8 }}>
                    ⏰ Quiz Due Date & Time
                    <span style={{ fontSize: '0.58rem', color: s.accLight, fontWeight: 600, marginLeft: 6, textTransform: 'none' }}>
                      · Quiz inactive after this
                    </span>
                  </label>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 10 }}>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.62rem', color: s.textSec, marginBottom: 5 }}>Due Date</label>
                      <input type="date" id="override-due-date" value={overrideForm.dueDate}
                        onChange={e => setOverrideForm(f => ({ ...f, dueDate: e.target.value }))}
                        min={new Date().toISOString().split('T')[0]}
                        style={{ ...inputStyle, colorScheme: 'dark' }} />
                    </div>
                    <div>
                      <label style={{ display: 'block', fontSize: '0.62rem', color: s.textSec, marginBottom: 5 }}>
                        Due Time
                        {overrideForm.dueTime && (
                          <span style={{ marginLeft: 6, color: s.accLight, fontWeight: 700, fontSize: '0.6rem' }}>
                            → {to12hr(overrideForm.dueTime)}
                          </span>
                        )}
                      </label>
                      {/* Custom 12-hour AM/PM Time Picker */}
                      {(() => {
                        const [hStr, mStr] = (overrideForm.dueTime || '00:00').split(':');
                        let h24 = parseInt(hStr, 10);
                        const min = mStr || '00';
                        const ampm = h24 >= 12 ? 'PM' : 'AM';
                        let h12 = h24 % 12 || 12;

                        const update12hr = (newH12, newMin, newAmpm) => {
                          let h = parseInt(newH12, 10) % 12;
                          if (newAmpm === 'PM') h += 12;
                          const hh = String(h).padStart(2, '0');
                          const mm = String(newMin).padStart(2, '0');
                          setOverrideForm(f => ({ ...f, dueTime: `${hh}:${mm}` }));
                        };

                        return (
                          <div id="override-due-time" style={{ display: 'flex', gap: 6, alignItems: 'center' }}>
                            {/* Hour */}
                            <select
                              value={h12}
                              onChange={e => update12hr(e.target.value, min, ampm)}
                              style={{ ...inputStyle, flex: 1, appearance: 'none', textAlign: 'center', padding: '11px 8px', cursor: 'pointer' }}
                            >
                              {[...Array(12)].map((_, i) => {
                                const v = i + 1;
                                return <option key={v} value={v}>{String(v).padStart(2, '0')}</option>;
                              })}
                            </select>
                            <span style={{ color: s.textSec, fontWeight: 700, fontSize: '1rem', flexShrink: 0 }}>:</span>
                            {/* Minute */}
                            <select
                              value={parseInt(min, 10)}
                              onChange={e => update12hr(h12, e.target.value, ampm)}
                              style={{ ...inputStyle, flex: 1, appearance: 'none', textAlign: 'center', padding: '11px 8px', cursor: 'pointer' }}
                            >
                              {[0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55].map(v => (
                                <option key={v} value={v}>{String(v).padStart(2, '0')}</option>
                              ))}
                            </select>
                            {/* AM/PM Toggle */}
                            <div style={{ display: 'flex', borderRadius: 8, overflow: 'hidden', border: `1px solid ${s.border}`, flexShrink: 0 }}>
                              {['AM', 'PM'].map(ap => (
                                <button
                                  key={ap}
                                  type="button"
                                  onClick={() => update12hr(h12, min, ap)}
                                  style={{
                                    padding: '10px 12px', fontWeight: 700, fontSize: '0.75rem',
                                    background: ampm === ap ? s.acc : s.surface3,
                                    color: ampm === ap ? '#fff' : s.textSec,
                                    border: 'none', cursor: 'pointer', fontFamily: 'inherit',
                                    transition: 'all 0.15s',
                                  }}
                                >
                                  {ap}
                                </button>
                              ))}
                            </div>
                          </div>
                        );
                      })()}
                    </div>
                  </div>
                </div>
                <button type="submit" id="btn-set-topic" disabled={submitting}
                  style={{
                    background: submitting ? s.surface3 : s.grad, color: '#fff', fontWeight: 700, fontSize: '0.9rem',
                    padding: '13px', border: 'none', borderRadius: 12, cursor: submitting ? 'default' : 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8,
                    fontFamily: 'inherit', opacity: submitting ? 0.7 : 1, marginTop: 4,
                  }}>
                  {submitting ? '⌛ Activating…' : '✓ Activate Today\'s Topic'}
                </button>
              </form>
            </div>
          </div>


          {/* Student Performance Monitor */}
          <div style={{ ...cardStyle }}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '18px 18px 0 0' }} />
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 22 }}>
              <div>
                <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.1rem', fontWeight: 700, marginBottom: 6 }}>Student Performance Monitor</div>
                <span id="cohort-display-label" style={{
                  fontSize: '0.68rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase',
                  color: s.accLight, background: 'rgba(124,58,237,0.12)', border: `1px solid ${s.acc}`,
                  padding: '3px 10px', borderRadius: 99, display: 'inline-block',
                }}>
                  {YEAR_FULL[year]}
                </span>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                <button onClick={() => loadCohort(year)}
                  style={{
                    background: s.surface2, border: `1px solid ${s.border}`, borderRadius: 8,
                    padding: '6px 14px', fontSize: '0.75rem', fontWeight: 600, color: s.textSec,
                    cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.2s',
                  }}
                  onMouseEnter={e => { e.currentTarget.style.color = '#fff'; e.currentTarget.style.borderColor = s.borderStrong; }}
                  onMouseLeave={e => { e.currentTarget.style.color = s.textSec; e.currentTarget.style.borderColor = s.border; }}>
                  {loadingCohort ? '⌛ Loading…' : '↻ Refresh'}
                </button>
                <span style={{ fontSize: '0.78rem', color: s.textMuted }}>Live data</span>
              </div>
            </div>

            {loadingCohort ? (
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', padding: '40px 0', color: s.textSec, gap: 10 }}>
                <div style={{ width: 36, height: 36, border: `3px solid ${s.border}`, borderTop: `3px solid ${s.acc}`, borderRadius: '50%', animation: 'spin 0.9s linear infinite' }} />
                <div style={{ fontSize: '0.85rem' }}>Loading cohort data…</div>
              </div>
            ) : noQuizActive ? (
              /* No active quiz — show clean message */
              <div style={{ textAlign: 'center', padding: '52px 0 44px' }}>
                <div style={{ fontSize: '3rem', marginBottom: 14 }}>📊</div>
                <div style={{ fontWeight: 700, fontSize: '1.05rem', color: s.textPrimary, marginBottom: 8 }}>
                  No quiz currently active
                </div>
                <div style={{ fontSize: '0.82rem', color: s.textMuted, maxWidth: 340, margin: '0 auto', lineHeight: 1.7 }}>
                  To monitor student performance, activate a topic from
                  <strong style={{ color: s.accLight }}> "Set Today's Active Topic" </strong>
                  above.
                </div>
              </div>
            ) : students.length === 0 ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: s.textSec }}>
                <div style={{ fontSize: '2.5rem', marginBottom: 12 }}>📭</div>
                <div style={{ fontWeight: 600 }}>No students found for {YEAR_FULL[year]}.</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 6 }}>
                {/* Table header */}
                <div style={{
                  display: 'grid', gridTemplateColumns: '32px minmax(120px,1.5fr) 100px minmax(100px,1fr) 140px 80px',
                  gap: '0 12px', padding: '8px 16px',
                  borderBottom: `1px solid ${s.border}`,
                }}>
                  {['', 'Student', 'Reg No.', 'Topic', 'Status', ''].map((h, idx) => (
                    <div key={idx} style={{ fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: s.textMuted }}>{h}</div>
                  ))}
                </div>
                {students.map((st, i) => {
                  const cfg = {
                    good: { dot: '#10B981', bg: 'rgba(16,185,129,0.08)', bd: 'rgba(16,185,129,0.22)', clr: '#10B981', label: 'Good' },
                    weak: { dot: '#EF4444', bg: 'rgba(239,68,68,0.08)', bd: 'rgba(239,68,68,0.22)', clr: '#EF4444', label: 'Weak' },
                    missed: { dot: '#F59E0B', bg: 'rgba(245,158,11,0.06)', bd: 'rgba(245,158,11,0.18)', clr: '#F59E0B', label: 'Missed' },
                    not_understood: { dot: '#8B5CF6', bg: 'rgba(139,92,246,0.08)', bd: 'rgba(139,92,246,0.25)', clr: '#8B5CF6', label: 'Not Understandable' },
                  };
                  const c = cfg[st.status] || cfg.missed;
                  const canViewAnswers = st.status === 'good' || st.status === 'weak' || st.status === 'not_understood';
                  const isLoadingThis = loadingAnswers === st.regno;
                  return (
                    <div key={i}
                      style={{
                        display: 'grid', gridTemplateColumns: '32px minmax(120px,1.5fr) 100px minmax(100px,1fr) 140px 80px',
                        gap: '0 12px', padding: '11px 16px', borderRadius: 10,
                        alignItems: 'center', transition: 'background 0.15s',
                        cursor: 'default',
                      }}
                      onMouseEnter={e => e.currentTarget.style.background = 'rgba(124,58,237,0.05)'}
                      onMouseLeave={e => e.currentTarget.style.background = ''}>
                      {/* Avatar */}
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%', background: s.grad,
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontSize: '0.75rem', fontWeight: 800, color: '#fff', flexShrink: 0,
                      }}>{(st.name || 'S')[0].toUpperCase()}</div>
                      {/* Name */}
                      <div>
                        <div style={{ fontSize: '0.875rem', fontWeight: 700, color: s.textPrimary, lineHeight: 1.2 }}>{st.name}</div>
                      </div>
                      {/* Reg No */}
                      <div style={{ fontSize: '0.72rem', color: s.textMuted, fontFamily: 'monospace' }}>{st.regno}</div>
                      {/* Topic */}
                      <div style={{ fontSize: '0.78rem', color: s.textSec, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{st.topic}</div>
                      {/* Status */}
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6 }}>
                        <div style={{ width: 7, height: 7, borderRadius: '50%', background: c.dot, boxShadow: `0 0 6px ${c.dot}88`, flexShrink: 0 }} />
                        <span style={{ fontSize: '0.72rem', fontWeight: 700, color: c.clr }}>{c.label}</span>
                      </div>
                      {/* View Answers button */}
                      <div style={{ display: 'flex', justifyContent: 'flex-end' }}>
                        {canViewAnswers ? (
                          <button
                            onClick={async () => {
                              if (isLoadingThis) return;
                              setLoadingAnswers(st.regno);
                              try {
                                const res = await fetch(
                                  `/api/mentors/student-attempts?regno=${encodeURIComponent(st.regno)}&topic=${encodeURIComponent(todayActive?.topic || st.topic)}`,
                                  { headers: authHeaders() }
                                );
                                const data = await res.json();
                                setQuizAnswerModal({ student: st, data });
                              } catch (e) {
                                addToast('Could not load answers: ' + e.message, 'error');
                              } finally {
                                setLoadingAnswers(null);
                              }
                            }}
                            style={{
                              fontSize: '0.65rem', fontWeight: 700,
                              background: 'rgba(124,58,237,0.08)', border: '1px solid rgba(124,58,237,0.25)',
                              borderRadius: 6, padding: '4px 10px', cursor: isLoadingThis ? 'default' : 'pointer',
                              color: s.accLight, fontFamily: 'inherit', transition: 'all 0.2s',
                              opacity: isLoadingThis ? 0.6 : 1, whiteSpace: 'nowrap',
                            }}
                            onMouseEnter={e => { if (!isLoadingThis) e.currentTarget.style.background = 'rgba(124,58,237,0.18)'; }}
                            onMouseLeave={e => e.currentTarget.style.background = 'rgba(124,58,237,0.08)'}
                          >
                            {isLoadingThis ? '⌛…' : '📖 Answers'}
                          </button>
                        ) : (
                          <span style={{ fontSize: '0.62rem', color: s.textMuted }}>—</span>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </div>

        </main>
      </div>

      {/* Modals */}

      {/* ── Quiz Answer Viewer Modal (mentor sees student's Q&A) ── */}
      {quizAnswerModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 9999,
          background: 'rgba(4,4,12,0.88)', backdropFilter: 'blur(16px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
          animation: 'fadeInBg 0.25s ease',
        }} onClick={() => setQuizAnswerModal(null)}>
          <div style={{
            background: s.surface, border: `1px solid ${s.borderStrong}`,
            borderRadius: 24, width: '100%', maxWidth: 680,
            maxHeight: '88vh', overflowY: 'auto', position: 'relative',
            boxShadow: '0 32px 100px rgba(0,0,0,0.85)',
            animation: 'modalSlideUp 0.35s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          }} onClick={e => e.stopPropagation()}>
            {/* Gradient bar */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '24px 24px 0 0' }} />
            {/* Header */}
            <div style={{ padding: '28px 28px 18px', borderBottom: `1px solid ${s.border}`, display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
                <div style={{ width: 48, height: 48, borderRadius: 14, background: 'rgba(124,58,237,0.12)', border: `1px solid ${s.border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.4rem', flexShrink: 0 }}>📖</div>
                <div>
                  <div style={{ fontFamily: "'Outfit',sans-serif", fontSize: '1.1rem', fontWeight: 800, color: s.textPrimary }}>
                    {quizAnswerModal.student.name}'s Quiz Answers
                  </div>
                  <div style={{ fontSize: '0.73rem', color: s.textSec, marginTop: 3 }}>
                    {quizAnswerModal.data.topic} · {quizAnswerModal.data.subject || 'N/A'} · {quizAnswerModal.data.date}
                  </div>
                </div>
              </div>
              <button onClick={() => setQuizAnswerModal(null)} style={{ width: 34, height: 34, borderRadius: '50%', background: 'rgba(255,255,255,0.06)', border: `1px solid ${s.border}`, cursor: 'pointer', color: s.textSec, fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center', transition: 'all 0.2s' }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = s.textPrimary; }}
                onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = s.textSec; }}>✕</button>
            </div>

            {/* Score summary */}
            {quizAnswerModal.data.found && (
              <div style={{ padding: '14px 28px', borderBottom: `1px solid ${s.border}`, background: s.surface2, display: 'flex', gap: 16, alignItems: 'center' }}>
                {[
                  { label: 'Score', val: quizAnswerModal.data.score, color: s.accLight, bg: 'rgba(124,58,237,0.1)' },
                  { label: 'Percentage', val: `${quizAnswerModal.data.percentage}%`, color: quizAnswerModal.data.percentage >= 50 ? '#10B981' : '#EF4444', bg: quizAnswerModal.data.percentage >= 50 ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)' },
                  { label: 'Correct', val: (quizAnswerModal.data.answers || []).filter(a => a.is_correct).length, color: '#10B981', bg: 'rgba(16,185,129,0.08)' },
                  { label: 'Wrong', val: (quizAnswerModal.data.answers || []).filter(a => !a.is_correct).length, color: '#EF4444', bg: 'rgba(239,68,68,0.08)' },
                ].map(b => (
                  <div key={b.label} style={{ background: b.bg, borderRadius: 10, padding: '8px 16px', textAlign: 'center' }}>
                    <div style={{ fontSize: '1.05rem', fontWeight: 900, color: b.color, fontFamily: "'Outfit',sans-serif" }}>{b.val}</div>
                    <div style={{ fontSize: '0.6rem', color: s.textMuted, marginTop: 1 }}>{b.label}</div>
                  </div>
                ))}
              </div>
            )}

            {/* Body */}
            <div style={{ padding: '20px 28px', display: 'flex', flexDirection: 'column', gap: 12 }}>
              {!quizAnswerModal.data.found ? (
                <div style={{ textAlign: 'center', padding: '48px 0' }}>
                  <div style={{ fontSize: '3rem', marginBottom: 12 }}>📭</div>
                  <div style={{ fontWeight: 700, color: s.textPrimary, marginBottom: 6 }}>No Quiz Attempt Found</div>
                  <div style={{ fontSize: '0.82rem', color: s.textMuted }}>{quizAnswerModal.data.message}</div>
                </div>
              ) : (quizAnswerModal.data.answers || []).map((ans, qi) => {
                const hasMCQOptions = (ans.type === 'MCQ' || ans.type === 'TF') && ans.options && ans.options.length > 0;
                return (
                  <div key={qi} style={{
                    background: s.surface2,
                    border: `1px solid ${ans.is_correct ? 'rgba(16,185,129,0.3)' : 'rgba(239,68,68,0.3)'}`,
                    borderRadius: 16, padding: '18px 20px',
                    position: 'relative', overflow: 'hidden',
                  }}>
                    {/* Left accent bar */}
                    <div style={{ position: 'absolute', top: 0, left: 0, bottom: 0, width: 4, borderRadius: '16px 0 0 16px', background: ans.is_correct ? 'linear-gradient(180deg,#10B981,#059669)' : 'linear-gradient(180deg,#EF4444,#DC2626)' }} />

                    {/* Question header */}
                    <div style={{ display: 'flex', gap: 10, marginBottom: 14, alignItems: 'flex-start', paddingLeft: 12 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: 6, flexShrink: 0, paddingTop: 2 }}>
                        <span style={{ fontSize: '0.7rem', fontWeight: 900, color: s.textMuted, background: 'rgba(255,255,255,0.06)', border: `1px solid ${s.border}`, borderRadius: 6, padding: '2px 8px' }}>Q{qi + 1}</span>
                        <span style={{ fontSize: '0.52rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.07em', padding: '2px 8px', borderRadius: 4, background: ans.type === 'MCQ' ? 'rgba(124,58,237,0.18)' : ans.type === 'TF' ? 'rgba(16,185,129,0.18)' : 'rgba(245,158,11,0.18)', color: ans.type === 'MCQ' ? s.accLight : ans.type === 'TF' ? '#10B981' : '#F59E0B', border: `1px solid ${ans.type === 'MCQ' ? 'rgba(124,58,237,0.35)' : ans.type === 'TF' ? 'rgba(16,185,129,0.35)' : 'rgba(245,158,11,0.35)'}` }}>{ans.type === 'MCQ' ? '⊙ MCQ' : ans.type === 'TF' ? '⇌ T/F' : '✏ Fill'}</span>
                      </div>
                      <div style={{ fontSize: '0.9rem', fontWeight: 700, color: s.textPrimary, lineHeight: 1.55 }}>{ans.q}</div>
                    </div>

                    {/* MCQ / TF: show all options */}
                    {hasMCQOptions ? (
                      <div style={{ paddingLeft: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                        <div style={{ fontSize: '0.6rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.07em', color: s.textMuted, marginBottom: 2 }}>Options</div>
                        {ans.options.map((opt, oi) => {
                          const isStudentPick = opt.trim().toLowerCase() === (ans.student_answer || '').trim().toLowerCase();
                          const isCorrect = opt.trim().toLowerCase() === (ans.correct_answer || '').trim().toLowerCase();
                          let bg = 'rgba(255,255,255,0.03)';
                          let border = s.border;
                          let color = s.textSec;
                          let icon = null;
                          if (isCorrect && isStudentPick) { bg = 'rgba(16,185,129,0.15)'; border = 'rgba(16,185,129,0.5)'; color = '#10B981'; icon = '✓'; }
                          else if (isCorrect) { bg = 'rgba(16,185,129,0.1)'; border = 'rgba(16,185,129,0.4)'; color = '#10B981'; icon = '✓'; }
                          else if (isStudentPick) { bg = 'rgba(239,68,68,0.1)'; border = 'rgba(239,68,68,0.4)'; color = '#EF4444'; icon = '✗'; }
                          return (
                            <div key={oi} style={{ display: 'flex', alignItems: 'center', gap: 10, background: bg, border: `1px solid ${border}`, borderRadius: 10, padding: '8px 14px', transition: 'all 0.15s' }}>
                              <span style={{ width: 22, height: 22, borderRadius: '50%', border: `1.5px solid ${border}`, display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '0.65rem', fontWeight: 900, color, flexShrink: 0, background: icon ? bg : 'transparent' }}>
                                {icon || String.fromCharCode(65 + oi)}
                              </span>
                              <span style={{ fontSize: '0.84rem', fontWeight: icon ? 700 : 500, color: icon ? color : s.textSec, flex: 1 }}>{opt}</span>
                              {isStudentPick && !isCorrect && <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#EF4444', background: 'rgba(239,68,68,0.15)', padding: '2px 7px', borderRadius: 4 }}>Student's Pick</span>}
                              {isCorrect && <span style={{ fontSize: '0.58rem', fontWeight: 800, color: '#10B981', background: 'rgba(16,185,129,0.15)', padding: '2px 7px', borderRadius: 4 }}>Correct{isStudentPick ? ' ✓ Picked' : ''}</span>}
                            </div>
                          );
                        })}
                      </div>
                    ) : (
                      /* FILL: two-column student vs correct */
                      <div style={{ paddingLeft: 12, display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8 }}>
                        <div style={{ background: ans.is_correct ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${ans.is_correct ? 'rgba(16,185,129,0.35)' : 'rgba(239,68,68,0.35)'}`, borderRadius: 10, padding: '9px 14px' }}>
                          <div style={{ fontSize: '0.58rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: ans.is_correct ? '#10B981' : '#EF4444', marginBottom: 4 }}>{ans.is_correct ? '✓ Student — Correct' : '✗ Student — Wrong'}</div>
                          <div style={{ fontSize: '0.88rem', fontWeight: 700, color: s.textPrimary }}>{ans.student_answer || '—'}</div>
                        </div>
                        <div style={{ background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.3)', borderRadius: 10, padding: '9px 14px' }}>
                          <div style={{ fontSize: '0.58rem', fontWeight: 800, textTransform: 'uppercase', letterSpacing: '0.06em', color: '#10B981', marginBottom: 4 }}>✓ Correct Answer</div>
                          <div style={{ fontSize: '0.88rem', fontWeight: 700, color: s.textPrimary }}>{ans.correct_answer}</div>
                        </div>
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      )}

      {modal === 'weak' && (
        <StudentListModal
          title="Flagged Weak Students"
          subtitle={`Scored below 50% on today's quiz — ${YEAR_FULL[year]}`}
          icon="⚠️"
          students={weakStudents}
          color="linear-gradient(135deg,#EF4444,#F97316)"
          onClose={() => setModal(null)}
        />
      )}
      {modal === 'missed' && (
        <StudentListModal
          title="Missed Quiz Students"
          subtitle={`Did not attempt today's quiz — ${YEAR_FULL[year]}`}
          icon="🔴"
          students={missedStudents}
          color="linear-gradient(135deg,#F59E0B,#EF4444)"
          onClose={() => setModal(null)}
        />
      )}
      {showAllStudents && (
        <StudentListModal
          title="All Students"
          subtitle={`${YEAR_FULL[year]} — complete student list`}
          icon="🎓"
          students={students}
          color="linear-gradient(135deg,#7C3AED,#EC4899)"
          onClose={() => setShowAllStudents(false)}
        />
      )}

      {/* ── Question Mode Chooser Modal ─────────────────────────────────── */}
      {qModeModal && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 9998,
          background: 'rgba(0,0,0,0.88)', backdropFilter: 'blur(20px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
        }} onClick={() => setQModeModal(false)}>
          <div style={{
            background: s.surface, border: `1px solid ${s.border}`,
            borderRadius: 28, padding: '40px 36px', maxWidth: 540, width: '100%',
            boxShadow: '0 40px 100px rgba(0,0,0,0.9)', position: 'relative',
            animation: 'modalIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
          }} onClick={e => e.stopPropagation()}>
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '28px 28px 0 0' }} />
            <button onClick={() => setQModeModal(false)} style={{
              position: 'absolute', top: 16, right: 16,
              background: theme === 'dark' ? 'rgba(255,255,255,0.06)' : 'rgba(0,0,0,0.06)',
              border: `1px solid ${s.border}`, borderRadius: '50%',
              width: 34, height: 34, cursor: 'pointer', color: s.textSec,
              fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>✕</button>

            <div style={{ textAlign: 'center', marginBottom: 10 }}>
              <div style={{ fontSize: '2.4rem', marginBottom: 10 }}>📋</div>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.35rem', fontWeight: 900, color: s.textPrimary, marginBottom: 6 }}>
                How should questions be created?
              </div>
              <div style={{ fontSize: '0.82rem', color: s.textSec }}>
                For <strong style={{ color: s.textPrimary }}>{overrideForm.topic}</strong> · {overrideForm.subject}
              </div>
            </div>

            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 16, marginTop: 28 }}>
              {/* Option 1 — Manual */}
              <button
                onClick={() => { setQModeModal(false); setQBuilderModal(true); setManualQuestions([]); }}
                style={{
                  background: theme === 'dark' ? 'rgba(124,58,237,0.08)' : 'rgba(124,58,237,0.05)',
                  border: `2px solid ${s.borderStrong}`,
                  borderRadius: 18, padding: '28px 20px', cursor: 'pointer',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
                  transition: 'all 0.2s', fontFamily: 'inherit',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(124,58,237,0.14)'; e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 12px 36px rgba(124,58,237,0.2)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = theme === 'dark' ? 'rgba(124,58,237,0.08)' : 'rgba(124,58,237,0.05)'; e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
              >
                <div style={{ fontSize: '2rem' }}>✍️</div>
                <div style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1rem', color: s.textPrimary }}>Create Manually</div>
                <div style={{ fontSize: '0.72rem', color: s.textSec, textAlign: 'center', lineHeight: 1.5 }}>
                  Build your own MCQ, True/False & Fill-in questions with correct answers
                </div>
                <div style={{
                  fontSize: '0.65rem', fontWeight: 700, color: '#7C3AED',
                  background: 'rgba(124,58,237,0.12)', border: '1px solid rgba(124,58,237,0.3)',
                  padding: '3px 10px', borderRadius: 99,
                }}>Option 1</div>
              </button>

              {/* Option 2 — AI */}
              <button
                onClick={() => handleActivateTopic(null)}
                style={{
                  background: theme === 'dark' ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.05)',
                  border: '2px solid rgba(16,185,129,0.4)',
                  borderRadius: 18, padding: '28px 20px', cursor: 'pointer',
                  display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12,
                  transition: 'all 0.2s', fontFamily: 'inherit',
                }}
                onMouseEnter={e => { e.currentTarget.style.background = 'rgba(16,185,129,0.14)'; e.currentTarget.style.transform = 'translateY(-3px)'; e.currentTarget.style.boxShadow = '0 12px 36px rgba(16,185,129,0.2)'; }}
                onMouseLeave={e => { e.currentTarget.style.background = theme === 'dark' ? 'rgba(16,185,129,0.08)' : 'rgba(16,185,129,0.05)'; e.currentTarget.style.transform = ''; e.currentTarget.style.boxShadow = ''; }}
              >
                <div style={{ fontSize: '2rem' }}>🤖</div>
                <div style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1rem', color: s.textPrimary }}>AI Chatbot</div>
                <div style={{ fontSize: '0.72rem', color: s.textSec, textAlign: 'center', lineHeight: 1.5 }}>
                  Let Gemini AI automatically create questions for students
                </div>
                <div style={{
                  fontSize: '0.65rem', fontWeight: 700, color: '#10B981',
                  background: 'rgba(16,185,129,0.12)', border: '1px solid rgba(16,185,129,0.3)',
                  padding: '3px 10px', borderRadius: 99,
                }}>Option 2</div>
              </button>
            </div>
          </div>
        </div>
      )}

      {/* ── Manual Question Builder Modal ────────────────────────────────── */}
      {qBuilderModal && (() => {
        const totalNeeded = overrideForm.mcq + overrideForm.tf + overrideForm.fill + overrideForm.shortanswer;
        const qDone = manualQuestions.length;
        const allDone = qDone >= totalNeeded;

        // Determine type of current question (cycle: MCQ → TF → FILL → SHORT)
        let currentType = 'MCQ';
        let mcqSoFar = manualQuestions.filter(q => q.type === 'MCQ').length;
        let tfSoFar = manualQuestions.filter(q => q.type === 'TF').length;
        let fillSoFar = manualQuestions.filter(q => q.type === 'FILL').length;
        let shortSoFar = manualQuestions.filter(q => q.type === 'SHORT').length;
        if (mcqSoFar < overrideForm.mcq) currentType = 'MCQ';
        else if (tfSoFar < overrideForm.tf) currentType = 'TF';
        else if (fillSoFar < overrideForm.fill) currentType = 'FILL';
        else if (shortSoFar < overrideForm.shortanswer) currentType = 'SHORT';

        const typeLabel = {
          MCQ: 'Multiple Choice (MCQ)',
          TF: 'True / False',
          FILL: 'Fill in the Blank',
          SHORT: 'Short Answer',
        };
        const typeIcon = { MCQ: '📝', TF: '✅', FILL: '✏️', SHORT: '📄' };

        const initBlank = () => {
          if (currentType === 'MCQ') return { type: 'MCQ', q: '', a: '', options: ['', '', '', ''] };
          if (currentType === 'TF') return { type: 'TF', q: '', a: 'True', options: ['True', 'False'] };
          return { type: 'FILL', q: '', a: '', options: null };
        };

        // Track current-in-progress question in component state
        // We use a sub-state trick via a ref key; simplest is to put it in manualQuestions only on "Add"
        // Use a separate single-question draft state stored in manualQuestions at index qDone (not yet added)
        // Instead let's use a local variable approach — read from manualQuestions[qDone] if it exists as draft
        // Actually we'll store the draft in state as a special entry; simplest: use "draftQ" via useState
        // Since we can't add useState here, let's use a data-attribute approach — read form values on submit
        // Best pattern: render controlled form fields backed by local refs via a helper component

        return (
          <div style={{
            position: 'fixed', inset: 0, zIndex: 9999,
            background: 'rgba(0,0,0,0.92)', backdropFilter: 'blur(20px)',
            display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
            overflowY: 'auto',
          }}>
            <div style={{
              background: s.surface, border: `1px solid ${s.border}`,
              borderRadius: 28, padding: '36px 32px', maxWidth: 620, width: '100%',
              boxShadow: '0 40px 100px rgba(0,0,0,0.95)', position: 'relative',
              animation: 'modalIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
              maxHeight: '90vh', overflowY: 'auto',
            }}>
              <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: s.grad, borderRadius: '28px 28px 0 0' }} />

              {/* Header */}
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
                <div>
                  <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.15rem', fontWeight: 900, color: s.textPrimary }}>
                    ✍️ Create Questions
                  </div>
                  <div style={{ fontSize: '0.72rem', color: s.textSec, marginTop: 2 }}>
                    {overrideForm.topic} · {overrideForm.subject}
                  </div>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  {/* Progress pill */}
                  <div style={{
                    fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1rem',
                    background: 'rgba(124,58,237,0.12)', border: `1px solid ${s.border}`,
                    borderRadius: 99, padding: '6px 16px', color: s.accLight,
                  }}>
                    {qDone} / {totalNeeded}
                  </div>
                  {/* Close ✕ button */}
                  <button
                    type="button"
                    onClick={() => { setQBuilderModal(false); setManualQuestions([]); }}
                    style={{
                      width: 34, height: 34, borderRadius: '50%',
                      background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                      color: '#EF4444', fontSize: '1rem', fontWeight: 700,
                      cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center',
                      fontFamily: 'inherit', flexShrink: 0, transition: 'all 0.15s',
                    }}
                    title="Close"
                  >✕</button>
                </div>
              </div>

              {/* Progress bar */}
              <div style={{ height: 6, background: s.surface3, borderRadius: 99, marginBottom: 24, overflow: 'hidden' }}>
                <div style={{
                  height: '100%', width: `${totalNeeded > 0 ? (qDone / totalNeeded) * 100 : 0}%`,
                  background: s.grad, borderRadius: 99,
                  transition: 'width 0.4s cubic-bezier(0.16,1,0.3,1)',
                }} />
              </div>

              {allDone ? (
                /* All questions created — show summary & finish */
                <div>
                  <div style={{ textAlign: 'center', marginBottom: 24 }}>
                    <div style={{ fontSize: '2.8rem', marginBottom: 10 }}>🎉</div>
                    <div style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 900, fontSize: '1.2rem', color: s.textPrimary, marginBottom: 6 }}>
                      All {totalNeeded} questions ready!
                    </div>
                    <div style={{ fontSize: '0.8rem', color: s.textSec }}>Review your questions below, then activate the topic.</div>
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 10, marginBottom: 24, maxHeight: 280, overflowY: 'auto' }}>
                    {manualQuestions.map((mq, mi) => (
                      <div key={mi} style={{
                        background: s.surface2, border: `1px solid ${s.border}`,
                        borderRadius: 12, padding: '12px 16px',
                        display: 'flex', alignItems: 'flex-start', gap: 12,
                      }}>
                        <div style={{
                          width: 28, height: 28, borderRadius: '50%', background: s.grad,
                          display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontSize: '0.7rem', fontWeight: 800, color: '#fff', flexShrink: 0,
                        }}>{mi + 1}</div>
                        <div style={{ flex: 1 }}>
                          <div style={{ fontSize: '0.7rem', fontWeight: 700, color: s.accLight, marginBottom: 3 }}>
                            {typeIcon[mq.type]} {typeLabel[mq.type]}
                          </div>
                          <div style={{ fontSize: '0.85rem', color: s.textPrimary, marginBottom: 4 }}>{mq.q}</div>
                          <div style={{ fontSize: '0.72rem', color: '#10B981', fontWeight: 700 }}>
                            {mq.type === 'SHORT' ? '📄 Model Answer: ' : '✓ Answer: '}{mq.a}
                          </div>
                        </div>
                        <button
                          onClick={() => setManualQuestions(qs => qs.filter((_, i) => i !== mi))}
                          style={{
                            background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                            borderRadius: 8, padding: '4px 10px', cursor: 'pointer',
                            color: '#EF4444', fontSize: '0.68rem', fontWeight: 700, fontFamily: 'inherit',
                          }}
                        >Remove</button>
                      </div>
                    ))}
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12 }}>
                    <button
                      onClick={() => setManualQuestions(qs => qs.slice(0, -1))}
                      style={{
                        background: s.surface3, border: `1px solid ${s.border}`,
                        borderRadius: 12, padding: '12px', cursor: 'pointer',
                        color: s.textSec, fontWeight: 700, fontSize: '0.88rem', fontFamily: 'inherit',
                      }}
                    >← Edit Last</button>
                    <button
                      onClick={() => handleActivateTopic(manualQuestions)}
                      disabled={submitting}
                      style={{
                        background: submitting ? s.surface3 : s.grad, color: '#fff',
                        border: 'none', borderRadius: 12, padding: '12px', cursor: submitting ? 'default' : 'pointer',
                        fontWeight: 800, fontSize: '0.92rem', fontFamily: 'inherit', opacity: submitting ? 0.7 : 1,
                      }}
                    >{submitting ? '⌛ Activating…' : '🚀 Activate Topic'}</button>
                  </div>
                </div>
              ) : (
                /* Question input form for current question */
                <QuestionForm
                  qIndex={qDone}
                  total={totalNeeded}
                  qType={currentType}
                  typeLabel={typeLabel}
                  typeIcon={typeIcon}
                  s={s}
                  theme={theme}
                  onAdd={(q) => setManualQuestions(prev => [...prev, q])}
                  onCancel={() => {
                    setQBuilderModal(false);
                    setManualQuestions([]);
                    setQModeModal(true);
                  }}
                />
              )}
            </div>
          </div>
        );
      })()}

      {/* Weak Report Modal */}
      {showWeakReport && (
        <div style={{
          position: 'fixed', inset: 0, zIndex: 9998,
          background: 'rgba(0,0,0,0.85)', backdropFilter: 'blur(18px)',
          display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
        }} onClick={() => setShowWeakReport(false)}>
          <div style={{
            background: s.surface, border: `1px solid ${s.border}`,
            borderRadius: 24, padding: '36px 32px', maxWidth: 600, width: '100%',
            boxShadow: '0 32px 80px rgba(0,0,0,0.8)', position: 'relative',
            animation: 'modalIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
            maxHeight: '85vh', overflowY: 'auto',
          }} onClick={e => e.stopPropagation()}>
            {/* Top gradient bar */}
            <div style={{ position: 'absolute', top: 0, left: 0, right: 0, height: 3, background: 'linear-gradient(135deg,#7C3AED,#EC4899)', borderRadius: '24px 24px 0 0' }} />
            {/* Close button */}
            <button onClick={() => setShowWeakReport(false)} style={{
              position: 'absolute', top: 16, right: 16, background: 'rgba(255,255,255,0.06)',
              border: '1px solid rgba(255,255,255,0.1)', borderRadius: '50%',
              width: 34, height: 34, cursor: 'pointer', color: s.textSec,
              fontSize: '0.9rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
            }}>✕</button>

            {/* Header */}
            <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 6 }}>
              <div style={{
                width: 52, height: 52, borderRadius: 16,
                background: 'linear-gradient(135deg,rgba(239,68,68,0.18),rgba(124,58,237,0.18))',
                border: '1px solid rgba(239,68,68,0.3)',
                display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1.6rem',
              }}>📊</div>
              <div>
                <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.25rem', fontWeight: 900, color: s.textPrimary }}>Weak Student Report</div>
                <div style={{ fontSize: '0.78rem', color: s.textSec }}>{YEAR_FULL[year]} · Students scoring below 50%</div>
              </div>
            </div>

            {/* Summary badges */}
            <div style={{ display: 'flex', gap: 10, marginBottom: 22, flexWrap: 'wrap' }}>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                background: 'rgba(239,68,68,0.1)', border: '1px solid rgba(239,68,68,0.3)',
                borderRadius: 99, padding: '5px 14px', fontSize: '0.78rem', fontWeight: 700, color: '#EF4444',
              }}>⚠️ {weakReportData?.total_weak ?? weakReportData?.students?.length ?? 0} Weak Students</div>
              <div style={{
                display: 'inline-flex', alignItems: 'center', gap: 6,
                background: 'rgba(124,58,237,0.1)', border: `1px solid ${s.border}`,
                borderRadius: 99, padding: '5px 14px', fontSize: '0.78rem', fontWeight: 700, color: s.accLight,
              }}>📅 {new Date().toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })}</div>
            </div>

            {/* Student list */}
            {(!weakReportData?.students || weakReportData.students.length === 0) ? (
              <div style={{ textAlign: 'center', padding: '40px 0', color: s.textSec }}>
                <div style={{ fontSize: '3rem', marginBottom: 12 }}>🎉</div>
                <div style={{ fontWeight: 700, fontSize: '1rem', color: s.textPrimary }}>No weak students!</div>
                <div style={{ fontSize: '0.82rem', marginTop: 6 }}>All students scored above 50% in {YEAR_FULL[year]}</div>
              </div>
            ) : (
              <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                {/* Table header */}
                <div style={{
                  display: 'grid', gridTemplateColumns: '2fr 1.2fr 1fr 1fr',
                  padding: '8px 14px', fontSize: '0.68rem', fontWeight: 700,
                  color: s.textMuted, textTransform: 'uppercase', letterSpacing: '0.08em',
                  borderBottom: `1px solid ${s.border}`, marginBottom: 4,
                }}>
                  <span>Student</span>
                  <span>Reg No</span>
                  <span>Score</span>
                  <span>Subject</span>
                </div>
                {weakReportData.students.map((st, i) => (
                  <div key={i} style={{
                    display: 'grid', gridTemplateColumns: '2fr 1.2fr 1fr 1fr',
                    alignItems: 'center',
                    background: s.surface2, border: `1px solid ${s.border}`, borderRadius: 14,
                    padding: '13px 14px', transition: 'border-color 0.2s',
                  }}
                    onMouseEnter={e => e.currentTarget.style.borderColor = s.borderStrong}
                    onMouseLeave={e => e.currentTarget.style.borderColor = s.border}>
                    {/* Name + avatar */}
                    <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                      <div style={{
                        width: 32, height: 32, borderRadius: '50%',
                        background: 'linear-gradient(135deg,#EF4444,#F97316)',
                        display: 'flex', alignItems: 'center', justifyContent: 'center',
                        fontWeight: 800, fontSize: '0.8rem', color: '#fff', flexShrink: 0,
                      }}>{(st.name || 'S')[0].toUpperCase()}</div>
                      <span style={{ fontWeight: 700, fontSize: '0.88rem', color: s.textPrimary }}>{st.name || '—'}</span>
                    </div>
                    {/* Reg No */}
                    <span style={{ fontSize: '0.72rem', color: s.textSec, fontFamily: 'monospace' }}>{st.regno || st.reg_no || '—'}</span>
                    {/* Score badge */}
                    <div style={{
                      display: 'inline-flex', alignItems: 'center',
                      background: 'rgba(239,68,68,0.12)', border: '1px solid rgba(239,68,68,0.3)',
                      borderRadius: 99, padding: '3px 10px',
                      fontSize: '0.78rem', fontWeight: 800, color: '#EF4444', width: 'fit-content',
                    }}>{st.score !== undefined ? `${st.score}%` : '—'}</div>
                    {/* Subject */}
                    <span style={{ fontSize: '0.75rem', color: s.accLight, fontWeight: 600 }}>{st.subject || st.weak_topic || '—'}</span>
                  </div>
                ))}
              </div>
            )}

            {/* Footer actions */}
            <div style={{ display: 'flex', gap: 10, marginTop: 24, justifyContent: 'flex-end' }}>
              <button onClick={() => setShowWeakReport(false)} style={{
                background: 'rgba(255,255,255,0.06)', border: `1px solid ${s.border}`,
                color: s.textSec, borderRadius: 10, padding: '9px 20px',
                fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit',
              }}>Close</button>
              <button onClick={() => { setShowWeakReport(false); handleSendReport(); }} style={{
                background: s.grad, border: 'none',
                color: '#fff', borderRadius: 10, padding: '9px 20px',
                fontSize: '0.82rem', fontWeight: 700, cursor: 'pointer', fontFamily: 'inherit',
              }}>📧 Email Report</button>
            </div>
          </div>
        </div>
      )}

      <Toast toasts={toasts} />
      <style>{`
        @keyframes slideIn { from { transform: translateX(120%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes slideInRight { from { transform: translateX(100%); opacity: 0; } to { transform: translateX(0); opacity: 1; } }
        @keyframes modalIn { from { transform: scale(0.88) translateY(20px); opacity:0; } to { transform: scale(1) translateY(0); opacity:1; } }
        @keyframes modalSlideUp { from { transform: scale(0.92) translateY(40px); opacity:0; } to { transform: scale(1) translateY(0); opacity:1; } }
        @keyframes fadeInBg { from { opacity: 0; } to { opacity: 1; } }
        @keyframes spin { to { transform: rotate(360deg); } }
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Outfit:wght@700;800;900&display=swap');
        * { box-sizing: border-box; }
        body { margin: 0; }
        aside::-webkit-scrollbar { width: 4px; }
        aside::-webkit-scrollbar-track { background: transparent; }
        aside::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.3); border-radius: 4px; }
        main::-webkit-scrollbar { width: 6px; }
        main::-webkit-scrollbar-track { background: transparent; }
        main::-webkit-scrollbar-thumb { background: rgba(124,58,237,0.25); border-radius: 4px; }
        select option { background: #1C1C2E; color: #fff; }
        input[type=number]::-webkit-inner-spin-button { opacity: 0.4; }
        @media (max-width: 1024px) {
          .metrics-grid { grid-template-columns: 1fr 1fr !important; }
          .config-grid { grid-template-columns: 1fr !important; }
        }
        @media (max-width: 768px) {
          .metrics-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}

