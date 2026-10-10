import { Link } from 'react-router-dom';
import Logo from './Logo';

export default function Footer() {
  return (
    <footer className="footer" id="footer" role="contentinfo">
      <div className="footer-container">
        <div className="footer-brand">
          <Link to="/" className="nav-logo footer-logo" id="footer-logo-link">
            <div className="logo-icon" aria-hidden="true">
              <svg width="34" height="34" viewBox="0 0 34 34" fill="none">
                <rect width="34" height="34" rx="10" fill="#0A0A0A" stroke="rgba(212,175,55,0.4)" strokeWidth="1"/>
                <path d="M9 22 Q17 9 25 22" stroke="url(#flG)" strokeWidth="2.2" fill="none" strokeLinecap="round"/>
                <circle cx="17" cy="14" r="2.8" fill="url(#flG)"/>
                <defs>
                  <linearGradient id="flG" x1="0" y1="0" x2="34" y2="34">
                    <stop offset="0%" stopColor="#D4AF37"/>
                    <stop offset="100%" stopColor="#F5C518"/>
                  </linearGradient>
                </defs>
              </svg>
            </div>
            <span className="logo-text">EduMentor <span className="logo-ai">AI</span></span>
          </Link>
          <p className="footer-desc">
            A premium AI-powered platform helping students learn smarter and mentors guide better. Built for the future of education.
          </p>
        </div>

        <div className="footer-links-grid">
          <div className="footer-col">
            <h4 className="footer-col-title">Platform</h4>
            <ul role="list">
              <li><a href="#features" className="footer-link" id="footer-features">Features</a></li>
              <li><a href="#how-it-works" className="footer-link" id="footer-how">How It Works</a></li>
              <li><a href="#roles" className="footer-link" id="footer-roles">For Students</a></li>
              <li><a href="#roles" className="footer-link" id="footer-mentor">For Mentors</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4 className="footer-col-title">Resources</h4>
            <ul role="list">
              <li><a href="#" className="footer-link" id="footer-docs">Documentation</a></li>
              <li><a href="#" className="footer-link" id="footer-blog">Blog</a></li>
              <li><a href="#" className="footer-link" id="footer-faq">FAQ</a></li>
              <li><a href="#" className="footer-link" id="footer-support">Support</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4 className="footer-col-title">Company</h4>
            <ul role="list">
              <li><a href="#" className="footer-link" id="footer-about">About Us</a></li>
              <li><a href="#" className="footer-link" id="footer-careers">Careers</a></li>
              <li><a href="#" className="footer-link" id="footer-privacy">Privacy Policy</a></li>
              <li><a href="#" className="footer-link" id="footer-terms">Terms of Service</a></li>
            </ul>
          </div>
          <div className="footer-col">
            <h4 className="footer-col-title">Contact</h4>
            <ul role="list">
              <li>
                <a
                  href="mailto:support@edumentorai.com"
                  className="footer-link footer-email-link"
                  id="footer-email"
                  aria-label="Email EduMentor AI support"
                >
                  <svg
                    width="13" height="13" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                    strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}
                    aria-hidden="true"
                  >
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  support@edumentorai.com
                </a>
              </li>
              <li>
                <a
                  href="mailto:mentors@edumentorai.com"
                  className="footer-link footer-email-link"
                  id="footer-mentor-email"
                  aria-label="Email EduMentor AI mentor team"
                >
                  <svg
                    width="13" height="13" viewBox="0 0 24 24" fill="none"
                    stroke="currentColor" strokeWidth="2" strokeLinecap="round"
                    strokeLinejoin="round" style={{ flexShrink: 0, marginTop: 1 }}
                    aria-hidden="true"
                  >
                    <path d="M4 4h16c1.1 0 2 .9 2 2v12c0 1.1-.9 2-2 2H4c-1.1 0-2-.9-2-2V6c0-1.1.9-2 2-2z"/>
                    <polyline points="22,6 12,13 2,6"/>
                  </svg>
                  mentors@edumentorai.com
                </a>
              </li>
            </ul>
          </div>
        </div>
      </div>

      <div className="footer-bottom">
        <p id="footer-copyright">© 2026 EduMentor AI. All rights reserved. Built with ✦ for learners worldwide.</p>
        <p id="footer-tagline" className="footer-tagline-bottom">Empowering Education through AI</p>
      </div>
    </footer>
  );
}
