import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import Logo from './Logo';
import ThemeToggle from './ThemeToggle';

export default function Navbar({ onOpenRoleSelect }) {
  const [scrolled, setScrolled] = useState(false);
  const [menuOpen, setMenuOpen] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  const scrollTo = (id) => {
    setMenuOpen(false);
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth' });
  };

  const openRole = () => {
    setMenuOpen(false);
    if (onOpenRoleSelect) onOpenRoleSelect();
  };

  return (
    <nav className={`navbar${scrolled ? ' scrolled' : ''}`} id="navbar" role="navigation" aria-label="Main navigation">
      <div className="nav-container">
        <Link to="/" className="nav-logo" id="nav-logo-link">
          <div className="logo-icon" aria-hidden="true"><Logo /></div>
          <span className="logo-text">EduMentor <span className="logo-ai">AI</span></span>
        </Link>

        <ul className="nav-links" id="nav-links" role="list">
          <li><button className="nav-link nav-link-btn" onClick={() => scrollTo('features')}>Features</button></li>
          <li><button className="nav-link nav-link-btn" onClick={() => scrollTo('how-it-works')}>How It Works</button></li>
          <li><button className="nav-link nav-link-btn" onClick={() => scrollTo('footer')}>Contact</button></li>
        </ul>

        <div className="nav-actions">
          <ThemeToggle />
          <button className="btn btn-outline" onClick={openRole} id="nav-login-btn">Log In</button>
          <button className="btn btn-primary" onClick={openRole} id="nav-signup-btn">Get Started</button>
        </div>

        <button
          className={`hamburger${menuOpen ? ' active' : ''}`}
          id="hamburger-btn"
          aria-label="Toggle navigation menu"
          aria-expanded={menuOpen}
          onClick={() => setMenuOpen(o => !o)}
        >
          <span></span><span></span><span></span>
        </button>
      </div>

      <div className={`mobile-menu${menuOpen ? ' open' : ''}`} id="mobile-menu" aria-hidden={!menuOpen}>
        <button className="mobile-link" onClick={() => scrollTo('features')}>Features</button>
        <button className="mobile-link" onClick={() => scrollTo('how-it-works')}>How It Works</button>
        <button className="mobile-link" onClick={() => scrollTo('footer')}>Contact</button>
        <div className="mobile-theme-row">
          <span className="mobile-theme-label" id="mob-theme-label">🌙 Theme</span>
          <ThemeToggle minWidth="64px" />
        </div>
        <button className="btn btn-primary w-full mt-2" onClick={openRole}>
          Get Started Free
        </button>
      </div>
    </nav>
  );
}
