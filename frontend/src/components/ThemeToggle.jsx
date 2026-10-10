import { useTheme } from '../context/ThemeContext';

export default function ThemeToggle({ minWidth = '76px' }) {
  const { theme, toggleTheme } = useTheme();
  const isDark = theme === 'dark';
  return (
    <button
      className={`theme-toggle ${isDark ? 'theme-dark' : 'theme-light'}`}
      onClick={toggleTheme}
      aria-label="Toggle dark/light mode"
      style={{ minWidth }}
      title={isDark ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
    >
      <span className="toggle-icons">
        <span className="sun-icon">☀️</span>
        <span className="moon-icon">🌙</span>
      </span>
      <span className="toggle-thumb">✦</span>
    </button>
  );
}
