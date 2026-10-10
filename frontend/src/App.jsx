import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { ThemeProvider } from './context/ThemeContext';
import LandingPage from './pages/LandingPage';
import StudentLoginPage from './pages/StudentLoginPage';
import MentorLoginPage from './pages/MentorLoginPage';
import StudentChatPage from './pages/StudentChatPage';
import StudentDashboardPage from './pages/StudentDashboardPage';
import MentorDashboardPage from './pages/MentorDashboardPage';

export default function App() {
  return (
    <ThemeProvider>
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<LandingPage />} />
          <Route path="/student-login" element={<StudentLoginPage />} />
          <Route path="/mentor-login" element={<MentorLoginPage />} />
          <Route path="/student-chat" element={<StudentChatPage />} />
          <Route path="/student-dashboard" element={<StudentDashboardPage />} />
          <Route path="/mentor-dashboard" element={<MentorDashboardPage />} />
          <Route path="*" element={<LandingPage />} />
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
