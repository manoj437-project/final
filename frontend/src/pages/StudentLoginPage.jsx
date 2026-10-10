import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';
import studentVisual from '../assets/student-visual.png';

/* ── Forgot Password Modal ── */
function ForgotPasswordModal({ onClose, role }) {
  const [step, setStep] = useState(1); // 1=email, 2=otp+newpass
  const [email, setEmail] = useState('');
  const [otp, setOtp] = useState('');
  const [newPass, setNewPass] = useState('');
  const [confirmPass, setConfirmPass] = useState('');
  const [loading, setLoading] = useState(false);
  const [alert, setAlert] = useState(null);

  const showAlert = (type, text) => { setAlert({ type, text }); setTimeout(() => setAlert(null), 5000); };

  const handleSendOtp = async (e) => {
    e.preventDefault();
    if (!email) { showAlert('error', 'Please enter your email address.'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/forgot-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, role }),
      });
      const data = await res.json();
      if (res.ok) {
        showAlert('success', data.message || 'OTP sent to your email!');
        setTimeout(() => { setAlert(null); setStep(2); }, 1500);
      } else {
        showAlert('error', data.detail || 'Email not found. Please try again.');
      }
    } catch {
      showAlert('error', 'Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleResetPassword = async (e) => {
    e.preventDefault();
    if (!otp || !newPass || !confirmPass) { showAlert('error', 'Please fill all fields.'); return; }
    if (newPass.length < 6) { showAlert('error', 'Password must be at least 6 characters.'); return; }
    if (newPass !== confirmPass) { showAlert('error', 'Passwords do not match!'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/reset-password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email, otp, new_password: newPass, role }),
      });
      const data = await res.json();
      if (res.ok) {
        showAlert('success', 'Password reset successful! You can now login.');
        setTimeout(() => { onClose(); }, 2000);
      } else {
        showAlert('error', data.detail || 'Invalid or expired OTP. Please try again.');
      }
    } catch {
      showAlert('error', 'Connection error. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{
      position: 'fixed', inset: 0, zIndex: 9999,
      background: 'rgba(0,0,0,0.8)', backdropFilter: 'blur(12px)',
      display: 'flex', alignItems: 'center', justifyContent: 'center', padding: 24,
    }}>
      <div style={{
        background: 'var(--surface, #1a1208)', border: '1px solid rgba(212,175,55,0.25)',
        borderRadius: 24, padding: '40px 36px', maxWidth: 420, width: '100%',
        boxShadow: '0 24px 80px rgba(0,0,0,0.7), 0 0 40px rgba(212,175,55,0.15)',
        position: 'relative',
        animation: 'modalIn 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275)',
      }}>
        {/* Close */}
        <button onClick={onClose} style={{
          position: 'absolute', top: 16, right: 16, background: 'rgba(255,255,255,0.06)',
          border: '1px solid rgba(255,255,255,0.1)', borderRadius: '50%',
          width: 36, height: 36, cursor: 'pointer', color: 'rgba(255,255,255,0.6)',
          fontSize: '1rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
        }}>✕</button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 28 }}>
          <div style={{ fontSize: '2rem', marginBottom: 10 }}>🔑</div>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.5rem', fontWeight: 800, marginBottom: 6, color: 'var(--text-primary, #fff)' }}>
            Forgot Password?
          </h2>
          <p style={{ fontSize: '0.85rem', color: 'var(--text-secondary, rgba(255,255,255,0.5))', lineHeight: 1.5 }}>
            {step === 1
              ? 'Enter your registered email — we\'ll send a 6-digit OTP'
              : `OTP sent to ${email} — enter it below`}
          </p>
        </div>

        {/* Step indicator */}
        <div style={{ display: 'flex', gap: 8, marginBottom: 24, justifyContent: 'center' }}>
          {[1, 2].map(s => (
            <div key={s} style={{
              height: 4, width: 48, borderRadius: 99,
              background: s <= step ? 'linear-gradient(135deg, #F39C12, #D4AF37)' : 'rgba(255,255,255,0.1)',
              transition: 'background 0.3s',
            }} />
          ))}
        </div>

        {/* Alert */}
        {alert && (
          <div style={{
            background: alert.type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)',
            border: `1px solid ${alert.type === 'success' ? '#10B981' : '#EF4444'}`,
            padding: '10px 14px', borderRadius: 10, fontSize: '0.82rem', marginBottom: 16,
            display: 'flex', alignItems: 'center', gap: 8, color: 'var(--text-primary, #fff)',
          }}>
            <span>{alert.type === 'success' ? '✅' : '⚠️'}</span><span>{alert.text}</span>
          </div>
        )}

        {/* Step 1: Email */}
        {step === 1 && (
          <form onSubmit={handleSendOtp} noValidate>
            <div style={{ marginBottom: 16 }}>
              <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary, rgba(255,255,255,0.5))', marginBottom: 8 }}>
                Email Address
              </label>
              <input
                type="email" id="forgot-email" placeholder="your@college.edu"
                value={email} onChange={e => setEmail(e.target.value)} required
                style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(212,175,55,0.2)', borderRadius: 12, padding: '13px 16px', fontSize: '0.95rem', color: 'var(--text-primary, #fff)', outline: 'none', fontFamily: 'Inter, sans-serif', boxSizing: 'border-box' }}
              />
            </div>
            <button type="submit" id="forgot-send-otp" disabled={loading} style={{
              width: '100%', background: 'linear-gradient(135deg, #F39C12, #D4AF37)',
              color: '#0c0a06', fontWeight: 700, fontSize: '0.95rem', padding: 14, border: 'none',
              borderRadius: 12, cursor: 'pointer', fontFamily: 'Inter, sans-serif', opacity: loading ? 0.7 : 1,
            }}>
              {loading ? '⌛ Sending OTP...' : '📧 Send OTP to Email'}
            </button>
          </form>
        )}

        {/* Step 2: OTP + New Password */}
        {step === 2 && (
          <form onSubmit={handleResetPassword} noValidate>
            {[
              { label: 'OTP Code (6 digits)', id: 'reset-otp', type: 'text', placeholder: '● ● ● ● ● ●', val: otp, set: setOtp },
              { label: 'New Password', id: 'reset-newpass', type: 'password', placeholder: 'Min. 6 characters', val: newPass, set: setNewPass },
              { label: 'Confirm New Password', id: 'reset-confirm', type: 'password', placeholder: 'Re-enter password', val: confirmPass, set: setConfirmPass },
            ].map(f => (
              <div key={f.id} style={{ marginBottom: 14 }}>
                <label style={{ display: 'block', fontSize: '0.75rem', fontWeight: 700, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary, rgba(255,255,255,0.5))', marginBottom: 8 }}>
                  {f.label}
                </label>
                <input
                  type={f.type} id={f.id} placeholder={f.placeholder}
                  value={f.val} onChange={e => f.set(e.target.value)} required
                  style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid rgba(212,175,55,0.2)', borderRadius: 12, padding: '12px 16px', fontSize: '0.95rem', color: 'var(--text-primary, #fff)', outline: 'none', fontFamily: 'Inter, sans-serif', boxSizing: 'border-box' }}
                />
              </div>
            ))}
            <button type="submit" id="reset-password-btn" disabled={loading} style={{
              width: '100%', background: 'linear-gradient(135deg, #F39C12, #D4AF37)',
              color: '#0c0a06', fontWeight: 700, fontSize: '0.95rem', padding: 14, border: 'none',
              borderRadius: 12, cursor: 'pointer', fontFamily: 'Inter, sans-serif', opacity: loading ? 0.7 : 1, marginBottom: 10,
            }}>
              {loading ? '⌛ Resetting...' : '🔒 Reset Password'}
            </button>
            <button type="button" onClick={() => setStep(1)} style={{
              width: '100%', background: 'transparent', border: '1px solid rgba(255,255,255,0.1)',
              borderRadius: 12, padding: '10px', color: 'var(--text-secondary, rgba(255,255,255,0.5))',
              fontSize: '0.85rem', cursor: 'pointer', fontFamily: 'inherit',
            }}>
              ← Resend OTP
            </button>
          </form>
        )}

        <style>{`@keyframes modalIn { from { transform: scale(0.88) translateY(20px); opacity:0; } to { transform: scale(1) translateY(0); opacity:1; } }`}</style>
      </div>
    </div>
  );
}


export default function StudentLoginPage() {
  const navigate = useNavigate();
  const [tab, setTab] = useState('login');
  const [loginData, setLoginData] = useState({ email: '', password: '' });
  const [regData, setRegData] = useState({ username: '', regno: '', dept: '', year: '', email: '', password: '' });
  const [alert, setAlert] = useState(null); // { type: 'error'|'success', text }
  const [loading, setLoading] = useState(false);
  const [showForgotPw, setShowForgotPw] = useState(false);
  const [showLoginPw, setShowLoginPw] = useState(false);
  const [showRegPw, setShowRegPw] = useState(false);

  const showAlert = (type, text) => { setAlert({ type, text }); setTimeout(() => setAlert(null), 5000); };

  const handleLogin = async (e) => {
    e.preventDefault();
    if (!loginData.email || !loginData.password) { showAlert('error', 'Please fill in all fields.'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/student/login', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: loginData.email, password: loginData.password }),
      });
      const data = await res.json();
      if (res.ok && data.access_token) {
        sessionStorage.setItem('userRole', 'student');
        sessionStorage.setItem('studentName', data.name || loginData.email.split('@')[0]);
        sessionStorage.setItem('studentToken', data.access_token || '');
        sessionStorage.setItem('studentYear', data.year || '1');
        navigate('/student-dashboard');
      } else {
        showAlert('error', data.detail || 'Incorrect credentials. Please try again.');
      }
    } catch {
      showAlert('error', 'Unable to connect. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleRegister = async (e) => {
    e.preventDefault();
    if (!regData.username || !regData.regno || !regData.dept || !regData.year || !regData.email || !regData.password) {
      showAlert('error', 'Please fill in all fields.'); return;
    }
    if (regData.password.length < 6) { showAlert('error', 'Password must be at least 6 characters.'); return; }
    setLoading(true);
    try {
      const res = await fetch('/api/auth/student/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(regData),
      });
      const data = await res.json();
      if (res.ok) {
        showAlert('success', 'Registration successful! You can now log in.');
        setTab('login');
      } else {
        showAlert('error', data.detail || 'Registration failed. Please try again.');
      }
    } catch {
      showAlert('error', 'Unable to connect. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)', color: 'var(--text-primary)', overflow: 'hidden', position: 'relative', fontFamily: "'Inter', sans-serif" }}>
      {/* Grid texture */}
      <div style={{ position: 'fixed', inset: 0, backgroundImage: 'linear-gradient(rgba(212,175,55,0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(212,175,55,0.03) 1px, transparent 1px)', backgroundSize: '50px 50px', pointerEvents: 'none', zIndex: 0 }}></div>
      {/* Aurora orb */}
      <div style={{ position: 'absolute', width: 500, height: 500, background: 'radial-gradient(circle, rgba(212,175,55,0.12), transparent 70%)', filter: 'blur(80px)', top: -150, left: -150, pointerEvents: 'none', zIndex: 0 }}></div>

      {/* Theme Toggle */}
      <div style={{ position: 'absolute', top: 20, right: 20, zIndex: 100 }}><ThemeToggle /></div>

      {/* Home Button */}
      <div style={{ position: 'absolute', top: 20, left: 20, zIndex: 100 }}>
        <Link to="/" id="student-login-home-btn" style={{
          display: 'inline-flex', alignItems: 'center', gap: 6,
          background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.2)',
          borderRadius: 99, padding: '7px 16px', textDecoration: 'none',
          color: 'rgba(255,255,255,0.7)', fontSize: '0.8rem', fontWeight: 600,
          backdropFilter: 'blur(8px)', transition: 'all 0.2s',
        }}>
          🏠 Home
        </Link>
      </div>

      <div style={{ display: 'flex', width: '100%', minHeight: '100vh', position: 'relative', zIndex: 10 }}>
        {/* Visual Panel */}
        <div style={{ flex: '1.25', position: 'relative', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end', padding: 60, overflow: 'hidden', background: '#0c0a06', minHeight: '100vh' }} className="visual-panel-hide">
          <img src={studentVisual} alt="Student studying with AI support" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', opacity: 0.55, zIndex: 1 }} />
          <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(12,10,6,0.98) 15%, rgba(12,10,6,0.5) 60%, transparent 100%)', zIndex: 2 }}></div>
          <div style={{ position: 'relative', zIndex: 3, color: '#fff', maxWidth: 500 }}>
            <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '3rem', fontWeight: 900, letterSpacing: '-0.03em', marginBottom: 16, background: 'linear-gradient(135deg, #F39C12 0%, #D4AF37 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>EduMentor AI</h2>
            <p style={{ fontSize: '1.15rem', lineHeight: 1.6, color: '#f3f0e8', marginBottom: 36, fontStyle: 'italic', borderLeft: '3px solid #D4AF37', paddingLeft: 16 }}>
              "Empowering students to unlock their full potential with personalized AI-guided curriculum navigation and chat support."
            </p>
            <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>
              {[{ icon: '✨', title: 'AI Chatbot Support', desc: 'Instant guidance and step-by-step syllabus clarifications anytime.' }].map(f => (
                <div key={f.title} style={{ display: 'flex', alignItems: 'flex-start', gap: 16, background: 'rgba(25,22,16,0.4)', padding: 18, borderRadius: 16, border: '1px solid rgba(212,175,55,0.1)', backdropFilter: 'blur(12px)' }}>
                  <span style={{ fontSize: '1.4rem', background: 'rgba(212,175,55,0.12)', padding: 8, borderRadius: 12 }}>{f.icon}</span>
                  <div><h4 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1rem', fontWeight: 700, marginBottom: 4, color: '#fff' }}>{f.title}</h4><p style={{ fontSize: '0.85rem', color: '#d4c8ab', lineHeight: 1.4 }}>{f.desc}</p></div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Form Panel */}
        <div style={{ flex: 1, display: 'flex', flexDirection: 'column', justifyContent: 'center', alignItems: 'center', padding: '60px 40px', background: 'var(--bg)', position: 'relative', zIndex: 10 }}>
          <div style={{ width: '100%', maxWidth: 420 }}>

            <div style={{ background: 'var(--surface)', backdropFilter: 'blur(20px)', border: '1px solid var(--border)', borderRadius: 24, padding: '40px 32px', boxShadow: '0 20px 50px rgba(0,0,0,0.65), 0 0 40px rgba(212,175,55,0.25)', textAlign: 'center' }}>
              {/* Logo */}
              <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 12, marginBottom: 20 }}>
                <div style={{ display: 'inline-flex', alignItems: 'center', gap: 8 }}>
                  <svg width="28" height="28" viewBox="0 0 34 34" fill="none"><circle cx="17" cy="17" r="13" fill="none" stroke="url(#slogoG)" strokeWidth="2" /><path d="M9 22 Q17 9 25 22" stroke="url(#slogoG)" strokeWidth="2.5" fill="none" strokeLinecap="round" /><circle cx="17" cy="14" r="2.8" fill="url(#slogoG)" /><defs><linearGradient id="slogoG" x1="0" y1="0" x2="34" y2="34"><stop offset="0%" stopColor="#F39C12" /><stop offset="100%" stopColor="#D4AF37" /></linearGradient></defs></svg>
                  <span style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1.4rem', letterSpacing: '-0.02em' }}>EduMentor <span style={{ background: 'linear-gradient(135deg, #F39C12 0%, #D4AF37 100%)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI</span></span>
                </div>
                <span style={{ display: 'inline-block', background: 'rgba(212,175,55,0.12)', border: '1px solid var(--border)', color: 'var(--gold)', fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.1em', textTransform: 'uppercase', padding: '4px 14px', borderRadius: 99 }}>Student Portal</span>
              </div>

              {/* Tab Switcher */}
              <div style={{ display: 'flex', background: 'rgba(0,0,0,0.2)', border: '1px solid var(--border)', borderRadius: 12, padding: 4, marginBottom: 24, gap: 4 }}>
                {['login', 'register'].map(t => (
                  <button key={t} onClick={() => setTab(t)} style={{ flex: 1, padding: '9px 12px', border: 'none', borderRadius: 9, fontSize: '0.84rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'Inter, sans-serif', transition: 'all 0.25s', background: tab === t ? 'linear-gradient(135deg, #F39C12, #D4AF37)' : 'transparent', color: tab === t ? '#0c0a06' : 'var(--text-secondary)' }}>
                    {t === 'login' ? 'Login' : 'Register'}
                  </button>
                ))}
              </div>

              <h1 style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.65rem', fontWeight: 700, marginBottom: 8 }}>{tab === 'login' ? 'Student Login' : 'Create Account'}</h1>
              <p style={{ fontSize: '0.88rem', color: 'var(--text-secondary)', marginBottom: 20 }}>{tab === 'login' ? 'Enter your college credentials to start learning' : 'Fill in your details to get started'}</p>

              {/* Alert */}
              {alert && (
                <div style={{ background: alert.type === 'success' ? 'rgba(16,185,129,0.1)' : 'rgba(239,68,68,0.1)', border: `1px solid ${alert.type === 'success' ? '#10B981' : '#EF4444'}`, padding: '12px', borderRadius: 12, fontSize: '0.85rem', marginBottom: 20, display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span>{alert.type === 'success' ? '✅' : '⚠️'}</span><span>{alert.text}</span>
                </div>
              )}

              {tab === 'login' && (
                <form onSubmit={handleLogin} noValidate>
                  {/* Email field */}
                  <div style={{ textAlign: 'left', marginBottom: 20 }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: 8 }}>Email Address</label>
                    <input type="email" id="login-email" placeholder="Enter your college email" required value={loginData.email} onChange={e => setLoginData(d => ({ ...d, email: e.target.value }))}
                      style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border)', borderRadius: 12, padding: '12px 16px', fontSize: '0.95rem', color: 'var(--text-primary)', outline: 'none', fontFamily: 'Inter, sans-serif', transition: 'all 0.3s', boxSizing: 'border-box' }} />
                  </div>
                  {/* Password field with eye toggle */}
                  <div style={{ textAlign: 'left', marginBottom: 20 }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: 8 }}>Password</label>
                    <div style={{ position: 'relative' }}>
                      <input type={showLoginPw ? 'text' : 'password'} id="login-password" placeholder="Enter your password" required value={loginData.password} onChange={e => setLoginData(d => ({ ...d, password: e.target.value }))}
                        style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border)', borderRadius: 12, padding: '12px 48px 12px 16px', fontSize: '0.95rem', color: 'var(--text-primary)', outline: 'none', fontFamily: 'Inter, sans-serif', transition: 'all 0.3s', boxSizing: 'border-box' }} />
                      <button type="button" onClick={() => setShowLoginPw(v => !v)}
                        style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', padding: 4, display: 'flex', alignItems: 'center', color: '#888' }}
                        title={showLoginPw ? 'Hide password' : 'Show password'}>
                        {showLoginPw ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                            <line x1="1" y1="1" x2="23" y2="23" />
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                            <circle cx="12" cy="12" r="3" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  {/* Forgot Password Link */}
                  <div style={{ textAlign: 'right', marginTop: -12, marginBottom: 20 }}>
                    <button type="button" id="forgot-pw-link" onClick={() => setShowForgotPw(true)} style={{ background: 'none', border: 'none', color: 'var(--gold, #D4AF37)', fontSize: '0.82rem', fontWeight: 600, cursor: 'pointer', fontFamily: 'inherit' }}>
                      🔑 Forgot Password?
                    </button>
                  </div>
                  <button type="submit" id="login-submit-btn" disabled={loading}
                    style={{ width: '100%', background: 'linear-gradient(135deg, #F39C12, #D4AF37)', color: '#0c0a06', fontWeight: 700, fontSize: '0.95rem', padding: 14, border: 'none', borderRadius: 12, cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 8, fontFamily: 'Inter, sans-serif', opacity: loading ? 0.7 : 1 }}>
                    {loading ? '⌛ Logging in...' : 'Log In as Student'}
                  </button>
                </form>
              )}

              {/* Register Form */}
              {tab === 'register' && (
                <form onSubmit={handleRegister} noValidate>
                  {[{ label: 'Username', id: 'reg-username', type: 'text', placeholder: 'e.g. john_doe', key: 'username' },
                  { label: 'Register Number', id: 'reg-regno', type: 'text', placeholder: 'e.g. 21CS045', key: 'regno' },
                  { label: 'Department', id: 'reg-dept', type: 'text', placeholder: 'e.g. Computer Science', key: 'dept' },
                  { label: 'Email ID', id: 'reg-email', type: 'email', placeholder: 'john.doe@college.edu', key: 'email' }].map(f => (
                    <div key={f.id} style={{ textAlign: 'left', marginBottom: 16 }}>
                      <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: 8 }}>{f.label}</label>
                      <input type={f.type} id={f.id} placeholder={f.placeholder} required value={regData[f.key]} onChange={e => setRegData(d => ({ ...d, [f.key]: e.target.value }))}
                        style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border)', borderRadius: 12, padding: '12px 16px', fontSize: '0.95rem', color: 'var(--text-primary)', outline: 'none', fontFamily: 'Inter, sans-serif', boxSizing: 'border-box' }} />
                    </div>
                  ))}
                  {/* Password field with eye toggle */}
                  <div style={{ textAlign: 'left', marginBottom: 16 }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: 8 }}>Password</label>
                    <div style={{ position: 'relative' }}>
                      <input type={showRegPw ? 'text' : 'password'} id="reg-password" placeholder="Min. 6 characters" required value={regData.password} onChange={e => setRegData(d => ({ ...d, password: e.target.value }))}
                        style={{ width: '100%', background: 'rgba(0,0,0,0.25)', border: '1px solid var(--border)', borderRadius: 12, padding: '12px 48px 12px 16px', fontSize: '0.95rem', color: 'var(--text-primary)', outline: 'none', fontFamily: 'Inter, sans-serif', boxSizing: 'border-box' }} />
                      <button type="button" onClick={() => setShowRegPw(v => !v)}
                        style={{ position: 'absolute', right: 12, top: '50%', transform: 'translateY(-50%)', background: 'none', border: 'none', cursor: 'pointer', padding: 4, display: 'flex', alignItems: 'center', color: '#888' }}
                        title={showRegPw ? 'Hide password' : 'Show password'}>
                        {showRegPw ? (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94" />
                            <path d="M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19" />
                            <line x1="1" y1="1" x2="23" y2="23" />
                          </svg>
                        ) : (
                          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                            <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z" />
                            <circle cx="12" cy="12" r="3" />
                          </svg>
                        )}
                      </button>
                    </div>
                  </div>
                  {/* Year Select */}
                  <div style={{ textAlign: 'left', marginBottom: 16 }}>
                    <label style={{ display: 'block', fontSize: '0.78rem', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.08em', color: 'var(--text-secondary)', marginBottom: 8 }}>Year of Study</label>
                    <select id="reg-year" required value={regData.year} onChange={e => setRegData(d => ({ ...d, year: e.target.value }))}
                      style={{ width: '100%', background: 'var(--surface)', border: '1px solid var(--border)', borderRadius: 12, padding: '12px 16px', fontSize: '0.95rem', color: 'var(--text-primary)', outline: 'none', fontFamily: 'Inter, sans-serif', appearance: 'none' }}>
                      <option value="" disabled>Select Year of Study</option>
                      <option value="1">1st Year</option>
                      <option value="2">2nd Year</option>
                      <option value="3">3rd Year</option>
                    </select>
                  </div>
                  <button type="submit" id="register-submit-btn" disabled={loading}
                    style={{ width: '100%', background: 'linear-gradient(135deg, #F39C12, #D4AF37)', color: '#0c0a06', fontWeight: 700, fontSize: '0.95rem', padding: 14, border: 'none', borderRadius: 12, cursor: 'pointer', fontFamily: 'Inter, sans-serif', opacity: loading ? 0.7 : 1 }}>
                    {loading ? '⌛ Creating account...' : 'Create Account'}
                  </button>
                </form>
              )}

              <div style={{ marginTop: 24, fontSize: '0.88rem', color: 'var(--text-secondary)' }}>
                {tab === 'login' ? <><>New here? <button onClick={() => setTab('register')} style={{ color: 'var(--gold)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: 'inherit' }}>Register Now</button></></> : <><>Already have an account? <button onClick={() => setTab('login')} style={{ color: 'var(--gold)', fontWeight: 600, background: 'none', border: 'none', cursor: 'pointer', fontFamily: 'inherit', fontSize: 'inherit' }}>Login</button></></>}
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Forgot Password Modal */}
      {showForgotPw && <ForgotPasswordModal onClose={() => setShowForgotPw(false)} role="student" />}

      <style>{`.visual-panel-hide { } @media (max-width: 1024px) { .visual-panel-hide { display: none !important; } }`}</style>
    </div>
  );
}
