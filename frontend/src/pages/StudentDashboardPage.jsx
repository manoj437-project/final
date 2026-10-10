import { useState, useEffect, useRef, useCallback } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import ThemeToggle from '../components/ThemeToggle';

function delay(ms) { return new Promise(r => setTimeout(r, ms)); }

/* ─────────────────────────────────────────────────────────────
   CHAT PHASES
   'greet'        → AI says hello, asks "how was class?"
   'ask_how'      → waiting for student to reply about class
   'ask_understand' → AI asks "did you understand [topic]?"
   'ask_confirm'  → waiting for yes/no on understanding
   'free'         → normal free-chat mode (no topic or after understand)
   'quiz'         → quiz in progress
   'done'         → quiz finished
───────────────────────────────────────────────────────────── */

/* ─────────────────────────────────────────────────────────────
   MAIN COMPONENT
───────────────────────────────────────────────────────────── */
export default function StudentDashboardPage() {
  const navigate = useNavigate();

  // Auth
  const studentName  = sessionStorage.getItem('studentName') || 'Student';
  const studentToken = sessionStorage.getItem('studentToken');
  const studentYear  = sessionStorage.getItem('studentYear') || '1';
  const firstNameDisplay = studentName.split(' ')[0];

  // Chat state
  const [messages, setMessages]     = useState([]);
  const [input, setInput]           = useState('');
  const [typing, setTyping]         = useState(false);
  const [chips, setChips]           = useState([]);
  const [quiz, setQuiz]             = useState(null);
  const [phase, setPhase]           = useState('greet');

  // Dashboard state
  const [todayTopic, setTodayTopic]       = useState(null);
  const [scores, setScores]               = useState([]);
  const [loadingTopic, setLoadingTopic]   = useState(true);
  const [sessionScore, setSessionScore]   = useState(null);
  const [quizDoneToday, setQuizDoneToday] = useState(false); // ONE-TIME LOCK
  const [sidebarTab, setSidebarTab]       = useState('overview'); // 'overview' | 'history'
  const [loadingHistory, setLoadingHistory] = useState(false);
  const [quizLoading, setQuizLoading]       = useState(false); // AI quiz generation in progress

  const chatRef  = useRef(null);
  const inputRef = useRef(null);

  /* ── Auth Guard ── */
  useEffect(() => {
    if (sessionStorage.getItem('userRole') !== 'student') {
      navigate('/student-login');
    }
  }, [navigate]);

  /* ── Scroll chat ── */
  const scrollDown = useCallback(() => {
    setTimeout(() => { if (chatRef.current) chatRef.current.scrollTop = chatRef.current.scrollHeight; }, 60);
  }, []);

  function addMsg(html, sender) {
    setMessages(prev => [...prev, { id: Date.now() + Math.random(), html, sender }]);
    scrollDown();
  }

  /* ── Fetch score history from backend ── */
  const fetchHistory = useCallback(async () => {
    if (!studentToken) return;
    setLoadingHistory(true);
    try {
      const res = await fetch('/api/students/scores?limit=10', {
        headers: { Authorization: `Bearer ${studentToken}` }
      });
      if (res.ok) {
        const json = await res.json();
        setScores(json.scores || []);
      }
    } catch { /* silent */ }
    setLoadingHistory(false);
  }, [studentToken]);

  /* ── Check quiz status — HARD BLOCK on re-attempt (but respects mentor re-activation) ── */
  async function checkQuizStatus(topic, activatedAt) {
    if (!studentToken || !topic) return false;
    const today = new Date();
    const dateStr = `${today.getFullYear()}-${String(today.getMonth() + 1).padStart(2, '0')}-${String(today.getDate()).padStart(2, '0')}`;
    // Cache key includes activatedAt so re-activation always bypasses cache
    const cacheKey = `quizDone_${topic}_${dateStr}_${activatedAt || ''}`;
    if (sessionStorage.getItem(cacheKey) === 'true') return true;
    try {
      let url = `/api/students/quiz-status?topic=${encodeURIComponent(topic)}&date=${dateStr}`;
      if (activatedAt) url += `&activated_at=${encodeURIComponent(activatedAt)}`;
      const res = await fetch(url, {
        headers: { Authorization: `Bearer ${studentToken}` }
      });
      if (res.ok) {
        const json = await res.json();
        if (json.attempted) {
          sessionStorage.setItem(cacheKey, 'true');
          return true;
        }
      }
    } catch { /* silent */ }
    return false;
  }

  const greetedRef = useRef(false);

  /* ── Fetch today's topic + initial greeting + history ── */
  useEffect(() => {
    if (greetedRef.current) return;
    greetedRef.current = true;
    fetchHistory();
    (async () => {
      setLoadingTopic(true);
      try {
        const headers = studentToken ? { Authorization: `Bearer ${studentToken}` } : {};
        const res = await fetch(`/api/timetable/get-today?year=${studentYear}`, { headers });
        const json = await res.json();

        if (json.success && json.data) {
          const cfg = json.data;
          setTodayTopic(cfg);
          setLoadingTopic(false);

          // Check if the quiz has expired (past due time)
          if (cfg.is_expired) {
            await delay(600);
            addMsg(
              `Hello <strong>${firstNameDisplay}!</strong> 👋 Welcome back!<br><br>` +
              `⏰ Today's quiz on <strong>${cfg.topic}</strong> (${cfg.subject}) had a deadline of <strong>${cfg.due_time || ''}</strong> on <strong>${cfg.due_date || 'today'}</strong> and is now <span style="color:#EF4444;font-weight:700">closed</span>.<br><br>` +
              `See you in the next session! 👋`,
              'ai'
            );
            setPhase('done');
            setChips([]);
            return;
          }

          // ── Step 1: Check if already attempted — pass activated_at so re-activation resets block ──
          const alreadyDone = await checkQuizStatus(cfg.topic, cfg.activated_at || cfg.updated_at);
          if (alreadyDone) {
            setQuizDoneToday(true);
            await delay(600);
            addMsg(
              `Hello <strong>${firstNameDisplay}!</strong> 👋<br><br>` +
              `✅ You have already completed today's quiz on <strong>${cfg.topic}</strong>.<br><br>` +
              `Each quiz can only be attempted <strong>once per day</strong>. Your score has been recorded! 📊<br><br>` +
              `See you in the next session! 👋`,
              'ai'
            );
            setPhase('done');
            setChips([]);
            return;
          }

          // Step 2: Friendly greeting (quiz is active)
          await delay(600);
          addMsg(
            `Hello <strong>${firstNameDisplay}!</strong> 👋 Good to see you!<br><br>` +
            `How was today's class? 😊`,
            'ai'
          );
          setPhase('ask_how');
          setChips([
            { label: '😄 It was great and enjoyable!', action: 'class_good' },
            { label: '😐 It was okay, normal class', action: 'class_ok' },
            { label: '😴 I found it boring', action: 'class_boring' },
          ]);
        } else {
          setLoadingTopic(false);
          await delay(600);
          addMsg(
            `Hello <strong>${firstNameDisplay}!</strong> 👋 Welcome back!<br><br>` +
            `📭 Your mentor has not assigned a topic yet — no quiz today.<br><br>` +
            `See you in the next session! 👋`,
            'ai'
          );
          setPhase('done');
          setChips([]);
        }
      } catch {
        setLoadingTopic(false);
        await delay(600);
        addMsg(
          `Hello <strong>${firstNameDisplay}!</strong> 👋 Welcome back!<br><br>` +
          `⚠️ Connection issue — could not load the mentor quiz.<br><br>` +
          `Please refresh and try again! 👋`,
          'ai'
        );
        setPhase('done');
        setChips([]);
      }
    })();
    // eslint-disable-next-line
  }, []);

  /* ── Report 'not understood' status to backend (marks weak + not_understandable flag) ── */
  async function reportNotUnderstood(topic) {
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      await fetch('/api/students/score', {
        method: 'POST', headers,
        body: JSON.stringify({
          topic: topic || 'General',
          score: '0/0',
          percentage: 0,
          date: new Date().toISOString().split('T')[0],
          not_understood: true,
        }),
      });
    } catch { /* silent */ }
  }

  /* ── Report boring class to backend (triggers mentor email) ── */
  async function reportBoringClass(topic) {
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      await fetch('/api/students/report-boring', {
        method: 'POST', headers,
        body: JSON.stringify({ topic: topic || 'General' }),
      });
    } catch { /* silent */ }
  }

  /* ── Not understood flow: report to backend, fetch & show resources, end session ── */
  async function triggerNotUnderstoodFlow(topicName) {
    const topic = topicName || todayTopic?.topic || 'this topic';
    setChips([]);
    setTyping(true);
    await delay(1000);
    setTyping(false);

    // Report 'not understood' to backend → marks as weak + not_understandable in mentor dashboard
    await reportNotUnderstood(topic);

    addMsg(
      `Thank you for being honest! 🤗<br><br>` +
      `Your mentor has been notified that you did not understand <strong>${topic}</strong>. ` +
      `They will provide additional support in the next class. 📋<br><br>` +
      `Let me share some learning resources to help you study this topic:`,
      'ai'
    );

    // Fetch and show learning resources
    setTyping(true);
    await delay(800);
    setTyping(false);

    addMsg(
      `⏳ <span style="opacity:0.7;font-size:0.85em">Fetching recommended resources for you — please wait a moment...</span>`,
      'ai'
    );
    await delay(1200);

    let ytLinks = '';
    let webLinks = '';
    try {
      const headers = studentToken ? { Authorization: `Bearer ${studentToken}` } : {};
      const res = await fetch(`/api/students/learning-resources?topic=${encodeURIComponent(topic)}`, { headers });
      if (res.ok) {
        const data = await res.json();
        ytLinks = (data.youtube || []).map(r =>
          `<a href="${r.url}" target="_blank" rel="noopener noreferrer" style="color:#FF4444;text-decoration:none;font-weight:600;display:flex;align-items:center;gap:6px;padding:8px 12px;background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.2);border-radius:8px;margin-bottom:6px;">▶ ${r.title}</a>`
        ).join('');
        webLinks = (data.websites || []).map(r =>
          `<a href="${r.url}" target="_blank" rel="noopener noreferrer" style="color:#60A5FA;text-decoration:none;font-weight:600;display:flex;align-items:center;gap:6px;padding:8px 12px;background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);border-radius:8px;margin-bottom:6px;">🌐 ${r.title}</a>`
        ).join('');
      }
    } catch { /* silent */ }

    if (!ytLinks) {
      const q = encodeURIComponent(topic + ' tutorial');
      ytLinks = `<a href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener noreferrer" style="color:#FF4444;text-decoration:none;font-weight:600;padding:8px 12px;background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.2);border-radius:8px;display:block;margin-bottom:6px;">▶ ${topic} Tutorial – YouTube Search</a>`;
    }
    if (!webLinks) {
      webLinks = `<a href="https://www.geeksforgeeks.org/?s=${encodeURIComponent(topic)}" target="_blank" rel="noopener noreferrer" style="color:#60A5FA;text-decoration:none;font-weight:600;padding:8px 12px;background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);border-radius:8px;display:block;margin-bottom:6px;">🌐 GeeksforGeeks – ${topic}</a>`;
    }

    addMsg(
      `📚 <strong>Recommended Resources — <span style="color:#F59E0B">${topic}</span></strong><br><br>` +
      `Don't worry! Use these resources to strengthen your understanding. 🚀<br><br>` +
      `<div style="padding:4px 0"><strong style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.55">🎦 YouTube Videos</strong></div>` +
      `<div style="margin:8px 0 14px">${ytLinks}</div>` +
      `<div style="padding:4px 0"><strong style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.55">🌐 Websites</strong></div>` +
      `<div style="margin:8px 0">${webLinks}</div>`,
      'ai'
    );

    await delay(1000);
    addMsg(
      `👋 <strong>Session ended.</strong> No quiz will be conducted today.<br><br>Study the resources above and come back stronger! See you in the next session! 🌟`,
      'ai'
    );

    // End session completely — no quiz, no chat
    setPhase('done');
    setChips([]);
    setQuizDoneToday(true);

    // NOTE: Mentor final report is sent by the backend scheduler at quiz deadline only.
    // Do NOT call notifySessionEnd() here — that caused a per-student email on every completion.
  }

  /* ── notifySessionEnd removed ──
     The mentor's final report is now sent ONLY by the backend scheduler
     (scheduler.py) when the quiz deadline expires — not per-student. ── */

  /* ── Chip click handler ── */
  async function handleChip(chip) {
    // During quiz, answer chips
    if (quiz?.active) {
      await handleSend(chip.label, chip);
      return;
    }

    // Class reaction chips (how was class?)
    if (chip.action === 'class_good' || chip.action === 'class_ok' || chip.action === 'class_boring') {
      addMsg(chip.label, 'user');
      setChips([]);

      // If boring → report to backend (emails mentor)
      if (chip.action === 'class_boring') {
        await reportBoringClass(todayTopic?.topic);
      }

      let reactionMsg = '';
      if (chip.action === 'class_good') reactionMsg = `Great! 🎉 Glad to hear the class was enjoyable!`;
      else if (chip.action === 'class_ok') reactionMsg = `Alright, a normal class! 😄 Ready to reinforce what you learned?`;
      else reactionMsg = `Sorry to hear that. 😔 Don't worry — let's make sure you understand the topic well!`;

      setTyping(true);
      await delay(1000);
      setTyping(false);

      if (todayTopic) {
        addMsg(
          `${reactionMsg}<br><br>` +
          `🔥 <strong>${todayTopic.topic}</strong> — Did you understand today's class on this topic? 🤔`,
          'ai'
        );
        setPhase('ask_confirm');
        setChips([
          { label: '✅ Yes, I understood it!', action: 'understood' },
          { label: '🤔 Partially understood', action: 'partial' },
          { label: '❌ No, I did not understand', action: 'not_understood' },
        ]);
      } else {
        addMsg(`${reactionMsg}<br><br>What topic would you like to practice?`, 'ai');
        setPhase('free');
        setChips([
          { label: '📊 Data Structures', action: 'topic', topic: 'Data Structures', subject: 'CS' },
          { label: '🔄 Recursion', action: 'topic', topic: 'Recursion', subject: 'CS' },
        ]);
      }
      return;
    }

    // Understanding chips
    if (chip.action === 'understood') {
      addMsg(chip.label, 'user');
      setChips([]);
      setTyping(true);
      await delay(900);
      setTyping(false);
      addMsg(
        `Excellent! 🔥 <strong>${todayTopic?.topic}</strong> — Ready for the quiz? 💪`,
        'ai'
      );
      setPhase('pre_quiz');
      setChips([
        { label: '🚀 Start Quiz', action: 'start_quiz', cfg: todayTopic },
      ]);
      return;
    }

    if (chip.action === 'partial') {
      addMsg(chip.label, 'user');
      setChips([]);
      setTyping(true);
      await delay(1000);
      setTyping(false);
      addMsg(
        `That's okay! 😊 Partial understanding is still progress.<br><br>` +
        `Taking the quiz will help reinforce what you've learned. Shall we proceed?`,
        'ai'
      );
      setPhase('pre_quiz');
      setChips([
        { label: '🚀 Yes, start the quiz!', action: 'start_quiz', cfg: todayTopic },
      ]);
      return;
    }

    if (chip.action === 'not_understood') {
      addMsg(chip.label, 'user');
      await triggerNotUnderstoodFlow(todayTopic?.topic);
      return;
    }

    // Start quiz — block if already done today
    if (chip.action === 'start_quiz' || chip.action === 'topic') {
      if (quizDoneToday) {
        addMsg(
          `✅ You have already completed today's quiz! Each quiz can only be taken <strong>once per day</strong>.<br><br>Your score has been recorded. See you tomorrow! 👋`,
          'ai'
        );
        setChips([]);
        return;
      }
      const cfg = chip.cfg || { topic: chip.topic, subject: chip.subject, counts: { mcq: 3, tf: 2, fill: 1 } };
      addMsg(`🚀 Starting quiz on <strong>${cfg.topic}</strong>!`, 'user');
      setChips([]);
      await delay(300);
      startQuiz(cfg);
    } else if (chip.action === 'explain') {
      addMsg('Please explain the topic 📖', 'user');
      setChips([]);
      await handleExplain();
    } else if (chip.action === 'concepts') {
      addMsg('Show key concepts 💡', 'user');
      setChips([]);
      await handleConcepts();
    } else if (chip.action === 'answer') {
      await handleSend(chip.label, chip);
    }
  }

  /* ── Free-text send ── */
  async function handleSend(textOverride, chipData) {
    const text = (textOverride ?? input).trim();
    if (!text) return;
    setInput('');

    if (!textOverride) addMsg(text, 'user');

    // Quiz answer mode — always allow if quiz is actively running
    if (quiz?.active) {
      if (chipData?.action === 'answer') processAnswer(chipData.value ?? text);
      else processAnswer(text);
      return;
    }

    // If session is done — block all input
    if (phase === 'done') {
      setTyping(true);
      await delay(600);
      setTyping(false);
      addMsg(`✅ Quiz completed! See you in the next session! 👋`, 'ai');
      return;
    }

    // ── GATE: no active mentor topic → block everything ──
    const hasActiveTopic = todayTopic && !todayTopic.is_expired;
    if (!hasActiveTopic) {
      setTyping(true);
      await delay(700);
      setTyping(false);
      addMsg(
        `📭 <strong>No quiz topic is assigned right now.</strong><br><br>` +
        `Please wait for your mentor to activate a topic. 🙏`,
        'ai'
      );
      setChips([]);
      return;
    }

    // Check if user is typing "not understand" / negative response in free text
    const lowerText = text.toLowerCase();
    const isNotUnderstoodText = (
      lowerText.includes('not understand') ||
      lowerText.includes('dont understand') ||
      lowerText.includes("didn't understand") ||
      lowerText.includes("don't understand") ||
      lowerText.includes('did not understand') ||
      lowerText.includes('not understanding') ||
      lowerText.includes('no iam not') ||
      lowerText.includes('no i am not') ||
      (phase === 'ask_confirm' && (lowerText === 'no' || lowerText.startsWith('no ') || lowerText.includes('no')))
    );

    if (isNotUnderstoodText) {
      await triggerNotUnderstoodFlow(todayTopic?.topic);
      return;
    }

    // If in ask_confirm phase and user types "yes" related
    if (phase === 'ask_confirm') {
      if (lowerText.includes('yes') || lowerText.includes('understood') || lowerText.includes('yeah') || lowerText.includes('sure') || lowerText.includes('ok') || lowerText.includes('partially')) {
        setChips([]);
        setTyping(true);
        await delay(900);
        setTyping(false);
        addMsg(
          `Excellent! 🔥 <strong>${todayTopic?.topic}</strong> — Ready for the quiz? 💪`,
          'ai'
        );
        setPhase('pre_quiz');
        setChips([
          { label: '🚀 Start Quiz', action: 'start_quiz', cfg: todayTopic },
        ]);
        return;
      } else {
        // Unrelated or unclear response — re-ask the question
        setTyping(true);
        await delay(700);
        setTyping(false);
        addMsg(
          `🤔 Did you understand <strong>${todayTopic?.topic}</strong> in today's class? Please choose one of the options below.`,
          'ai'
        );
        setChips([
          { label: '✅ Yes, I understood it!', action: 'understood' },
          { label: '🤔 Partially understood', action: 'partial' },
          { label: '❌ No, I did not understand', action: 'not_understood' },
        ]);
        return;
      }
    }

    // If in pre_quiz phase — analyse if user is saying ready or not
    if (phase === 'pre_quiz') {
      const readyWords = ['yes', 'ready', 'start', 'ok', 'sure', 'let', 'go', 'begin', 'yeah', 'yep', 'yup', 'haan', 'ha'];
      const notReadyWords = ['no', 'not', 'nope', 'wait', 'later', 'doubt', 'question', 'nahi', 'illa'];
      const isReady = readyWords.some(w => lowerText.includes(w));
      const isNotReady = notReadyWords.some(w => lowerText === w || lowerText.startsWith(w + ' '));
      if (isReady && !isNotReady) {
        setChips([]);
        if (!quizDoneToday) startQuiz(todayTopic);
        else addMsg(`✅ You have already completed today's quiz! See you tomorrow! 👋`, 'ai');
      } else if (isNotReady) {
        setTyping(true);
        await delay(700);
        setTyping(false);
        addMsg(`No worries! 😊 Are you ready to start the quiz on <strong>${todayTopic?.topic}</strong>? 💪`, 'ai');
        setChips([{ label: '🚀 Start Quiz', action: 'start_quiz', cfg: todayTopic }]);
      } else {
        // Completely unrelated message — re-ask readiness
        setTyping(true);
        await delay(700);
        setTyping(false);
        addMsg(`🤔 Are you ready to take the quiz on <strong>${todayTopic?.topic}</strong>? Let's start when you are! 💪`, 'ai');
        setChips([{ label: '🚀 Start Quiz', action: 'start_quiz', cfg: todayTopic }]);
      }
      return;
    }

    // If we're in ask_how phase, analyse if the reply relates to "how was class"
    if (phase === 'ask_how' && todayTopic) {
      const classRelatedWords = [
        'good', 'great', 'fine', 'ok', 'okay', 'boring', 'bad', 'fun', 'nice', 'enjoyed',
        'understand', 'understood', 'class', 'today', 'interesting', 'dull', 'normal',
        'super', 'awesome', 'excellent', 'average', 'best', 'tired', 'sleepy', 'confusing',
        'clear', 'unclear', 'learned', 'know', 'difficult', 'easy', 'tough', 'hard',
        'nalla', 'nana', 'seri', 'boring', 'sollow', 'teriyala', 'puriela',
      ];
      const boringWords = ['boring', 'bore', 'dull', 'boring', 'bad', 'worst', 'terrible', 'sleepy'];
      const isClassRelated = classRelatedWords.some(w => lowerText.includes(w)) || lowerText.length < 20;
      // If student typed "boring" or similar in free text, record it just like the chip
      if (boringWords.some(w => lowerText.includes(w))) {
        await reportBoringClass(todayTopic?.topic);
      }
      if (isClassRelated) {
        setChips([]);
        setTyping(true);
        await delay(900);
        setTyping(false);
        addMsg(
          `Got it! 😄<br><br>` +
          `One important question — did you understand <strong>${todayTopic.topic}</strong> in today's class? 🤔`,
          'ai'
        );
        setPhase('ask_confirm');
        setChips([
          { label: '✅ Yes, I understood it!', action: 'understood' },
          { label: '🤔 Partially understood', action: 'partial' },
          { label: '❌ No, I did not understand', action: 'not_understood' },
        ]);
      } else {
        // Unrelated message — re-ask how was class
        setTyping(true);
        await delay(700);
        setTyping(false);
        addMsg(`😊 How was today's class? Please tell me how it went!`, 'ai');
        setChips([
          { label: '😄 It was great and enjoyable!', action: 'class_good' },
          { label: '😐 It was okay, normal class', action: 'class_ok' },
          { label: '😴 I found it boring', action: 'class_boring' },
        ]);
      }
      return;
    }

    // "start" keyword — only if active topic and not already done
    if (text.toLowerCase().includes('start') && todayTopic && !todayTopic.is_expired) {
      if (quizDoneToday) {
        addMsg(`✅ You have already completed today's quiz! Each quiz can only be taken <strong>once per day</strong>.`, 'ai');
        return;
      }
      setChips([]);
      startQuiz(todayTopic);
      return;
    }

    // General AI response via Gemini — topic-scoped, English only
    setTyping(true);
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      const res = await fetch('/api/chat/respond', {
        method: 'POST', headers,
        body: JSON.stringify({
          message: text,
          topic: todayTopic?.topic,
          subject: todayTopic?.subject,
        }),
      });
      setTyping(false);
      if (res.ok) {
        const json = await res.json();
        addMsg(json.response || 'I am here to help with your topic questions!', 'ai');
        if (json.suggestions?.length) {
          setChips(json.suggestions.map(s => ({ label: s, action: 'send', text: s })));
        }
      } else {
        addMsg(`I could not process that right now. Please ask about <strong>${todayTopic?.topic}</strong>.`, 'ai');
      }
    } catch {
      setTyping(false);
      addMsg(`Connection issue. Please try again!`, 'ai');
    }
  }

  /* ── Explain ── */
  async function handleExplain() {
    setTyping(true);
    await delay(1400);
    setTyping(false);
    const t = todayTopic?.topic || 'this topic';
    const s = todayTopic?.subject || 'Computer Science';
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      const res = await fetch('/api/chat/respond', {
        method: 'POST', headers,
        body: JSON.stringify({ message: `Explain ${t} in detail`, topic: t, subject: s }),
      });
      if (res.ok) {
        const json = await res.json();
        addMsg(json.response, 'ai');
        setChips([
          { label: '🚀 Start Quiz', action: 'start_quiz', cfg: todayTopic },
          { label: '💡 Key concepts', action: 'concepts' },
        ]);
        return;
      }
    } catch { /* fall through */ }
    addMsg(
      `Let me explain <strong>${t}</strong> (${s})! 📖<br><br>` +
      `<strong>Core Idea:</strong> ${t} is a fundamental concept in ${s}.<br><br>` +
      `<strong>Key Points:</strong><br>` +
      `• Focus on primary use-cases and time complexity<br>` +
      `• Practice with simple examples first<br>` +
      `• Connect to real-world applications for better understanding<br><br>` +
      `Ready to test yourself with a quiz? 😊`,
      'ai'
    );
    setChips([
      { label: '🚀 Start Quiz!', action: 'start_quiz', cfg: todayTopic || { topic: t, subject: s, counts: { mcq: 3, tf: 2, fill: 1 } } },
      { label: '💡 Key concepts', action: 'concepts' },
    ]);
  }

  /* ── Concepts ── */
  async function handleConcepts() {
    setTyping(true);
    await delay(1200);
    setTyping(false);
    const t = todayTopic?.topic || 'this topic';
    const s = todayTopic?.subject || 'Computer Science';
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      const res = await fetch('/api/chat/respond', {
        method: 'POST', headers,
        body: JSON.stringify({ message: `List the key concepts of ${t}`, topic: t, subject: s }),
      });
      if (res.ok) {
        const json = await res.json();
        addMsg(json.response, 'ai');
        setChips([{ label: '🚀 Start Quiz!', action: 'start_quiz', cfg: todayTopic }]);
        return;
      }
    } catch { /* fall through */ }
    addMsg(
      `<strong>${t}</strong> — Key Concepts! 💡<br><br>` +
      `1. <strong>Definition & Purpose</strong> — What it is and why we use it<br>` +
      `2. <strong>Core Properties</strong> — How it works internally<br>` +
      `3. <strong>Time & Space Complexity</strong> — Performance characteristics<br>` +
      `4. <strong>Common Patterns</strong> — Typical problems it solves<br>` +
      `5. <strong>Edge Cases</strong> — Situations that need careful handling<br><br>` +
      `Pro tip: Implement it from scratch once — best way to truly understand! 🔥`,
      'ai'
    );
    setChips([{ label: '🚀 Start Quiz!', action: 'start_quiz', cfg: todayTopic || { topic: t, subject: s, counts: { mcq: 3, tf: 2, fill: 1 } } }]);
  }

  /* ── Start Quiz ── */
  async function startQuiz(cfg) {
    setChips([]);
    setQuizLoading(true);
    setPhase('quiz');
    setSessionScore(null);

    // Show a loading message while questions are being fetched (manual or AI)
    const isManual = cfg.question_mode === 'manual';
    addMsg(
      `🧠 <strong>${isManual ? `Loading mentor's questions for "${cfg.topic}"...` : `Generating AI questions for "${cfg.topic}"...`}</strong><br>` +
      `<span style="font-size:0.8em;opacity:0.6">${isManual ? 'Using questions created by your mentor ✍️' : 'Creating unique questions just for you — please wait a moment! ⏳'}</span>`,
      'ai'
    );

    let questions = [];
    let errorOccurred = false;
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;

      let res;
      if (isManual) {
        // ── MANUAL MODE: fetch mentor's questions directly — zero AI ──
        res = await fetch(
          `/api/students/get-manual-questions?topic=${encodeURIComponent(cfg.topic)}`,
          { method: 'GET', headers }
        );
      } else {
        // ── AI MODE: ask Gemini to generate questions ──
        res = await fetch('/api/students/generate-quiz', {
          method: 'POST',
          headers,
          body: JSON.stringify({
            topic: cfg.topic,
            subject: cfg.subject || 'Computer Science',
            counts: cfg.counts || { mcq: 3, tf: 2, fill: 1 }
          })
        });
      }

      if (res.ok) {
        const json = await res.json();
        questions = json.questions || [];
        questions = questions.filter(q => q.q && q.q.trim().length > 0 && q.a && q.a.trim().length > 0);
      } else {
        console.error('Quiz fetch error:', res.status);
        errorOccurred = true;
      }
    } catch (err) {
      console.error('Quiz fetch failed:', err);
      errorOccurred = true;
    }

    setQuizLoading(false);

    if (questions.length === 0) {
      setPhase('chat');
      setQuiz(null);
      addMsg(
        `❌ <strong>Could not load questions for "${cfg.topic}".</strong><br><br>` +
        (isManual
          ? 'Mentor\'s questions could not be loaded. Please ask your mentor to re-activate the topic.'
          : 'AI service unavailable. Please try again in a moment!'),
        'ai'
      );
      setChips([
        { label: '🔁 Retry Quiz', action: 'start_quiz', cfg },
        { label: '📚 Explain Topic Instead', action: 'explain', cfg },
      ]);
      return;
    }


    const state = { questions, step: 0, score: 0, active: true, cfg };
    setQuiz(state);

    addMsg(
      `🏁 <strong>Quiz Time!</strong> — <strong>${cfg.topic}</strong><br>` +
      `${questions.length} questions, all strictly about <strong>${cfg.topic}</strong>. Think carefully — let's go! 💪`,
      'ai'
    );
    askNextQuestion(state, 0);
  }

  function askNextQuestion(state, idx) {
    setTyping(true);
    setTimeout(() => {
      setTyping(false);
      if (idx >= state.questions.length) { finishQuiz(state); return; }
      const q = state.questions[idx];

      const typeLabel = q.type === 'MCQ' ? '📝 Multiple Choice' : q.type === 'TF' ? '✔️ True or False' : '✏️ Fill in the Blank';
      addMsg(
        `<span style="font-size:0.75rem;opacity:0.55;font-weight:600;letter-spacing:0.05em;text-transform:uppercase;">${typeLabel} · Q${idx + 1} of ${state.questions.length}</span><br><br>` +
        `<strong>${q.q}</strong>`,
        'ai'
      );

      if (q.options) {
        setChips(q.options.map(opt => ({ label: opt, action: 'answer', value: opt })));
      } else {
        setChips([]);
      }
    }, idx === 0 ? 900 : 1100);
  }

  function processAnswer(text) {
    const q = quiz.questions[quiz.step];
    const given   = text.trim().toLowerCase();
    const correct = q.a.trim().toLowerCase();
    let isRight = given === correct;
    if (!isRight && !q.options) {
      isRight = correct.split(' ').some(w => w.length > 2 && given.includes(w));
    }

    const newScore = quiz.score + (isRight ? 1 : 0);
    const newStep  = quiz.step + 1;

    // ── Track this answer for mentor review ──
    const newAnsweredList = [
      ...(quiz.answeredList || []),
      {
        q: q.q,
        type: q.type,
        options: q.options || null,
        student_answer: text.trim(),
        correct_answer: q.a,
        is_correct: isRight,
      }
    ];

    const newState = { ...quiz, score: newScore, step: newStep, answeredList: newAnsweredList };
    setQuiz(newState);
    setChips([]);

    addMsg(
      isRight
        ? `✅ <strong>Correct!</strong> Well done — exactly right!`
        : `❌ <strong>Not quite.</strong> The correct answer is: <strong>${q.a}</strong>`,
      'ai'
    );

    askNextQuestion(newState, newStep);
  }


  async function finishQuiz(state) {
    const total   = state.questions.length;
    const pct     = Math.round((state.score / total) * 100);
    const needsResources = pct < 80; // Show resources for both <50% and 50-79%
    const isWeak  = pct < 50;
    const isMentorQuiz = todayTopic && state.cfg?.topic === todayTopic.topic;
    const feedback =
      pct >= 80 ? "Excellent work! 🌟 You have a strong understanding of this topic — keep it up!" :
      pct >= 50 ? "Good effort! 💪 A bit more practice and you will master this topic!" :
                  "Keep going! 📚 Review the topic and try again — you can do it!";

    addMsg(
      `🎉 <strong>Quiz Complete!</strong><br><br>` +
      `Scored <strong style="font-size:1.3em;">${state.score}/${total}</strong> &nbsp;(${pct}%)<br><br>` +
      `${feedback}<br><br>` +
      `Your score has been sent to your mentor's dashboard! 📊`,
      'ai'
    );

    setSessionScore({ score: state.score, total, pct });
    setQuiz(s => s ? { ...s, active: false } : s);
    setPhase('done');
    setChips([]);

    // ── Show "Done" badge (but do NOT block future retakes) ──
    setQuizDoneToday(true);

    // Update local scores
    const newEntry = {
      topic: state.cfg?.topic || 'Quiz',
      score: `${state.score}/${total}`,
      percentage: pct,
      date: new Date().toLocaleDateString('en-IN'),
    };
    setScores(prev => [newEntry, ...prev].slice(0, 10));

    // Persist to backend — score only
    const localDate = new Date();
    const localDateStr = `${localDate.getFullYear()}-${String(localDate.getMonth() + 1).padStart(2, '0')}-${String(localDate.getDate()).padStart(2, '0')}`;
    try {
      const headers = { 'Content-Type': 'application/json' };
      if (studentToken) headers['Authorization'] = `Bearer ${studentToken}`;
      // 1) Save simple score summary (existing endpoint)
      await fetch('/api/students/score', {
        method: 'POST', headers,
        body: JSON.stringify({ topic: state.cfg?.topic, score: `${state.score}/${total}`, percentage: pct, date: localDateStr }),
      });
      // 2) Save full Q&A attempt so mentor can review answers
      if (state.answeredList && state.answeredList.length > 0) {
        await fetch('/api/students/save-attempt', {
          method: 'POST', headers,
          body: JSON.stringify({
            topic: state.cfg?.topic || 'Quiz',
            subject: state.cfg?.subject || 'Computer Science',
            date: localDateStr,
            score: `${state.score}/${total}`,
            percentage: pct,
            answers: state.answeredList,
          }),
        });
      }
    } catch { /* silent */ }

    // ── Show learning resources for <80% scorers ──
    if (needsResources) {
      // Show a small "please wait" message while resources are being fetched
      addMsg(
        `⏳ <span style="opacity:0.7;font-size:0.85em">Fetching recommended resources for you — please wait a moment...</span>`,
        'ai'
      );
      await delay(1600);

      let ytLinks = '';
      let webLinks = '';
      try {
        const headers = studentToken ? { Authorization: `Bearer ${studentToken}` } : {};
        const res = await fetch(`/api/students/learning-resources?topic=${encodeURIComponent(state.cfg?.topic || 'Computer Science')}`, { headers });
        if (res.ok) {
          const data = await res.json();
          ytLinks = (data.youtube || []).map(r =>
            `<a href="${r.url}" target="_blank" rel="noopener noreferrer" style="color:#FF4444;text-decoration:none;font-weight:600;display:flex;align-items:center;gap:6px;padding:8px 12px;background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.2);border-radius:8px;margin-bottom:6px;">` +
            `▶ ${r.title}</a>`
          ).join('');
          webLinks = (data.websites || []).map(r =>
            `<a href="${r.url}" target="_blank" rel="noopener noreferrer" style="color:#60A5FA;text-decoration:none;font-weight:600;display:flex;align-items:center;gap:6px;padding:8px 12px;background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);border-radius:8px;margin-bottom:6px;">🌐 ${r.title}</a>`
          ).join('');
        }
      } catch { /* silent */ }

      if (!ytLinks) {
        const q = encodeURIComponent((state.cfg?.topic || 'computer science') + ' tutorial');
        ytLinks = `<a href="https://www.youtube.com/results?search_query=${q}" target="_blank" rel="noopener noreferrer" style="color:#FF4444;text-decoration:none;font-weight:600;padding:8px 12px;background:rgba(255,68,68,0.08);border:1px solid rgba(255,68,68,0.2);border-radius:8px;display:block;margin-bottom:6px;">▶ ${state.cfg?.topic} Tutorial – YouTube Search</a>`;
      }
      if (!webLinks) {
        webLinks = `<a href="https://www.geeksforgeeks.org/?s=${encodeURIComponent(state.cfg?.topic || '')}" target="_blank" rel="noopener noreferrer" style="color:#60A5FA;text-decoration:none;font-weight:600;padding:8px 12px;background:rgba(96,165,250,0.08);border:1px solid rgba(96,165,250,0.2);border-radius:8px;display:block;margin-bottom:6px;">🌐 GeeksforGeeks – ${state.cfg?.topic}</a>`;
      }

      const resourceTitle = isWeak
        ? `Don't worry! Use these resources to strengthen your understanding. 🚀`
        : `Good score! Use these to improve further — aim for 100% next time! 🚀`;

      addMsg(
        `📚 <strong>Recommended Resources — <span style="color:#F59E0B">${state.cfg?.topic || 'this topic'}</span></strong><br><br>` +
        `${resourceTitle}<br><br>` +
        `<div style="padding:4px 0"><strong style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.55">🎦 YouTube Videos</strong></div>` +
        `<div style="margin:8px 0 14px">${ytLinks}</div>` +
        `<div style="padding:4px 0"><strong style="font-size:0.8rem;text-transform:uppercase;letter-spacing:0.08em;opacity:0.55">🌐 Websites</strong></div>` +
        `<div style="margin:8px 0">${webLinks}</div>`,
        'ai'
      );
    }

    // ── Post-quiz end ──
    await delay(needsResources ? 2200 : 1400);
    addMsg(
      `👋 <strong>Great effort, ${firstNameDisplay}!</strong><br><br>` +
      `Quiz complete! Scored <strong>${state.score}/${total}</strong> (${pct}%). See you in the next session!`,
      'ai'
    );
    setPhase('done');
    setChips([]);

    // NOTE: Mentor final report is sent by the backend scheduler at quiz deadline only.
    // Do NOT call notifySessionEnd() here — that caused a per-student email on every completion.
  }

  const handleLogout = () => { sessionStorage.clear(); navigate('/student-login'); };

  /* ─── Derived ─── */
  const yearLabel = { '1': '1st Year', '2': '2nd Year', '3': '3rd Year' }[studentYear] || `Year ${studentYear}`;
  const avgScore  = scores.length ? Math.round(scores.reduce((s, r) => s + r.percentage, 0) / scores.length) : null;
  const bestScore = scores.length ? Math.max(...scores.map(s => s.percentage)) : null;

  /* ─────────────────────────────────────────────────────────
     RENDER
  ───────────────────────────────────────────────────────── */
  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg, #0A0A0A)', color: 'var(--text-primary, #fff)', fontFamily: "'Inter', sans-serif", display: 'flex', flexDirection: 'column' }}>

      {/* ── Top Nav ── */}
      <nav style={{ background: 'var(--navbar-scroll-bg, rgba(10,10,10,0.85))', backdropFilter: 'blur(16px)', borderBottom: '1px solid var(--border, rgba(212,175,55,0.12))', padding: '0 28px', height: 60, display: 'flex', alignItems: 'center', justifyContent: 'space-between', position: 'sticky', top: 0, zIndex: 200 }}>
        <Link to="/" style={{ display: 'flex', alignItems: 'center', gap: 10, textDecoration: 'none' }}>
          <svg width="26" height="26" viewBox="0 0 34 34" fill="none">
            <circle cx="17" cy="17" r="13" fill="none" stroke="url(#navG)" strokeWidth="2"/>
            <path d="M9 22 Q17 9 25 22" stroke="url(#navG)" strokeWidth="2.5" fill="none" strokeLinecap="round"/>
            <circle cx="17" cy="14" r="2.8" fill="url(#navG)"/>
            <defs><linearGradient id="navG" x1="0" y1="0" x2="34" y2="34"><stop offset="0%" stopColor="#D4AF37"/><stop offset="100%" stopColor="#F5C518"/></linearGradient></defs>
          </svg>
          <span style={{ fontFamily: "'Outfit', sans-serif", fontWeight: 800, fontSize: '1.1rem', color: 'var(--text-primary)' }}>
            EduMentor <span style={{ background: 'linear-gradient(135deg,#D4AF37,#F5C518)', WebkitBackgroundClip: 'text', WebkitTextFillColor: 'transparent', backgroundClip: 'text' }}>AI</span>
          </span>
        </Link>

        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {/* Home Button */}
          <Link to="/" id="student-home-btn" style={{
            display: 'flex', alignItems: 'center', gap: 6,
            background: 'rgba(212,175,55,0.08)', border: '1px solid rgba(212,175,55,0.2)',
            borderRadius: 8, padding: '6px 14px', textDecoration: 'none',
            color: 'var(--text-secondary)', fontSize: '0.8rem', fontWeight: 600,
            transition: 'all 0.2s',
          }}
            onMouseEnter={e => { e.currentTarget.style.background = 'rgba(212,175,55,0.15)'; e.currentTarget.style.color = 'var(--text-primary)'; }}
            onMouseLeave={e => { e.currentTarget.style.background = 'rgba(212,175,55,0.08)'; e.currentTarget.style.color = 'var(--text-secondary)'; }}>
            🏠 Home
          </Link>

          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{ width: 34, height: 34, borderRadius: '50%', background: 'linear-gradient(135deg,#D4AF37,#F5C518)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 800, fontSize: '0.85rem', color: '#0A0A0A' }}>
              {firstNameDisplay[0]?.toUpperCase()}
            </div>
            <div>
              <div style={{ fontWeight: 600, fontSize: '0.82rem', lineHeight: 1.2, color: 'var(--text-primary)' }}>{firstNameDisplay}</div>
              <div style={{ fontSize: '0.68rem', color: 'rgba(212,175,55,0.8)', fontWeight: 600 }}>{yearLabel}</div>
            </div>
          </div>
          <ThemeToggle minWidth="60px" />
          <button id="student-logout-btn" onClick={handleLogout} style={{ background: 'transparent', border: '1px solid var(--border-faint)', color: 'var(--text-muted)', cursor: 'pointer', fontSize: '0.78rem', fontWeight: 600, fontFamily: 'inherit', padding: '6px 14px', borderRadius: 8, transition: 'all 0.2s' }}>
            Sign out
          </button>
        </div>
      </nav>

      {/* ── Body ── */}
      <div style={{ flex: 1, display: 'flex', overflow: 'hidden', height: 'calc(100vh - 58px)' }}>

        {/* ══════════ LEFT SIDEBAR — ChatGPT style ══════════ */}
        <aside id="student-dashboard-panel" style={{ width: 300, minWidth: 260, background: 'var(--surface, #111118)', borderRight: '1px solid var(--border-faint)', display: 'flex', flexDirection: 'column', overflow: 'hidden' }}>

          {/* Sidebar Tabs */}
          <div style={{ display: 'flex', borderBottom: '1px solid var(--border-faint)', padding: '0 4px', flexShrink: 0 }}>
            {[{ id: 'overview', label: 'Overview', icon: '⚡' }, { id: 'history', label: 'History', icon: '📋' }].map(tab => (
              <button key={tab.id} onClick={() => setSidebarTab(tab.id)} style={{
                flex: 1, background: 'transparent', border: 'none',
                borderBottom: sidebarTab === tab.id ? '2px solid #D4AF37' : '2px solid transparent',
                color: sidebarTab === tab.id ? '#D4AF37' : 'var(--text-muted)',
                cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600, fontSize: '0.75rem',
                padding: '12px 4px', transition: 'all 0.2s', letterSpacing: '0.03em',
              }}>
                {tab.icon} {tab.label}
              </button>
            ))}
          </div>

          <div style={{ flex: 1, overflowY: 'auto', padding: '14px 12px', display: 'flex', flexDirection: 'column', gap: 12 }}>

            {/* ── OVERVIEW TAB ── */}
            {sidebarTab === 'overview' && (<>

              {/* Profile */}
              <div style={{ background: 'linear-gradient(135deg,rgba(212,175,55,0.1),rgba(212,175,55,0.03))', border: '1px solid rgba(212,175,55,0.15)', borderRadius: 12, padding: 14 }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <div style={{ width: 40, height: 40, borderRadius: '50%', background: 'linear-gradient(135deg,#D4AF37,#F5C518)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 900, fontSize: '1rem', color: '#0A0A0A', flexShrink: 0 }}>
                    {firstNameDisplay[0]?.toUpperCase()}
                  </div>
                  <div style={{ minWidth: 0 }}>
                    <div style={{ fontWeight: 700, fontSize: '0.9rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{studentName}</div>
                    <div style={{ fontSize: '0.68rem', color: 'rgba(212,175,55,0.7)', fontWeight: 600 }}>{yearLabel} · Student</div>
                  </div>
                </div>
                <div style={{ marginTop: 10, fontSize: '0.68rem', color: 'var(--text-muted)' }}>
                  📅 {new Date().toLocaleDateString('en-IN', { weekday: 'long', day: 'numeric', month: 'long' })}
                </div>
              </div>

              {/* Today's Assignment */}
              <div>
                <div style={sectionLabel}>📌 Today's Assignment</div>
                {loadingTopic ? (
                  <div style={cardBase}>
                    <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                      <div style={{ width: 14, height: 14, border: '2px solid rgba(212,175,55,0.3)', borderTopColor: '#D4AF37', borderRadius: '50%', animation: 'spin 0.8s linear infinite', flexShrink: 0 }} />
                      <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>Fetching from mentor...</span>
                    </div>
                  </div>
                ) : (todayTopic && !todayTopic.is_expired) ? (
                  <div style={{ ...cardBase, borderColor: 'rgba(212,175,55,0.2)', background: 'rgba(212,175,55,0.05)' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', gap: 8 }}>
                      <div style={{ minWidth: 0 }}>
                        <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-primary)', marginBottom: 2 }}>{todayTopic.topic}</div>
                        <div style={{ fontSize: '0.7rem', color: 'var(--text-muted)' }}>{todayTopic.subject}</div>
                      </div>
                      <span style={{ background: 'rgba(212,175,55,0.12)', color: '#D4AF37', border: '1px solid rgba(212,175,55,0.25)', borderRadius: 99, padding: '2px 8px', fontSize: '0.62rem', fontWeight: 700, whiteSpace: 'nowrap', flexShrink: 0 }}>Active</span>
                    </div>
                    {todayTopic.counts && (
                      <div style={{ marginTop: 8, display: 'flex', gap: 5, flexWrap: 'wrap' }}>
                        {todayTopic.counts.mcq > 0 && <span style={tagStyle}>{todayTopic.counts.mcq} MCQ</span>}
                        {todayTopic.counts.tf > 0 && <span style={tagStyle}>{todayTopic.counts.tf} T/F</span>}
                        {todayTopic.counts.fill > 0 && <span style={tagStyle}>{todayTopic.counts.fill} Fill</span>}
                      </div>
                    )}
                  </div>
                ) : (
                  <div style={{ ...cardBase, textAlign: 'center', borderStyle: 'dashed' }}>
                    <div style={{ fontSize: '1.2rem', marginBottom: 4 }}>📭</div>
                    <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>No topic set today</div>
                  </div>
                )}
              </div>


              {/* Latest Result */}
              {sessionScore && (
                <div>
                  <div style={sectionLabel}>🎯 Latest Result</div>
                  <div style={{ ...cardBase, background: scoreColor(sessionScore.pct) === '#10B981' ? 'rgba(16,185,129,0.07)' : scoreColor(sessionScore.pct) === '#D4AF37' ? 'rgba(212,175,55,0.07)' : 'rgba(239,68,68,0.07)', borderColor: `${scoreColor(sessionScore.pct)}33`, textAlign: 'center' }}>
                    <div style={{ fontSize: '2rem', fontWeight: 800, fontFamily: "'Outfit', sans-serif", color: scoreColor(sessionScore.pct), lineHeight: 1 }}>{sessionScore.pct}%</div>
                    <div style={{ fontSize: '0.72rem', color: 'var(--text-muted)', marginTop: 4 }}>{sessionScore.score}/{sessionScore.total} correct</div>
                    <div style={{ marginTop: 8, background: 'var(--score-track)', borderRadius: 99, height: 4 }}>
                      <div style={{ height: '100%', width: `${sessionScore.pct}%`, background: scoreColor(sessionScore.pct), borderRadius: 99, transition: 'width 1s ease' }} />
                    </div>
                    <div style={{ marginTop: 6, fontSize: '0.7rem', color: scoreColor(sessionScore.pct), fontWeight: 700 }}>{scoreLabel(sessionScore.pct)}</div>
                  </div>
                </div>
              )}

              {/* Stats Grid */}
              <div>
                <div style={sectionLabel}>📈 Performance</div>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 7 }}>
                  {[
                    { label: 'Quizzes', value: scores.length || 0, icon: '🎯', color: '#D4AF37' },
                    { label: 'Average', value: avgScore != null ? `${avgScore}%` : '—', icon: '📊', color: avgScore != null ? scoreColor(avgScore) : 'var(--text-muted)' },
                    { label: 'Best', value: bestScore != null ? `${bestScore}%` : '—', icon: '🏆', color: '#F59E0B' },
                    { label: 'Year', value: yearLabel.split(' ')[0], icon: '🎓', color: '#60A5FA' },
                  ].map(stat => (
                    <div key={stat.label} style={{ background: 'var(--glass)', border: '1px solid var(--border-faint)', borderRadius: 10, padding: '10px 8px', textAlign: 'center' }}>
                      <div style={{ fontSize: '0.95rem', marginBottom: 3 }}>{stat.icon}</div>
                      <div style={{ fontWeight: 800, fontSize: '0.9rem', color: stat.color }}>{stat.value}</div>
                      <div style={{ fontSize: '0.6rem', color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.06em', marginTop: 2 }}>{stat.label}</div>
                    </div>
                  ))}
                </div>
              </div>
            </>)}

            {/* ── HISTORY TAB ── */}
            {sidebarTab === 'history' && (<>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 2 }}>
                <div style={sectionLabel}>📋 Quiz History</div>
                <div style={{ display: 'flex', gap: 6 }}>
                  <button onClick={fetchHistory} style={{ background: 'transparent', border: 'none', color: 'rgba(212,175,55,0.7)', cursor: 'pointer', fontSize: '0.7rem', fontWeight: 600, fontFamily: 'inherit', padding: '2px 4px' }}>↻ Refresh</button>
                </div>
              </div>

              {loadingHistory ? (
                <div style={{ textAlign: 'center', padding: '30px 0', color: 'var(--text-muted)' }}>
                  <div style={{ width: 18, height: 18, border: '2px solid rgba(212,175,55,0.2)', borderTopColor: '#D4AF37', borderRadius: '50%', animation: 'spin 0.8s linear infinite', margin: '0 auto 10px' }} />
                  <div style={{ fontSize: '0.75rem' }}>Loading...</div>
                </div>
              ) : scores.length === 0 ? (
                <div style={{ textAlign: 'center', padding: '40px 0', color: 'var(--text-muted)' }}>
                  <div style={{ fontSize: '2rem', marginBottom: 8 }}>📭</div>
                  <div style={{ fontSize: '0.78rem' }}>No quizzes yet.<br/>Complete one to see history!</div>
                </div>
              ) : (
                scores.map((s, i) => (
                  <div key={i} className="history-item" style={{ background: 'var(--glass)', border: '1px solid var(--border-faint)', borderRadius: 11, padding: '11px 13px', display: 'flex', justifyContent: 'space-between', alignItems: 'center', gap: 8, transition: 'all 0.2s' }}>
                    <div style={{ minWidth: 0 }}>
                      <div style={{ fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-primary)', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{s.topic}</div>
                      <div style={{ fontSize: '0.65rem', color: 'var(--text-muted)', marginTop: 2 }}>{s.date} · {s.score}</div>
                    </div>
                    <div style={{ textAlign: 'right', flexShrink: 0 }}>
                      <div style={{ fontWeight: 800, fontSize: '0.95rem', color: scoreColor(s.percentage) }}>{s.percentage}%</div>
                      <div style={{ fontSize: '0.58rem', color: scoreColor(s.percentage), opacity: 0.8, fontWeight: 700, marginTop: 1 }}>{scoreLabel(s.percentage).split(' ')[0]}</div>
                    </div>
                  </div>
                ))
              )}

              {scores.length > 0 && (
                <div style={{ marginTop: 4, padding: '12px 13px', background: 'rgba(212,175,55,0.05)', border: '1px solid rgba(212,175,55,0.1)', borderRadius: 11 }}>
                  {[
                    ['Attempts', scores.length, '#D4AF37'],
                    ['Average', avgScore != null ? `${avgScore}%` : '—', avgScore != null ? scoreColor(avgScore) : 'var(--text-muted)'],
                    ['Best', bestScore != null ? `${bestScore}%` : '—', '#F59E0B'],
                  ].map(([label, val, col]) => (
                    <div key={label} style={{ display: 'flex', justifyContent: 'space-between', fontSize: '0.75rem', marginBottom: 5 }}>
                      <span style={{ color: 'var(--text-secondary)' }}>{label}</span>
                      <span style={{ fontWeight: 700, color: col }}>{val}</span>
                    </div>
                  ))}
                </div>
              )}
            </>)}
          </div>
        </aside>

        {/* ══════════ RIGHT PANEL — Chatbot ══════════ */}
        <main style={{ flex: 1, display: 'flex', flexDirection: 'column', overflow: 'hidden', background: 'var(--surface2, #0D0D14)' }}>

          {/* Chat header */}
          <div style={{ padding: '11px 24px', borderBottom: '1px solid var(--border-faint)', display: 'flex', alignItems: 'center', gap: 12, background: 'var(--surface, rgba(13,13,20,0.8))', flexShrink: 0 }}>
            <div style={{ position: 'relative' }}>
              <div style={{ width: 36, height: 36, borderRadius: '50%', background: 'linear-gradient(135deg,#D4AF37,#F5C518)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: '1rem' }}>🤖</div>
              <div style={{ position: 'absolute', bottom: 1, right: 1, width: 9, height: 9, background: '#10B981', borderRadius: '50%', border: '2px solid var(--surface2)' }} />
            </div>
            <div>
              <div style={{ fontWeight: 700, fontSize: '0.88rem', color: 'var(--text-primary)' }}>EduMentor AI Tutor</div>
              <div style={{ fontSize: '0.67rem', color: '#10B981', fontWeight: 600 }}>● Online — Ready to help</div>
            </div>
            {quiz?.active && (
              <div style={{ marginLeft: 'auto', background: 'rgba(212,175,55,0.1)', border: '1px solid rgba(212,175,55,0.25)', borderRadius: 99, padding: '4px 12px', fontSize: '0.7rem', fontWeight: 700, color: '#D4AF37' }}>
                📝 Q{quiz.step + 1}/{quiz.questions.length}
              </div>
            )}
            {quizDoneToday && !quiz?.active && (
              <div style={{ marginLeft: 'auto', background: 'rgba(16,185,129,0.1)', border: '1px solid rgba(16,185,129,0.25)', borderRadius: 99, padding: '4px 12px', fontSize: '0.7rem', fontWeight: 700, color: '#10B981' }}>
                ✅ Today's Quiz Complete
              </div>
            )}
          </div>

          {/* Messages */}
          <div ref={chatRef} id="chat-messages-area" style={{ flex: 1, overflowY: 'auto', padding: '22px 28px 10px', display: 'flex', flexDirection: 'column', gap: 12 }}>
            {messages.length === 0 && (
              <div style={{ textAlign: 'center', color: 'var(--text-faint)', marginTop: 80 }}>
                <div style={{ fontSize: '2.5rem', marginBottom: 10 }}>💬</div>
                <div style={{ fontSize: '0.83rem' }}>Initializing session...</div>
              </div>
            )}
            {messages.map(m => (
              <div key={m.id} style={{
                maxWidth: '72%', padding: '12px 18px', borderRadius: 18, fontSize: '0.88rem', lineHeight: 1.65,
                ...(m.sender === 'ai'
                  ? { background: 'var(--ai-bubble-bg)', border: '1px solid var(--ai-bubble-border)', alignSelf: 'flex-start', borderBottomLeftRadius: 4, color: 'var(--text-primary)' }
                  : { background: 'linear-gradient(135deg,#D4AF37,#E5C43A)', color: '#0A0A0A', fontWeight: 600, alignSelf: 'flex-end', borderBottomRightRadius: 4 }
                )
              }} dangerouslySetInnerHTML={{ __html: m.html }} />
            ))}
            {typing && (
              <div style={{ maxWidth: '72%', padding: '13px 18px', borderRadius: 18, alignSelf: 'flex-start', background: 'rgba(255,255,255,0.04)', border: '1px solid rgba(255,255,255,0.07)', borderBottomLeftRadius: 4 }}>
                <div style={{ display: 'flex', gap: 5, alignItems: 'center' }}>
                  {[0, 0.18, 0.36].map((d, i) => (
                    <span key={i} style={{ width: 7, height: 7, background: '#D4AF37', borderRadius: '50%', display: 'inline-block', animation: `sdBounce 1.1s ${d}s infinite ease-in-out`, opacity: 0.6 }} />
                  ))}
                </div>
              </div>
            )}
          </div>

          {/* Chips */}
          {chips.length > 0 && (
            <div style={{ padding: '8px 28px', display: 'flex', gap: 7, flexWrap: 'wrap', flexShrink: 0 }}>
              {chips.map((c, i) => (
                <button key={i} id={`chip-${i}`} onClick={() => handleChip(c)} style={{ background: 'var(--glass)', border: '1px solid var(--border-faint)', padding: '7px 15px', borderRadius: 99, fontSize: '0.78rem', color: 'var(--text-secondary)', cursor: 'pointer', fontFamily: 'inherit', fontWeight: 600, transition: 'all 0.18s', whiteSpace: 'nowrap' }}>
                  {c.label}
                </button>
              ))}
            </div>
          )}

          {/* Input */}
          <div style={{ padding: '10px 28px 18px', flexShrink: 0 }}>
            <form id="student-chat-form" onSubmit={e => { e.preventDefault(); handleSend(); }} style={{ background: 'var(--glass)', border: '1px solid var(--border-faint)', borderRadius: 14, padding: '7px 7px 7px 18px', display: 'flex', alignItems: 'center', gap: 8, boxShadow: 'var(--shadow-card)' }}>
              <input
                ref={inputRef}
                id="student-chat-input"
                type="text"
                value={input}
                onChange={e => setInput(e.target.value)}
                placeholder={quiz?.active ? "Type your answer..." : "Message EduMentor AI..."}
                autoComplete="off"
                style={{ flex: 1, background: 'transparent', border: 'none', outline: 'none', color: 'var(--text-primary)', fontSize: '0.88rem', fontFamily: 'inherit' }}
              />
              <button type="submit" id="student-chat-send" style={{ background: input.trim() ? 'linear-gradient(135deg,#D4AF37,#F5C518)' : 'var(--glass-strong)', color: input.trim() ? '#0A0A0A' : 'var(--text-muted)', border: 'none', borderRadius: 10, width: 36, height: 36, display: 'flex', alignItems: 'center', justifyContent: 'center', cursor: input.trim() ? 'pointer' : 'default', flexShrink: 0, transition: 'all 0.2s' }}>
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"/><polygon points="22 2 15 22 11 13 2 9 22 2" fill="currentColor"/></svg>
              </button>
            </form>
            <div style={{ textAlign: 'center', fontSize: '0.63rem', color: 'var(--text-faint)', marginTop: 7 }}>
              EduMentor AI · Secure Learning Session
            </div>
          </div>
        </main>
      </div>

      <style>{`
        @keyframes sdBounce { 0%,100%{transform:translateY(0);opacity:0.3} 50%{transform:translateY(-5px);opacity:1} }
        @keyframes spin { to { transform: rotate(360deg); } }
        #student-dashboard-panel::-webkit-scrollbar { width:4px; }
        #student-dashboard-panel::-webkit-scrollbar-thumb { background:rgba(212,175,55,0.2); border-radius:4px; }
        #chat-messages-area::-webkit-scrollbar { width:4px; }
        #chat-messages-area::-webkit-scrollbar-thumb { background:rgba(212,175,55,0.15); border-radius:4px; }
        button[id^="chip-"]:hover { background:rgba(212,175,55,0.18)!important; border-color:rgba(212,175,55,0.45)!important; color:#fff!important; transform:translateY(-1px); }
        #student-chat-send:hover { transform:scale(1.08); }
        #student-logout-btn:hover { background:rgba(255,255,255,0.08)!important; color:rgba(255,255,255,0.8)!important; }
        @media (max-width: 768px) {
          #student-dashboard-panel { display: none; }
        }
      `}</style>
    </div>
  );
}

const tagStyle = {
  background: 'rgba(212,175,55,0.1)',
  border: '1px solid rgba(212,175,55,0.2)',
  borderRadius: 99,
  padding: '2px 10px',
  fontSize: '0.7rem',
  fontWeight: 700,
  color: '#D4AF37',
};

const sectionLabel = {
  fontSize: '0.62rem',
  fontWeight: 700,
  textTransform: 'uppercase',
  letterSpacing: '0.1em',
  color: 'var(--text-muted)',
  marginBottom: 7,
};

const cardBase = {
  background: 'var(--glass)',
  border: '1px solid var(--border-faint)',
  borderRadius: 12,
  padding: '12px 14px',
};

function scoreColor(pct) {
  if (pct >= 80) return '#10B981';
  if (pct >= 50) return '#D4AF37';
  return '#EF4444';
}

function scoreLabel(pct) {
  if (pct >= 80) return '🌟 Excellent';
  if (pct >= 50) return '💪 Good effort';
  return '📚 Needs review';
}
