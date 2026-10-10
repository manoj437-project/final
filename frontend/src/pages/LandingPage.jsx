import { useEffect, useRef, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import Navbar from '../components/Navbar';
import Footer from '../components/Footer';

/* ── Role Selection Sliding Overlay ── */
function RoleSelectOverlay({ open, onClose }) {
  const navigate = useNavigate();
  return (
    <>
      {/* Backdrop */}
      <div
        onClick={onClose}
        style={{
          position: 'fixed', inset: 0, zIndex: 1200,
          background: 'rgba(0,0,0,0.72)', backdropFilter: 'blur(8px)',
          opacity: open ? 1 : 0,
          pointerEvents: open ? 'all' : 'none',
          transition: 'opacity 0.4s ease',
        }}
      />
      {/* Sliding Panel */}
      <div style={{
        position: 'fixed', top: 0, right: 0, bottom: 0, zIndex: 1300,
        width: 'min(520px, 100vw)',
        background: 'linear-gradient(160deg, #0e0818 0%, #130d22 60%, #0a0714 100%)',
        borderLeft: '1px solid rgba(124,58,237,0.25)',
        boxShadow: '-24px 0 80px rgba(0,0,0,0.7)',
        transform: open ? 'translateX(0)' : 'translateX(100%)',
        transition: 'transform 0.45s cubic-bezier(0.4,0,0.2,1)',
        display: 'flex', flexDirection: 'column', alignItems: 'center',
        justifyContent: 'center', padding: '48px 36px', overflowY: 'auto',
      }}>
        {/* Close */}
        <button onClick={onClose} style={{
          position: 'absolute', top: 20, right: 20, background: 'rgba(255,255,255,0.06)',
          border: '1px solid rgba(255,255,255,0.1)', borderRadius: '50%',
          width: 40, height: 40, cursor: 'pointer', color: 'rgba(255,255,255,0.6)',
          fontSize: '1.2rem', display: 'flex', alignItems: 'center', justifyContent: 'center',
          transition: 'all 0.2s',
        }}
          onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.12)'; e.currentTarget.style.color = '#fff'; }}
          onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.06)'; e.currentTarget.style.color = 'rgba(255,255,255,0.6)'; }}>
          ✕
        </button>

        {/* Header */}
        <div style={{ textAlign: 'center', marginBottom: 40 }}>
          <div style={{
            display: 'inline-flex', alignItems: 'center', gap: 8,
            background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.25)',
            borderRadius: 99, padding: '6px 18px', marginBottom: 20,
          }}>
            <span style={{ width: 7, height: 7, background: '#D4AF37', borderRadius: '50%', display: 'inline-block', boxShadow: '0 0 8px #D4AF37' }} />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase', color: '#D4AF37' }}>Choose Your Role</span>
          </div>
          <h2 style={{ fontFamily: "'Outfit', sans-serif", fontSize: 'clamp(1.6rem,4vw,2.2rem)', fontWeight: 900, color: '#fff', letterSpacing: '-0.03em', marginBottom: 10 }}>
            How will you use<br /><span style={{ background: 'linear-gradient(135deg,#7C3AED,#EC4899)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>EduMentor AI?</span>
          </h2>
          <p style={{ fontSize: '0.9rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.6 }}>Select your role to get started</p>
        </div>

        {/* Cards */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 16, width: '100%' }}>
          {/* Student Card */}
          <div onClick={() => { onClose(); navigate('/student-login'); }}
            style={{
              background: 'rgba(20,12,40,0.7)', border: '1px solid rgba(212,175,55,0.18)',
              borderRadius: 20, padding: '28px 28px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 22,
              transition: 'all 0.3s cubic-bezier(0.4,0,0.2,1)',
              position: 'relative', overflow: 'hidden',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.borderColor = 'rgba(212,175,55,0.5)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(212,175,55,0.12)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.borderColor = 'rgba(212,175,55,0.18)'; e.currentTarget.style.boxShadow = ''; }}>
            <div style={{
              width: 68, height: 68, borderRadius: 18, flexShrink: 0,
              background: 'linear-gradient(135deg,rgba(212,175,55,0.25),rgba(212,175,55,0.08))',
              border: '1px solid rgba(212,175,55,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem',
            }}>🎓</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginBottom: 6 }}>I'm a Student</div>
              <div style={{ fontSize: '0.83rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>AI-powered Q&amp;A, weak area detection, and progress tracking</div>
              <div style={{ marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 700, color: '#D4AF37' }}>
                Start Learning <span>→</span>
              </div>
            </div>
          </div>

          {/* Mentor Card */}
          <div onClick={() => { onClose(); navigate('/mentor-login'); }}
            style={{
              background: 'rgba(20,12,40,0.7)', border: '1px solid rgba(124,58,237,0.2)',
              borderRadius: 20, padding: '28px 28px', cursor: 'pointer',
              display: 'flex', alignItems: 'center', gap: 22,
              transition: 'all 0.3s cubic-bezier(0.4,0,0.2,1)',
              position: 'relative', overflow: 'hidden',
            }}
            onMouseEnter={e => { e.currentTarget.style.transform = 'translateY(-4px)'; e.currentTarget.style.borderColor = 'rgba(124,58,237,0.55)'; e.currentTarget.style.boxShadow = '0 12px 40px rgba(124,58,237,0.14)'; }}
            onMouseLeave={e => { e.currentTarget.style.transform = ''; e.currentTarget.style.borderColor = 'rgba(124,58,237,0.2)'; e.currentTarget.style.boxShadow = ''; }}>
            <div style={{
              width: 68, height: 68, borderRadius: 18, flexShrink: 0,
              background: 'linear-gradient(135deg,rgba(124,58,237,0.28),rgba(124,58,237,0.08))',
              border: '1px solid rgba(124,58,237,0.3)',
              display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '2rem',
            }}>🏫</div>
            <div style={{ flex: 1 }}>
              <div style={{ fontFamily: "'Outfit', sans-serif", fontSize: '1.2rem', fontWeight: 800, color: '#fff', marginBottom: 6 }}>I'm a Mentor</div>
              <div style={{ fontSize: '0.83rem', color: 'rgba(255,255,255,0.5)', lineHeight: 1.5 }}>Cohort management, timetable setup, and student performance monitor</div>
              <div style={{ marginTop: 10, display: 'inline-flex', alignItems: 'center', gap: 6, fontSize: '0.78rem', fontWeight: 700, color: '#9F67FF' }}>
                Open Dashboard <span>→</span>
              </div>
            </div>
          </div>
        </div>


      </div>

      <style>{`
        @keyframes slidePanel { from { transform: translateX(100%); } to { transform: translateX(0); } }
      `}</style>
    </>
  );
}

/* ── Cinematic Intro Component ── */
function CinematicIntro({ onDone }) {
  const canvasRef = useRef(null);
  const overlayRef = useRef(null);
  const logoRef = useRef(null);
  const raysRef = useRef(null);
  const gridRef = useRef(null);
  const titleRef = useRef(null);
  const subtitleRef = useRef(null);
  const taglineRef = useRef(null);
  const skipBtnRef = useRef(null);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;
    const onResize = () => { width = canvas.width = window.innerWidth; height = canvas.height = window.innerHeight; };
    window.addEventListener('resize', onResize);

    const NUM = 160, FOV = 350;
    let timeline = 0, lastTime = performance.now();
    let introEnded = false, rafId;

    class Particle {
      constructor() { this.reset(); }
      reset() {
        this.x = (Math.random() - 0.5) * 2800;
        this.y = (Math.random() - 0.5) * 2800;
        this.z = Math.random() * 2000 + 200;
        this.size = Math.random() * 1.8 + 0.3;
        this.opacity = Math.random() * 0.7 + 0.15;
        this.speed = Math.random() * 1.2 + 0.4;
        this.color = `hsl(${42 + Math.random() * 14}, ${78 + Math.random() * 22}%, ${68 + Math.random() * 22}%)`;
        this.pulse = Math.random() * Math.PI * 2;
      }
      update(dt, camX, camY) {
        this.z -= this.speed * (dt / 12);
        this.pulse += dt * 0.002;
        if (this.z <= 0) this.reset();
      }
      draw(ctx, camX, camY) {
        const scale = FOV / this.z;
        const sx = (this.x - camX) * scale + width / 2;
        const sy = (this.y - camY) * scale + height / 2;
        if (sx < -20 || sx > width + 20 || sy < -20 || sy > height + 20) return;
        const s = this.size * scale * (0.85 + 0.15 * Math.sin(this.pulse));
        const op = this.opacity * Math.min(1, (2000 - this.z) / 400) * Math.min(1, this.z / 100);
        ctx.save();
        ctx.globalAlpha = op;
        ctx.fillStyle = this.color;
        ctx.shadowColor = this.color;
        ctx.shadowBlur = s * 4;
        ctx.beginPath();
        ctx.arc(sx, sy, Math.max(0.3, s), 0, Math.PI * 2);
        ctx.fill();
        ctx.restore();
      }
    }

    const particles = Array.from({ length: NUM }, () => new Particle());
    let glowPulse = 0;

    function endIntro() {
      if (introEnded) return;
      introEnded = true;
      cancelAnimationFrame(rafId);
      overlayRef.current?.classList.add('fade-out');
      sessionStorage.setItem('edumentor-intro-played', 'true');
      setTimeout(onDone, 1100);
    }

    skipBtnRef.current?.addEventListener('click', endIntro);

    function tick(now) {
      const dt = Math.min(now - lastTime, 50);
      lastTime = now;
      timeline += dt;

      const camX = Math.sin(timeline * 0.0003) * 80;
      const camY = Math.cos(timeline * 0.00025) * 60;

      ctx.fillStyle = `rgba(11,11,11,${timeline < 1000 ? 0.25 : 0.18})`;
      ctx.fillRect(0, 0, width, height);

      glowPulse += dt * 0.001;
      const gR = 350 + Math.sin(glowPulse) * 80;
      const grad = ctx.createRadialGradient(width / 2, height / 2, 0, width / 2, height / 2, gR);
      grad.addColorStop(0, `rgba(212,175,55,${0.06 + Math.sin(glowPulse) * 0.02})`);
      grad.addColorStop(1, 'rgba(212,175,55,0)');
      ctx.fillStyle = grad;
      ctx.fillRect(0, 0, width, height);

      particles.forEach(p => { p.update(dt, camX, camY); p.draw(ctx, camX, camY); });

      if (timeline > 600) gridRef.current?.classList.add('visible');
      if (timeline > 1000) {
        logoRef.current?.classList.add('visible');
        raysRef.current?.classList.add('visible');
      }
      if (timeline > 2200) titleRef.current?.classList.add('visible');
      if (timeline > 2700) subtitleRef.current?.classList.add('visible');
      if (timeline > 3000) taglineRef.current?.classList.add('visible');
      if (timeline > 1500) skipBtnRef.current?.classList.add('visible');
      if (timeline > 5000) endIntro();

      if (!introEnded) rafId = requestAnimationFrame(tick);
    }

    rafId = requestAnimationFrame(tick);
    return () => { cancelAnimationFrame(rafId); window.removeEventListener('resize', onResize); };
  }, [onDone]);

  return (
    <div id="cinematic-intro" ref={overlayRef} role="dialog" aria-modal="true" aria-label="Intro Screen">
      <canvas id="intro-canvas" ref={canvasRef}></canvas>
      <div className="intro-grid" ref={gridRef} aria-hidden="true"></div>
      <button className="skip-intro-btn" ref={skipBtnRef}>Skip Intro</button>
      <div className="intro-content">
        <div className="intro-rays" ref={raysRef} aria-hidden="true"></div>
        <div className="intro-logo-container" ref={logoRef}>
          <svg width="100%" height="100%" viewBox="0 0 34 34" fill="none" style={{ filter: 'drop-shadow(0 0 20px rgba(245,197,66,0.65))' }}>
            <rect width="34" height="34" rx="10" fill="#0A0A0A" stroke="#F5C542" strokeWidth="1.2" />
            <circle cx="17" cy="17" r="13" fill="none" stroke="#F5C542" strokeWidth="1.2" opacity="0.6" />
            <path d="M9 22 Q17 9 25 22" stroke="#F5C542" strokeWidth="2.2" fill="none" strokeLinecap="round" />
            <circle cx="17" cy="14" r="2.8" fill="#F5C542" />
            <circle cx="11" cy="22" r="1.8" fill="#F5C542" opacity="0.7" />
            <circle cx="23" cy="22" r="1.8" fill="#F5C542" opacity="0.7" />
          </svg>
        </div>
        <h1 className="intro-title" ref={titleRef}>EduMentor AI</h1>
        <div className="intro-subtitle" ref={subtitleRef}>Learn Smarter. Grow Faster.</div>
        <p className="intro-tagline" ref={taglineRef}>AI-Powered Personalized Learning</p>
      </div>
    </div>
  );
}

/* ── Landing Page ── */
export default function LandingPage() {
  const [showIntro, setShowIntro] = useState(() => sessionStorage.getItem('edumentor-intro-played') !== 'true');
  const navigate = useNavigate();
  const scoreBarRef = useRef(null);
  const statStudents = useRef(null);
  const statMentors = useRef(null);
  const statAccuracy = useRef(null);

  /* Scroll reveal */
  useEffect(() => {
    const els = document.querySelectorAll('.feature-card, .step, .role-card, .hero-badge, .section-header, .hero-stats, .cta-container');
    els.forEach((el, i) => {
      el.classList.add('reveal');
      const delay = ['feature-card', 'step'].some(c => el.classList.contains(c)) ? `reveal-delay-${(i % 6) + 1}` : '';
      if (delay) el.classList.add(delay);
    });
    const obs = new IntersectionObserver(entries => {
      entries.forEach(e => { if (e.isIntersecting) { e.target.classList.add('visible'); obs.unobserve(e.target); } });
    }, { threshold: 0.12, rootMargin: '0px 0px -40px 0px' });
    els.forEach(el => obs.observe(el));
    return () => obs.disconnect();
  }, []);

  /* Score bar animation */
  useEffect(() => {
    if (!scoreBarRef.current) return;
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting) { setTimeout(() => { if (scoreBarRef.current) scoreBarRef.current.style.width = '78%'; }, 800); obs.disconnect(); }
    }, { threshold: 0.5 });
    obs.observe(scoreBarRef.current.closest('.ai-chat-card'));
    return () => obs.disconnect();
  }, []);

  /* Counter animation */
  useEffect(() => {
    const counters = [
      { ref: statStudents, target: 10, suffix: 'K+', duration: 1800 },
      { ref: statMentors, target: 500, suffix: '+', duration: 2000 },
      { ref: statAccuracy, target: 95, suffix: '%', duration: 1600 },
    ];
    const statsEl = document.getElementById('hero-stats');
    if (!statsEl) return;
    let animated = false;
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !animated) {
        animated = true;
        counters.forEach(({ ref, target, suffix, duration }) => {
          if (!ref.current) return;
          const start = performance.now();
          const update = (now) => {
            const p = Math.min((now - start) / duration, 1);
            const eased = 1 - Math.pow(1 - p, 3);
            ref.current.textContent = Math.round(eased * target) + suffix;
            if (p < 1) requestAnimationFrame(update);
          };
          requestAnimationFrame(update);
        });
        obs.disconnect();
      }
    }, { threshold: 0.6 });
    obs.observe(statsEl);
    return () => obs.disconnect();
  }, []);

  /* Feature card tilt */
  useEffect(() => {
    if (window.innerWidth <= 768) return;
    const cards = document.querySelectorAll('.feature-card');
    const handlers = [];
    cards.forEach(card => {
      const onMove = e => {
        const r = card.getBoundingClientRect();
        const x = e.clientX - r.left, y = e.clientY - r.top;
        const tiltX = ((y - r.height / 2) / (r.height / 2)) * 4;
        const tiltY = ((r.width / 2 - x) / (r.width / 2)) * 4;
        card.style.transform = `translateY(-6px) rotateX(${tiltX}deg) rotateY(${tiltY}deg)`;
      };
      const onLeave = () => { card.style.transform = ''; };
      card.addEventListener('mousemove', onMove);
      card.addEventListener('mouseleave', onLeave);
      handlers.push({ card, onMove, onLeave });
    });
    return () => handlers.forEach(({ card, onMove, onLeave }) => {
      card.removeEventListener('mousemove', onMove);
      card.removeEventListener('mouseleave', onLeave);
    });
  }, [showIntro]);

  /* Parallax orbs */
  useEffect(() => {
    if (window.innerWidth <= 768) return;
    const orbs = document.querySelectorAll('.orb');
    const onMove = e => {
      const x = (e.clientX / window.innerWidth - 0.5) * 20;
      const y = (e.clientY / window.innerHeight - 0.5) * 20;
      orbs.forEach((orb, i) => { orb.style.transform = `translate(${x * (i + 1) * 0.4}px, ${y * (i + 1) * 0.4}px)`; });
    };
    window.addEventListener('mousemove', onMove, { passive: true });
    return () => window.removeEventListener('mousemove', onMove);
  }, [showIntro]);

  /* Simulated chat loop */
  useEffect(() => {
    if (showIntro) return;
    const chatMessages = document.querySelector('.chat-messages');
    const heroCard = document.querySelector('.ai-chat-card');
    if (!chatMessages || !heroCard) return;

    const aiMsgs = [
      "What is the primary source of energy for photosynthesis? 🌿",
      "Where does CO₂ absorption mainly occur in plants?",
      "Name the products of the light-dependent reactions.",
    ];
    const userMsgs = [
      "Sunlight is the primary energy source.",
      "CO₂ is absorbed through the stomata.",
      "ATP and NADPH are produced.",
    ];
    let idx = 0;
    let stopped = false;

    function addMsg(text, type, delay) {
      return new Promise(res => {
        setTimeout(() => {
          if (stopped) { res(); return; }
          const b = document.createElement('div');
          b.className = `chat-bubble ${type}-bubble`;
          b.style.cssText = 'opacity:0;transform:translateY(8px);transition:opacity 0.4s ease,transform 0.4s ease';
          b.innerHTML = `<p>${text}</p>`;
          chatMessages.appendChild(b);
          chatMessages.scrollTop = chatMessages.scrollHeight;
          requestAnimationFrame(() => requestAnimationFrame(() => { b.style.opacity = '1'; b.style.transform = 'translateY(0)'; }));
          const bubbles = chatMessages.querySelectorAll('.chat-bubble:not(.typing-indicator)');
          if (bubbles.length > 5) { bubbles[0].style.opacity = '0'; setTimeout(() => bubbles[0].remove(), 400); }
          res();
        }, delay);
      });
    }

    async function loop() {
      await new Promise(r => setTimeout(r, 3000));
      while (!stopped) {
        await addMsg(aiMsgs[idx % aiMsgs.length], 'ai', 1200);
        if (stopped) break;
        await addMsg(userMsgs[idx % userMsgs.length], 'user', 2400);
        idx++;
        await new Promise(r => setTimeout(r, 3500));
      }
    }

    let started = false;
    const obs = new IntersectionObserver(entries => {
      if (entries[0].isIntersecting && !started) { started = true; loop(); obs.disconnect(); }
    }, { threshold: 0.3 });
    obs.observe(heroCard);
    return () => { stopped = true; obs.disconnect(); };
  }, [showIntro]);

  if (showIntro) return <CinematicIntro onDone={() => setShowIntro(false)} />;

  const features = [
    { id: 'feature-chatbot', cls: 'card-glow-gold', iconCls: 'icon-gold', title: 'AI Chatbot Q&A', desc: 'Our AI generates topic-specific questions, evaluates your answers in real-time, and provides instant constructive feedback.', tag: 'Interactive Learning', icon: <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" /> },
    { id: 'feature-weakarea', cls: 'card-glow-purple', iconCls: 'icon-purple', title: 'Weak Area Detection', desc: 'Smart AI identifies concepts where you struggle the most, pinpointing which subtopics need more attention and practice.', tag: 'Smart Analysis', icon: <><circle cx="12" cy="12" r="10" /><line x1="12" y1="8" x2="12" y2="12" /><line x1="12" y1="16" x2="12.01" y2="16" /></> },
    { id: 'feature-resources', cls: 'card-glow-teal', iconCls: 'icon-teal', title: 'Resource Recommendations', desc: 'Get curated articles, videos, and exercises personalized to fill your knowledge gaps — intelligently selected by AI.', tag: 'Personalized', icon: <><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20" /><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z" /></> },
    { id: 'feature-reports', cls: 'card-glow-orange', iconCls: 'icon-orange', title: 'Mentor Reports', desc: 'Detailed session reports are automatically sent to mentors, keeping them informed of each student\'s progress and areas for improvement.', tag: 'Auto-Reports', icon: <><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" /><polyline points="14 2 14 8 20 8" /><line x1="16" y1="13" x2="8" y2="13" /><line x1="16" y1="17" x2="8" y2="17" /></> },
    { id: 'feature-progress', cls: 'card-glow-pink', iconCls: 'icon-pink', title: 'Progress Tracking', desc: 'Visual dashboards show learning trends over time. Track score improvements, sessions completed, and topics mastered.', tag: 'Analytics', icon: <polyline points="22 12 18 12 15 21 9 3 6 12 2 12" /> },
    { id: 'feature-adaptive', cls: 'card-glow-green', iconCls: 'icon-green', title: 'Adaptive Learning', desc: 'The AI adapts question difficulty and learning path based on your performance, ensuring you\'re always challenged at the right level.', tag: 'AI-Adaptive', icon: <><circle cx="12" cy="12" r="3" /><path d="M12 1v4M12 19v4M4.22 4.22l2.83 2.83M16.95 16.95l2.83 2.83M1 12h4M19 12h4M4.22 19.78l2.83-2.83M16.95 7.05l2.83-2.83" /></> },
  ];

  const steps = [
    { id: 'step-1', num: '01', iconCls: 'icon-gold', title: 'Enter Your Topics', desc: 'Students type in topics they studied — the AI takes it from there.', icon: <><path d="M12 20h9" /><path d="M16.5 3.5a2.121 2.121 0 0 1 3 3L7 19l-4 1 1-4L16.5 3.5z" /></> },
    { id: 'step-2', num: '02', iconCls: 'icon-purple', title: 'AI Asks Questions', desc: 'The chatbot generates intelligent, topic-relevant questions at varying difficulty levels.', icon: <><circle cx="12" cy="12" r="10" /><path d="M9.09 9a3 3 0 0 1 5.83 1c0 2-3 3-3 3" /><line x1="12" y1="17" x2="12.01" y2="17" /></> },
    { id: 'step-3', num: '03', iconCls: 'icon-teal', title: 'Evaluate & Recommend', desc: 'Answers are scored, weak areas are flagged, and curated resources are recommended.', icon: <><path d="M2 20h.01M7 20v-4" /><path d="M12 20v-8" /><path d="M17 20V8" /><path d="M22 4v16" /></> },
    { id: 'step-4', num: '04', iconCls: 'icon-orange', title: 'Report to Mentor', desc: 'A comprehensive session report is automatically emailed to the student\'s mentor.', icon: <><path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z" /><polyline points="22,6 12,13 2,6" /></> },
  ];

  return (
    <>
      <div className="aurora-bg" aria-hidden="true"></div>
      <Navbar onOpenRoleSelect={() => { const el = document.getElementById('get-started'); if (el) el.scrollIntoView({ behavior: 'smooth' }); }} />

      {/* HERO */}
      <section className="hero" id="hero" aria-labelledby="hero-title">
        <div className="hero-bg-orbs" aria-hidden="true">
          <div className="orb orb-1"></div>
          <div className="orb orb-2"></div>
          <div className="orb orb-3"></div>
        </div>
        <div className="floating-particles" aria-hidden="true">
          {['📚', '🎓', '💡', '⭐', '🧠', '📊'].map((e, i) => <span key={i} className={`particle p${i + 1}`}>{e}</span>)}
        </div>
        <div className="hero-container">
          <div className="hero-content">
            <div className="hero-badge" id="hero-badge">
              <span className="badge-dot" aria-hidden="true"></span>
              AI-Powered Education Platform
            </div>
            <h1 className="hero-title" id="hero-title">
              Learn Smarter
              <span className="accent-line">with AI</span>
            </h1>
            <p className="hero-subtitle" id="hero-subtitle">
              Helping students improve through AI-based learning and mentor guidance. Ask questions, identify weak areas, and grow — all in one premium platform.
            </p>
            <div className="hero-actions" id="hero-actions">
              <button className="btn btn-hero-primary" id="hero-get-started-btn" onClick={() => { const el = document.getElementById('get-started'); if (el) el.scrollIntoView({ behavior: 'smooth' }); }}>
                Get Started
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" aria-hidden="true"><path d="M5 12h14M12 5l7 7-7 7" /></svg>
              </button>
              <a href="#how-it-works" className="btn btn-hero-ghost" id="hero-watch-btn">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" aria-hidden="true"><circle cx="12" cy="12" r="10" /><polygon points="10 8 16 12 10 16 10 8" fill="currentColor" /></svg>
                See How It Works
              </a>
            </div>
            <div className="hero-stats" id="hero-stats" role="list" aria-label="Platform statistics">
              <div className="stat-item" role="listitem"><span className="stat-number" ref={statStudents}>10K+</span><span className="stat-label">Students</span></div>
              <div className="stat-divider" aria-hidden="true"></div>
              <div className="stat-item" role="listitem"><span className="stat-number" ref={statMentors}>500+</span><span className="stat-label">Mentors</span></div>
              <div className="stat-divider" aria-hidden="true"></div>
              <div className="stat-item" role="listitem"><span className="stat-number" ref={statAccuracy}>95%</span><span className="stat-label">Accuracy</span></div>
            </div>
          </div>

          <div className="hero-visual" id="hero-visual" aria-hidden="true">
            <div className="hero-card-wrapper">
              <div className="ai-chat-card">
                <div className="chat-header">
                  <div className="chat-avatar">
                    <svg width="22" height="22" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#0A0A0A" /><path d="M4 20 Q12 14 20 20" stroke="#0A0A0A" strokeWidth="2" fill="none" strokeLinecap="round" /></svg>
                  </div>
                  <div><p className="chat-name">EduMentor AI</p><p className="chat-status">Online</p></div>
                </div>
                <div className="chat-messages">
                  <div className="chat-bubble ai-bubble"><p>Hi! What topic did you study today? 📖</p></div>
                  <div className="chat-bubble user-bubble"><p>I studied Photosynthesis.</p></div>
                  <div className="chat-bubble ai-bubble typing-indicator" id="chat-typing">
                    <p>Great! Let me ask you a question...</p>
                    <div className="dots"><span></span><span></span><span></span></div>
                  </div>
                </div>
                <div className="chat-score">
                  <div className="score-label">Session Score</div>
                  <div className="score-bar-wrapper"><div className="score-bar" ref={scoreBarRef} id="chat-score-bar"></div></div>
                  <div className="score-value" id="chat-score-val">78%</div>
                </div>
              </div>
              <div className="floating-badge badge-top-right"><span>🎯</span> 3 Weak Areas Found</div>
              <div className="floating-badge badge-bottom-left"><span>📩</span> Report Sent to Mentor</div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="features" id="features" aria-labelledby="features-title">
        <div className="section-container">
          <div className="section-header">
            <span className="section-tag" id="features-tag">Features</span>
            <h2 className="section-title" id="features-title">Everything You Need to Excel</h2>
            <p className="section-subtitle">Powered by advanced AI to make learning personal, efficient, and measurable.</p>
            <div className="gold-divider"></div>
          </div>
          <div className="features-grid" id="features-grid" role="list">
            {features.map(f => (
              <div key={f.id} className={`feature-card ${f.cls}`} id={f.id} role="listitem">
                <div className={`feature-icon ${f.iconCls}`}>
                  <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">{f.icon}</svg>
                </div>
                <h3 className="feature-title">{f.title}</h3>
                <p className="feature-desc">{f.desc}</p>
                <div className="feature-tag">{f.tag}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* HOW IT WORKS */}
      <section className="how-it-works" id="how-it-works" aria-labelledby="how-title">
        <div className="section-container">
          <div className="section-header">
            <span className="section-tag">Process</span>
            <h2 className="section-title" id="how-title">How EduMentor AI Works</h2>
            <p className="section-subtitle">Four simple steps to smarter, more effective learning.</p>
            <div className="gold-divider"></div>
          </div>
          <div className="steps-wrapper" id="steps-wrapper">
            <div className="steps-line" aria-hidden="true"></div>
            {steps.map(s => (
              <div key={s.id} className="step" id={s.id}>
                <div className="step-number" aria-hidden="true">{s.num}</div>
                <div className="step-icon-wrap">
                  <div className={`step-icon ${s.iconCls}`}>
                    <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" aria-hidden="true">{s.icon}</svg>
                  </div>
                </div>
                <div className="step-content">
                  <h3 className="step-title">{s.title}</h3>
                  <p className="step-desc">{s.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>


      {/* CTA / Role Selection */}
      <section className="cta-section" id="get-started" aria-labelledby="cta-title">
        <div className="cta-bg-orbs" aria-hidden="true">
          <div className="cta-orb cta-orb-1"></div>
          <div className="cta-orb cta-orb-2"></div>
        </div>
        <div className="cta-container">
          <h2 className="cta-title" id="cta-title">Ready to Transform Learning?</h2>
          <p className="cta-subtitle">Join thousands of students and mentors already using EduMentor AI to achieve better outcomes.</p>
          <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ height: 1, width: 60, background: 'rgba(212,175,55,0.3)' }} />
            <span style={{ fontSize: '0.72rem', fontWeight: 700, letterSpacing: '0.14em', textTransform: 'uppercase', color: '#D4AF37', opacity: 0.85 }}>
              Choose Your Role
            </span>
            <div style={{ height: 1, width: 60, background: 'rgba(212,175,55,0.3)' }} />
          </div>
          <div className="cta-actions">
            <button className="btn btn-cta-primary" id="cta-student-btn" onClick={() => navigate('/student-login')}>🎓 Start as Student</button>
            <button className="btn btn-cta-outline" id="cta-mentor-btn" onClick={() => navigate('/mentor-login')}>🏫 Join as Mentor</button>
          </div>
          <p className="cta-note" id="cta-note">select your role to continue..</p>
        </div>
      </section>

      <Footer />
    </>
  );
}
