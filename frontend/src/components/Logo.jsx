export default function Logo({ size = 34 }) {
  return (
    <svg width={size} height={size} viewBox="0 0 34 34" fill="none">
      <rect width="34" height="34" rx="10" fill="#0A0A0A" stroke="rgba(212,175,55,0.5)" strokeWidth="1"/>
      <circle cx="17" cy="17" r="13" fill="none" stroke="url(#lG)" strokeWidth="1.2" opacity="0.6"/>
      <path d="M9 22 Q17 9 25 22" stroke="url(#lG)" strokeWidth="2.2" fill="none" strokeLinecap="round"/>
      <circle cx="17" cy="14" r="2.8" fill="url(#lG)"/>
      <circle cx="11" cy="22" r="1.8" fill="url(#lG)" opacity="0.7"/>
      <circle cx="23" cy="22" r="1.8" fill="url(#lG)" opacity="0.7"/>
      <defs>
        <linearGradient id="lG" x1="0" y1="0" x2="34" y2="34">
          <stop offset="0%" stopColor="#D4AF37"/>
          <stop offset="100%" stopColor="#F5C518"/>
        </linearGradient>
      </defs>
    </svg>
  );
}
