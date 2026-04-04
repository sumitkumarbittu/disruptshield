/**
 * DisruptShield — Main Application Entry Point
 * Auth-aware routing: Login → Rider Dashboard / Admin Dashboard.
 */

import { useState, useEffect } from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Sidebar from './components/Sidebar';
import LoginPage from './pages/LoginPage';
import RiderDashboard from './pages/RiderDashboard';
import AdminDashboard from './pages/AdminDashboard';
import UploadPage from './pages/UploadPage';
import RidersPage from './pages/RidersPage';
import RiderProfilePage from './pages/RiderProfilePage';
import ClaimsPage from './pages/ClaimsPage';
import PayoutsPage from './pages/PayoutsPage';
import EventsPage from './pages/EventsPage';
import DashboardPage from './pages/DashboardPage';

export default function App() {
  const [user, setUser] = useState(null);

  useEffect(() => {
    // Restore session from localStorage
    const stored = localStorage.getItem('ds_user');
    const token = localStorage.getItem('ds_token');
    if (stored && token) {
      try {
        setUser(JSON.parse(stored));
      } catch {
        localStorage.clear();
      }
    }
  }, []);

  const handleLogin = (data) => {
    setUser(data);
  };

  const handleLogout = () => {
    localStorage.removeItem('ds_token');
    localStorage.removeItem('ds_role');
    localStorage.removeItem('ds_user');
    setUser(null);
  };

  // Not logged in → show login page
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const isAdmin = user.role === 'admin' || user.role === 'superadmin';
  const isRider = user.role === 'rider';

  return (
    <BrowserRouter>
      <div className="app-layout">
        <Sidebar role={user.role} onLogout={handleLogout} user={user} />
        <main className="main-content">
          <Routes>
            {isAdmin && (
              <>
                <Route path="/" element={<AdminDashboard />} />
                <Route path="/analytics" element={<DashboardPage />} />
                <Route path="/upload" element={<UploadPage />} />
                <Route path="/riders" element={<RidersPage />} />
                <Route path="/riders/:riderId" element={<RiderProfilePage />} />
                <Route path="/claims" element={<ClaimsPage />} />
                <Route path="/payouts" element={<PayoutsPage />} />
                <Route path="/events" element={<EventsPage />} />
              </>
            )}
            {isRider && (
              <>
                <Route path="/" element={<RiderDashboard user={user} />} />
              </>
            )}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}
