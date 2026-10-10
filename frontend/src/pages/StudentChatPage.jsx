import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';
import { useTheme } from '../context/ThemeContext';

// ─── Chat session flow states ───────────────────────────────────────────────
// 'idle'          : No topic assigned by mentor
// 'greeting'      : Topic assigned, asking if student understands
// 'no_understand' : Student said they don't understand → show resources, end
// 'quiz_active'   : Quiz is ongoing
// 'session_ended' : After quiz + resources shown, session complete
// 'deactivated'   : Mentor deactivated mid-session
const FLOW = {
  IDLE: 'idle',
  GREETING: 'greeting',
  NO_UNDERSTAND: 'no_understand',
  QUIZ_ACTIVE: 'quiz_active',
  SESSION_ENDED: 'session_ended',
  DEACTIVATED: 'deactivated',
};

const makeChatTheme = (isDark) => ({
  bg:              isDark ? '#050b0d'                   : '#F0FAFF',
  navBg:           isDark ? 'rgba(10,20,23,0.4)'        : 'rgba(255,255,255,0.85)',
  navBorder:       isDark ? 'rgba(6,182,212,0.15)'      : 'rgba(6,182,212,0.25)',
  textPrimary:     isDark ? '#ffffff'                   : '#0a1a1f',
  textSec:         isDark ? 'rgba(255,255,255,0.6)'     : 'rgba(10,26,31,0.65)',
  textMuted:       isDark ? 'rgba(255,255,255,0.4)'     : 'rgba(10,26,31,0.45)',
  aiBubbleBg:      isDark ? 'rgba(6,182,212,0.08)'     : 'rgba(6,182,212,0.07)',
  aiBubbleBrd:     isDark ? 'rgba(6,182,212,0.2)'      : 'rgba(6,182,212,0.3)',
  inputBg:         isDark ? '#0a1417'                   : '#FFFFFF',
  inputBorder:     isDark ? 'rgba(6,182,212,0.15)'     : 'rgba(6,182,212,0.3)',
  inputColor:      isDark ? '#ffffff'                   : '#0a1a1f',
  chipBg:          isDark ? 'rgba(6,182,212,0.08)'     : 'rgba(6,182,212,0.1)',
  chipBorder:      isDark ? 'rgba(6,182,212,0.2)'      : 'rgba(6,182,212,0.35)',
  chipColor:       isDark ? 'rgba(255,255,255,0.75)'   : '#0a1a1f',
  sessionText:     isDark ? 'rgba(255,255,255,0.4)'    : 'rgba(10,26,31,0.5)',
  logoutColor:     isDark ? 'rgba(255,255,255,0.5)'    : 'rgba(10,26,31,0.6)',
  homeColor:       isDark ? 'rgba(255,255,255,0.6)'    : 'rgba(10,26,31,0.65)',
  typingBg:        isDark ? 'rgba(6,182,212,0.08)'     : 'rgba(6,182,212,0.07)',
  userMsgColor:    isDark ? '#ffffff'                   : '#0a1a1f',
  dotColor:        '#06B6D4',
});

// ─── Keyword classifiers (English only) ─────────────────────────────────────
function classifyUnderstanding(text) {
  const t = text.trim().toLowerCase();
  const YES_WORDS = [
    'yes', 'yeah', 'yep', 'yup', 'sure', 'ok', 'okay', 'i understand', 'i know',
    'understood', 'clear', 'got it', 'i do', 'definitely', 'absolutely',
    'of course', 'correct', 'right', 'indeed', 'affirmative', 'i get it',
    'i\'m ready', 'ready', 'let\'s go', 'lets go', 'start', 'begin', 'proceed',
    'well', 'good', 'great', 'fine', 'perfect', 'nice', 'cool', 'awesome',
    'confident', 'i\'m confident', 'confident enough',
  ];
  const NO_WORDS = [
    'no', 'nope', 'nah', 'not', 'don\'t', 'dont', 'i don\'t', 'idont',
    'not understand', 'not clear', 'not sure', 'confused', 'confusing',
    'don\'t understand', 'dont understand', 'i don\'t understand',
    'difficult', 'hard', 'not ready', 'not confident', 'need help',
    'help me', 'explain', 'unclear', 'doubt', 'no idea', 'lost',
    'what is', 'what are', 'never heard', 'first time', 'new to',
    'i haven\'t', 'haven\'t', 'never', 'did not', 'didnt',
  ];
  for (const w of YES_WORDS) { if (t === w || t.includes(w)) return 'yes'; }
  for (const w of NO_WORDS) { if (t === w || t.includes(w)) return 'no'; }
  return 'unclear';
}

export default function StudentChatPage() {
  const navigate = useNavigate();
  const { theme } = useTheme();
  const c = makeChatTheme(theme === 'dark');

  const [messages, setMessages]         = useState([]);
  const [input, setInput]               = useState('');
  const [typing, setTyping]             = useState(false);
  const [suggestions, setSuggestions]   = useState([]);
  const [quizState, setQuizState]       = useState(null);
  const [assignedTopic, setAssignedTopic] = useState(null);
  const [flowState, setFlowState]       = useState(FLOW.IDLE);
  const chatWindowRef = useRef(null);
  const inputRef      = useRef(null);
  const flowRef       = useRef(FLOW.IDLE); // always in sync

  const studentName  = sessionStorage.getItem('studentName') || 'Student';
  const studentToken = sessionStorage.getItem('studentToken');
  const studentYear  = sessionStorage.getItem('studentYear') || '1';

  // keep flowRef in sync so closures can read current state
  useEffect(() => { flowRef.current = flowState; }, [flowState]);

  /* Auth Guard */
  useEffect(() => {
    const role = sessionStorage.getItem('userRole');
    if (role !== 'student') {
      alert('Access Denied. Please log in as a student.');
      navigate('/student-login');
    }
  }, [navigate]);

  /* Scroll to bottom */
  const scrollDown = useCallback(() => {
    setTimeout(() => {
      if (chatWindowRef.current)
        chatWindowRef.current.scrollTop = chatWindowRef.current.scrollHeight;
    }, 50);
  }, []);

  function addMsg(html, sender) {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), html, sender }]);
    scrollDown();
  }

  // ─── Poll for topic every 30s ──────────────────────────────────────────────
  useEffect(() => {
    let mounted = true;

    async function fetchTopic(isInitial) {
      try {
        const headers = studentToken ? { 'Authorization': `Bearer ${studentToken}` } : {};
        const res    = await fetch(`/api/timetable/get-today?year=${studentYear}`, { headers });
        const result = await res.json();
        if (!mounted) return;

        if (result.success && result.data && !result.data.is_expired) {
          const cfg = result.data;
          if (isInitial) {
            setAssignedTopic({ topic: cfg.topic, subject: cfg.subject, counts: cfg.counts });
            setFlowState(FLOW.GREETING);
            flowRef.current = FLOW.GREETING;
            // Greeting message — ask if they understand
            addMsg(
              `Hello <strong>${studentName}</strong>! 👋<br><br>` +
              `Your mentor has assigned today's topic: <strong>${cfg.topic}</strong> ` +
              `(${cfg.subject}).<br><br>` +
              `<strong>First Class Question:</strong> Do you understand the topic ` +
              `<strong>"${cfg.topic}"</strong>? Have you already learned about it, ` +
              `or is this your first time hearing it?<br><br>` +
              `<em>Please reply honestly — this helps me guide you correctly!</em>`,
              'ai'
            );
            setSuggestions([
              { label: '✅ Yes, I understand it',   value: 'yes' },
              { label: '❌ No, I need to learn it', value: 'no' },
            ]);
          } else {
            // ongoing poll — topic still active, no action needed
            const cur = flowRef.current;
            if (cur === FLOW.DEACTIVATED) {
              // Topic came back? Re-greet
              setAssignedTopic({ topic: cfg.topic, subject: cfg.subject, counts: cfg.counts });
              setFlowState(FLOW.GREETING);
              addMsg(
                `📢 Your mentor has assigned a new topic: <strong>${cfg.topic}</strong>.<br><br>` +
                `Do you understand this topic already, or would you like resources first?`,
                'ai'
              );
              setSuggestions([
                { label: '✅ Yes, I understand it',   value: 'yes' },
                { label: '❌ No, I need to learn it', value: 'no' },
              ]);
            }
          }
        } else {
          // Topic gone / expired
          if (!isInitial && flowRef.current !== FLOW.IDLE && flowRef.current !== FLOW.DEACTIVATED && flowRef.current !== FLOW.SESSION_ENDED) {
            setAssignedTopic(null);
            setFlowState(FLOW.DEACTIVATED);
            flowRef.current = FLOW.DEACTIVATED;
            setQuizState(null);
            setSuggestions([]);
            addMsg(
              `🚫 <strong>Session Ended by Mentor.</strong><br><br>` +
              `Your mentor has deactivated today's quiz session. No new interactions can take place.<br><br>` +
              `<em>Please wait for your mentor to assign a new topic.</em>`,
              'ai'
            );
          } else if (isInitial) {
            setFlowState(FLOW.IDLE);
            flowRef.current = FLOW.IDLE;
            addMsg(
              `Hello <strong>${studentName}</strong>! 👋<br><br>` +
              `Welcome to your <strong>EduMentor AI</strong> study space.<br>` +
              `<em>No topic has been assigned by your mentor yet. Please check back later!</em><br><br>` +
              `⚠️ <strong>No topic is active right now.</strong> I cannot assist until your mentor activates a session.`,
              'ai'
            );
            setSuggestions([]);
          }
        }
      } catch {
        if (isInitial) {
          setFlowState(FLOW.IDLE);
          addMsg(
            `Hello <strong>${studentName}</strong>! 👋<br><br>` +
            `Welcome to your EduMentor AI study space.<br>` +
            `<em>Could not connect to server. Please refresh the page.</em>`,
            'ai'
          );
        }
      }
    }

    fetchTopic(true);
    const pollTimer = setInterval(() => fetchTopic(false), 30000);
    return () => { mounted = false; clearInterval(pollTimer); };
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  // ─── Fetch AI learning resources for topic ─────────────────────────────────
  async function fetchAndShowResources(topic, subject, isAfterQuiz = false) {
    setTyping(true);
    let resourcesHtml = '';
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      const res = await fetch('/api/chat/respond', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          message: `Provide comprehensive learning resources for the topic "${topic}" including: 
1. A brief concept overview (2-3 sentences)
2. Key points to remember (3-5 bullet points)
3. Recommended study links or references
4. One practical tip for mastering this topic.
Format with HTML. Keep it concise, educational and English only.`,
          topic,
          subject,
          mode: 'resources',
        }),
      });
      if (res.ok) {
        const data = await res.json();
        resourcesHtml = data.response || '';
      }
    } catch {}
    setTyping(false);

    if (!resourcesHtml) {
      resourcesHtml = (
        `<strong>📚 Learning Resources for ${topic}</strong><br><br>` +
        `<ul>` +
        `<li><strong>Concept:</strong> Review your textbook chapter on ${topic} thoroughly.</li>` +
        `<li><strong>Practice:</strong> Solve at least 5 problems on ${topic} from your exercise set.</li>` +
        `<li><strong>Online:</strong> Search "${topic} tutorial" on GeeksForGeeks, W3Schools, or Khan Academy.</li>` +
        `<li><strong>Tip:</strong> Write a short summary of ${topic} in your own words to reinforce memory.</li>` +
        `</ul>`
      );
    }

    const prefix = isAfterQuiz
      ? `🎓 <strong>Session Complete!</strong> Here are your learning resources for <strong>${topic}</strong> — study these to strengthen your understanding:<br><br>`
      : `📚 <strong>Learning Resources for "${topic}"</strong><br><br>` +
        `Since you haven't learned this topic yet, please go through these resources first and come back when your mentor assigns the next session:<br><br>`;

    addMsg(prefix + resourcesHtml, 'ai');

    setTimeout(() => {
      addMsg(
        `✅ <strong>Session Closed.</strong><br><br>` +
        `That's all for today's session on <strong>${topic}</strong>. ` +
        `Good luck with your studies! 📖<br><br>` +
        `<em>Your mentor will be notified of your session status. Please wait for the next assigned topic.</em>`,
        'ai'
      );
      setFlowState(FLOW.SESSION_ENDED);
      flowRef.current = FLOW.SESSION_ENDED;
      setSuggestions([]);
    }, 1200);
  }

  // ─── Handle student says "No, I don't understand" ─────────────────────────
  async function handleNotUnderstood(topic, subject) {
    setFlowState(FLOW.NO_UNDERSTAND);
    flowRef.current = FLOW.NO_UNDERSTAND;
    setSuggestions([]);

    // Save a "not_understood" score record so it appears in the mentor's report
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      await fetch('/api/students/score', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          topic,
          score: '0/0',
          percentage: 0,
          date: new Date().toISOString().split('T')[0],
          not_understood: true,
        }),
      });
    } catch {}

    addMsg(
      `📖 No problem! Learning starts from understanding the basics.<br><br>` +
      `Since you are not yet familiar with <strong>${topic}</strong>, ` +
      `I will share learning resources to help you prepare. ` +
      `Fetching the best materials for you right now...`,
      'ai'
    );

    await fetchAndShowResources(topic, subject, false);
  }

  // ─── Start Quiz ────────────────────────────────────────────────────────────
  async function startQuiz(cfg) {
    const topicName   = cfg.topic || assignedTopic?.topic || 'General';
    const subjectName = cfg.subject || assignedTopic?.subject || 'Computer Science';
    const counts      = cfg.counts || assignedTopic?.counts || { mcq: 3, tf: 2, fill: 1 };

    setFlowState(FLOW.QUIZ_ACTIVE);
    flowRef.current = FLOW.QUIZ_ACTIVE;
    setSuggestions([]);

    addMsg(
      `⏳ Generating AI quiz questions on <strong>${topicName}</strong>...`,
      'ai'
    );
    setTyping(true);

    let questions = [];
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      const res = await fetch('/api/students/generate-quiz', {
        method: 'POST',
        headers,
        body: JSON.stringify({
          topic: topicName,
          subject: subjectName,
          counts: { mcq: counts.mcq || 3, tf: counts.tf || 2, fill: counts.fill || 1 },
        }),
      });
      if (res.ok) {
        const data = await res.json();
        questions = data.questions || [];
      }
    } catch {}

    setTyping(false);

    if (questions.length === 0) {
      addMsg(`❌ Could not generate questions. Please try again!`, 'ai');
      setFlowState(FLOW.GREETING);
      flowRef.current = FLOW.GREETING;
      setSuggestions([
        { label: '🔄 Try Again', value: '__start_quiz__' },
      ]);
      return;
    }

    const state = {
      questions,
      step: 0,
      score: 0,
      active: true,
      answerLog: [],
      assessment: { topic: topicName, subject: subjectName, counts },
    };
    setQuizState(state);
    addMsg(
      `🏁 <strong>Assessment Started!</strong><br><br>` +
      `Topic: <strong>${topicName}</strong> (${subjectName})<br>` +
      `Questions: <strong>${questions.length}</strong> — All strictly from this topic!<br><br>` +
      `<em>Type your answers in the box below or click the suggestion chips. Let's test your understanding! 💪</em>`,
      'ai'
    );
    askQuizQuestion(state, 0);
  }

  function askQuizQuestion(state, idx) {
    const delayMs = idx === 0 ? 800 : 1000;
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      if (idx >= state.questions.length) {
        finishQuiz(state);
        return;
      }
      const q         = state.questions[idx];
      const typeLabel = q.type === 'TF' ? 'True / False' : q.type === 'FILL' ? 'Fill in the Blank' : 'Multiple Choice';
      addMsg(
        `<strong>Question ${idx + 1} of ${state.questions.length}</strong> <em>(${typeLabel})</em>:<br><br>${q.q}`,
        'ai'
      );
      if (q.options && q.options.length > 0) {
        setSuggestions(q.options.map(opt => ({ label: opt, value: opt })));
      } else {
        setSuggestions([{
          label: `💡 Hint: ${q.a.substring(0, 1)}${'_'.repeat(Math.max(q.a.length - 1, 2))} (${q.a.length} chars)`,
          value: `hint`,
        }]);
      }
    }, delayMs);
  }

  function processAnswer(text) {
    const q          = quizState.questions[quizState.step];
    const cleanAns   = text.trim().toLowerCase();
    const cleanCorr  = q.a.trim().toLowerCase();
    let correct      = cleanAns === cleanCorr;
    if (!correct && (!q.options || q.options.length === 0)) {
      const words = cleanCorr.split(' ');
      if (words.some(w => w.length > 3 && cleanAns.includes(w))) correct = true;
    }

    const newScore = quizState.score + (correct ? 1 : 0);
    const newStep  = quizState.step + 1;
    const logEntry = {
      q: q.q, type: q.type, options: q.options || null,
      student_answer: text.trim(), correct_answer: q.a, is_correct: correct,
    };
    const newState = { ...quizState, score: newScore, step: newStep, answerLog: [...(quizState.answerLog || []), logEntry] };
    setQuizState(newState);

    addMsg(
      correct
        ? `✅ <strong>Correct!</strong> Well done.`
        : `❌ <strong>Incorrect.</strong> The correct answer was: <strong>${q.a}</strong>`,
      'ai'
    );
    setSuggestions([]);
    askQuizQuestion(newState, newStep);
  }

  async function finishQuiz(state) {
    const total   = state.questions.length;
    const pct     = Math.round((state.score / total) * 100);
    const feedback = pct >= 80
      ? '🌟 Excellent! You have mastered this topic.'
      : pct >= 50
        ? '👍 Good effort! A little more study and you\'ll ace it.'
        : '📖 Review the core concepts and practice more. You\'ve got this!';

    addMsg(
      `🎉 <strong>Assessment Completed!</strong><br><br>` +
      `You scored <strong>${state.score} out of ${total}</strong> (${pct}%).<br>${feedback}<br><br>` +
      `Your score has been logged to your mentor's performance panel.<br><br>` +
      `<em>Now I will share learning resources for you to strengthen your understanding...</em>`,
      'ai'
    );
    setSuggestions([]);
    setQuizState(s => s ? { ...s, active: false } : s);

    // Save score + attempt
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      await fetch('/api/students/score', {
        method: 'POST', headers,
        body: JSON.stringify({
          topic: state.assessment?.topic,
          score: `${state.score}/${total}`,
          percentage: pct,
          date: new Date().toISOString().split('T')[0],
          not_understood: false,
        }),
      });
      if (state.answerLog && state.answerLog.length > 0) {
        await fetch('/api/students/submit-attempt', {
          method: 'POST', headers,
          body: JSON.stringify({
            topic: state.assessment?.topic,
            subject: state.assessment?.subject,
            date: new Date().toISOString().split('T')[0],
            score: `${state.score}/${total}`,
            percentage: pct,
            answers: state.answerLog,
          }),
        });
      }
    } catch {}

    // Always provide resources after quiz — regardless of score
    await fetchAndShowResources(state.assessment?.topic, state.assessment?.subject, true);
  }

  // ─── Main message handler ──────────────────────────────────────────────────
  async function handleSend(textOverride) {
    const text = (textOverride ?? input).trim();
    if (!text) return;
    setInput('');

    const currentFlow = flowRef.current;

    // ── Block all input when session ended or deactivated ──
    if (currentFlow === FLOW.SESSION_ENDED || currentFlow === FLOW.DEACTIVATED) {
      // Don't add user message, just reply with status
      addMsg(
        `🚫 <strong>No active topic right now.</strong><br><br>` +
        `<em>Please wait for your mentor to assign a new topic before interacting.</em>`,
        'ai'
      );
      return;
    }

    // ── Block when no topic assigned ──
    if (currentFlow === FLOW.IDLE || !assignedTopic) {
      addMsg(
        `⚠️ <strong>No topic is active right now.</strong><br><br>` +
        `Your mentor has not assigned a topic yet. Please wait for a topic to be activated before interacting.`,
        'ai'
      );
      return;
    }

    // Show user message
    addMsg(text, 'user');

    // ── Quiz active: process answer ──
    if (currentFlow === FLOW.QUIZ_ACTIVE && quizState?.active) {
      // If student types something irrelevant during quiz, still treat as answer
      processAnswer(text);
      return;
    }

    // ── Greeting flow: classify yes/no ──
    if (currentFlow === FLOW.GREETING) {
      const understanding = classifyUnderstanding(text);

      if (understanding === 'yes') {
        addMsg(
          `Great! 🎉 Since you understand <strong>${assignedTopic.topic}</strong>, ` +
          `let's test your knowledge with a quiz right away!<br><br>` +
          `<em>Preparing your assessment now...</em>`,
          'ai'
        );
        setSuggestions([]);
        setTimeout(() => startQuiz(assignedTopic), 600);
      } else if (understanding === 'no') {
        await handleNotUnderstood(assignedTopic.topic, assignedTopic.subject);
      } else {
        // Unclear — redirect back to the question, ignore off-topic
        addMsg(
          `I'm sorry, I can only proceed with your answer regarding <strong>${assignedTopic.topic}</strong>.<br><br>` +
          `Please tell me: <strong>Do you understand the topic "${assignedTopic.topic}"?</strong><br>` +
          `<em>Reply with "Yes" if you know it, or "No" if you need to learn it first.</em>`,
          'ai'
        );
        setSuggestions([
          { label: '✅ Yes, I understand it',   value: 'yes' },
          { label: '❌ No, I need to learn it', value: 'no' },
        ]);
      }
      return;
    }

    // ── No_understand or Session_ended — block ──
    if (currentFlow === FLOW.NO_UNDERSTAND) {
      addMsg(
        `📖 Your session has concluded with the learning resources provided. ` +
        `Please wait for your mentor to assign a new topic.`,
        'ai'
      );
      return;
    }

    // ── Default fallback — redirect to flow ──
    addMsg(
      `⚠️ I am strictly focused on today's topic: <strong>${assignedTopic.topic}</strong>.<br><br>` +
      `I cannot discuss anything outside of this topic. Please follow the session flow.`,
      'ai'
    );
  }

  // ─── Chip click handler ────────────────────────────────────────────────────
  function handleChipClick(chip) {
    if (chip.value === '__start_quiz__') {
      addMsg('✅ Yes, I understand it', 'user');
      addMsg(
        `Great! 🎉 Let's test your knowledge with a quiz on <strong>${assignedTopic?.topic}</strong>!<br><br>` +
        `<em>Preparing your assessment now...</em>`,
        'ai'
      );
      setSuggestions([]);
      setTimeout(() => startQuiz(assignedTopic), 600);
      return;
    }
    handleSend(chip.value);
  }

  const handleLogout = () => { sessionStorage.clear(); navigate('/student-login'); };

  // ─── Is input blocked? ─────────────────────────────────────────────────────
  const isBlocked = flowState === FLOW.SESSION_ENDED || flowState === FLOW.DEACTIVATED || flowState === FLOW.IDLE;

  // ─── Status banner config ──────────────────────────────────────────────────
  let statusBanner = null;
  if (flowState === FLOW.IDLE) {
    statusBanner = {
      icon: '⏳',
      title: 'No Active Topic',
      desc: 'Your mentor has not assigned a topic yet. Check back soon!',
      bg: 'rgba(107,114,128,0.08)', border: '1px solid rgba(107,114,128,0.3)', titleColor: '#6B7280',
    };
  } else if (flowState === FLOW.DEACTIVATED) {
    statusBanner = {
      icon: '🚫',
      title: 'Session Deactivated',
      desc: 'Your mentor has ended this session. Please wait for a new topic.',
      bg: 'rgba(239,68,68,0.08)', border: '1px solid rgba(239,68,68,0.3)', titleColor: '#EF4444',
    };
  } else if (flowState === FLOW.SESSION_ENDED) {
    statusBanner = {
      icon: '✅',
      title: 'Session Complete',
      desc: 'You have completed today\'s session. Your mentor has been notified.',
      bg: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.3)', titleColor: '#10B981',
    };
  }

  return (
    <div style={{
      minHeight: '100vh',
      background: c.bg,
      color: c.textPrimary,
      display: 'flex',
      flexDirection: 'column',
      fontFamily: "'Inter', sans-serif",
      transition: 'background 0.35s, color 0.35s',
    }}>
      {/* Header */}
      <nav style={{
        background: c.navBg,
        backdropFilter: 'blur(12px)',
        borderBottom: `1px solid ${c.navBorder}`,
        padding: '16px 32px',
        display: 'flex',
        justifyContent: 'space-between',
        alignItems: 'center',
        position: 'sticky',
        top: 0,
        zIndex: 100,
        transition: 'background 0.35s, border-color 0.35s',
      }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <svg width="28" height="28" viewBox="0 0 34 34" fill="none">
            <circle cx="17" cy="17" r="13" fill="none" stroke="url(#chatlogoG)" strokeWidth="2"/>
            <path d="M9 22 Q17 9 25 22" stroke="url(#chatlogoG)" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
            <circle cx="17" cy="14" r="2.8" fill="url(#chatlogoG)"/>
            <defs><linearGradient id="chatlogoG" x1="0" y1="0" x2="34" y2="34"><stop offset="0%" stopColor="#06B6D4"/><stop offset="100%" stopColor="#10B981"/></linearGradient></defs>
          </svg>
          <span style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1.2rem', color: c.textPrimary }}>
            EduMentor <span style={{ background: 'linear-gradient(135deg, #06B6D4, #10B981)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI</span>
          </span>
        </Link>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <span style={{
            fontSize: '0.75rem', fontWeight: 700, letterSpacing: '0.08em', textTransform: 'uppercase',
            color: '#06B6D4', background: 'rgba(6,182,212,0.1)', border: '1px solid rgba(6,182,212,0.2)',
            padding: '4px 12px', borderRadius: 99,
          }}>Student Access</span>
          {assignedTopic && (
            <span style={{
              fontSize: '0.73rem', fontWeight: 600, color: c.textSec,
              background: 'rgba(16,185,129,0.08)', border: '1px solid rgba(16,185,129,0.2)',
              padding: '4px 12px', borderRadius: 99,
            }}>📚 {assignedTopic.topic}</span>
          )}
          <Link to="/" id="chat-home-btn" style={{
            display: 'inline-flex', alignItems: 'center', gap: 6,
            background: 'rgba(6,182,212,0.08)', border: '1px solid rgba(6,182,212,0.2)',
            borderRadius: 8, padding: '5px 14px', textDecoration: 'none',
            color: c.homeColor, fontSize: '0.82rem', fontWeight: 600, transition: 'all 0.2s',
          }}>🏠 Home</Link>
          <ThemeToggle minWidth="64px" />
          <button onClick={handleLogout} id="chat-logout-btn" style={{
            background: 'none', border: 'none', color: c.logoutColor,
            cursor: 'pointer', fontSize: '0.88rem', fontWeight: 600, fontFamily: 'inherit',
          }}>Log Out</button>
        </div>
      </nav>

      {/* Chat Area */}
      <main style={{ flex: 1, maxWidth: 800, width: '100%', margin: '0 auto', display: 'flex', flexDirection: 'column', padding: 24 }}>
        <div style={{
          fontSize: '0.8rem', color: c.sessionText, textAlign: 'center',
          marginBottom: 24, letterSpacing: '0.04em', textTransform: 'uppercase',
        }}>🎓 Session Started · Secure AI Chatbot Workspace</div>

        {/* Chat Window */}
        <div ref={chatWindowRef} id="chat-window" style={{
          flex: 1, overflowY: 'auto', paddingBottom: 24,
          display: 'flex', flexDirection: 'column', gap: 16, minHeight: 300, maxHeight: '60vh',
        }}>
          {messages.map(m => (
            <div key={m.id} style={{
              maxWidth: '82%', padding: '16px 20px', borderRadius: 18, fontSize: '0.95rem', lineHeight: 1.6,
              ...(m.sender === 'ai'
                ? {
                    background: c.aiBubbleBg,
                    border: `1px solid ${c.aiBubbleBrd}`,
                    alignSelf: 'flex-start', borderBottomLeftRadius: 4,
                    boxShadow: '0 4px 12px rgba(0,0,0,0.1)',
                    color: c.textPrimary,
                  }
                : {
                    background: 'linear-gradient(135deg, #06B6D4, #10B981)',
                    color: c.userMsgColor, fontWeight: 600,
                    alignSelf: 'flex-end', borderBottomRightRadius: 4,
                    boxShadow: '0 4px 12px rgba(6,182,212,0.25)',
                  }
              )
            }} dangerouslySetInnerHTML={{ __html: m.html }} />
          ))}
          {typing && (
            <div style={{
              maxWidth: '80%', padding: '16px 20px', borderRadius: 18,
              alignSelf: 'flex-start', background: c.typingBg,
              border: `1px solid ${c.aiBubbleBrd}`, borderBottomLeftRadius: 4,
            }}>
              <div style={{ display: 'flex', gap: 5, padding: '4px 0' }}>
                {[0, 0.2, 0.4].map((d, i) => (
                  <span key={i} style={{
                    width: 8, height: 8, background: '#06B6D4',
                    borderRadius: '50%', display: 'inline-block',
                    animation: `bounce 1.2s ${d}s infinite ease-in-out`,
                  }}></span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Suggestion Chips */}
        {suggestions.length > 0 && !isBlocked && (
          <div style={{ display: 'flex', gap: 8, flexWrap: 'wrap', marginBottom: 12 }}>
            {suggestions.map((s, i) => (
              <button key={i} onClick={() => handleChipClick(s)}
                style={{
                  background: s.label.startsWith('✅') ? 'rgba(16,185,129,0.12)' : s.label.startsWith('❌') ? 'rgba(239,68,68,0.1)' : s.label.startsWith('🏁') ? 'rgba(6,182,212,0.15)' : c.chipBg,
                  border: `1px solid ${s.label.startsWith('✅') ? 'rgba(16,185,129,0.4)' : s.label.startsWith('❌') ? 'rgba(239,68,68,0.3)' : s.label.startsWith('🏁') ? '#06B6D4' : c.chipBorder}`,
                  padding: '8px 18px', borderRadius: 99, fontSize: '0.82rem',
                  color: s.label.startsWith('✅') ? '#10B981' : s.label.startsWith('❌') ? '#EF4444' : s.label.startsWith('🏁') ? (theme === 'dark' ? '#fff' : '#0a1417') : c.chipColor,
                  cursor: 'pointer', fontFamily: 'inherit', transition: 'all 0.2s',
                  fontWeight: 600,
                }}>
                {s.label}
              </button>
            ))}
          </div>
        )}

        {/* Status Banner */}
        {statusBanner && (
          <div style={{
            display: 'flex', alignItems: 'center', gap: 12, marginBottom: 12,
            background: statusBanner.bg, border: statusBanner.border,
            borderRadius: 14, padding: '12px 18px',
          }}>
            <span style={{ fontSize: '1.4rem' }}>{statusBanner.icon}</span>
            <div>
              <div style={{ fontSize: '0.82rem', fontWeight: 800, color: statusBanner.titleColor, marginBottom: 2 }}>{statusBanner.title}</div>
              <div style={{ fontSize: '0.73rem', color: c.textSec }}>{statusBanner.desc}</div>
            </div>
          </div>
        )}

        {/* Input */}
        <form id="chat-input-form" onSubmit={e => { e.preventDefault(); handleSend(); }} style={{
          background: isBlocked ? 'rgba(107,114,128,0.04)' : c.inputBg,
          border: `1px solid ${isBlocked ? 'rgba(107,114,128,0.2)' : c.inputBorder}`,
          borderRadius: 16, padding: 8,
          display: 'flex', alignItems: 'center', gap: 8,
          boxShadow: '0 10px 30px rgba(0,0,0,0.15)',
          transition: 'background 0.35s, border-color 0.35s',
        }}>
          <input
            ref={inputRef}
            id="chat-input"
            type="text"
            value={input}
            onChange={e => setInput(e.target.value)}
            placeholder={
              flowState === FLOW.IDLE ? 'No topic active — waiting for mentor...' :
              flowState === FLOW.DEACTIVATED ? 'Session deactivated by mentor...' :
              flowState === FLOW.SESSION_ENDED ? 'Session complete — waiting for next topic...' :
              flowState === FLOW.GREETING ? 'Type "Yes" or "No" to answer...' :
              flowState === FLOW.QUIZ_ACTIVE ? 'Type your answer here...' :
              'Type a message...'
            }
            autoComplete="off"
            style={{
              flex: 1, background: 'transparent', border: 'none', outline: 'none',
              color: isBlocked ? c.textMuted : c.inputColor,
              padding: 12, fontSize: '0.95rem', fontFamily: 'inherit',
            }}
          />
          <button type="submit" id="chat-send-btn" style={{
            background: isBlocked ? 'rgba(107,114,128,0.15)' : 'linear-gradient(135deg, #06B6D4, #10B981)',
            color: isBlocked ? c.textMuted : '#050b0d',
            border: 'none', borderRadius: 12,
            width: 44, height: 44, display: 'flex', alignItems: 'center',
            justifyContent: 'center', cursor: 'pointer', transition: 'transform 0.2s',
          }}>
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
              <line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2" fill="currentColor"/>
            </svg>
          </button>
        </form>

        {/* Flow progress indicator */}
        {assignedTopic && flowState !== FLOW.IDLE && (
          <div style={{
            display: 'flex', justifyContent: 'center', gap: 8, marginTop: 12, alignItems: 'center',
          }}>
            {[
              { label: 'Topic', active: true },
              { label: 'Understanding Check', active: [FLOW.GREETING, FLOW.NO_UNDERSTAND, FLOW.QUIZ_ACTIVE, FLOW.SESSION_ENDED].includes(flowState) },
              { label: 'Quiz', active: [FLOW.QUIZ_ACTIVE, FLOW.SESSION_ENDED].includes(flowState) },
              { label: 'Resources', active: flowState === FLOW.SESSION_ENDED },
            ].map((step, i) => (
              <div key={i} style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <div style={{
                  width: 8, height: 8, borderRadius: '50%',
                  background: step.active ? '#06B6D4' : 'rgba(107,114,128,0.3)',
                  transition: 'background 0.3s',
                }}/>
                <span style={{ fontSize: '0.68rem', color: step.active ? c.textSec : c.textMuted, fontWeight: step.active ? 600 : 400 }}>
                  {step.label}
                </span>
                {i < 3 && <div style={{ width: 20, height: 1, background: 'rgba(107,114,128,0.2)' }}/>}
              </div>
            ))}
          </div>
        )}
      </main>

      <style>{`
        @keyframes bounce { 0%, 100% { transform: translateY(0); opacity: 0.3; } 50% { transform: translateY(-4px); opacity: 1; } }
      `}</style>
    </div>
  );
}
