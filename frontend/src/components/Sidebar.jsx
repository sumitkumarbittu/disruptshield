/**
 * Sidebar navigation component — role-aware.
 * Admins see full navigation, riders see limited menu.
 */

import { NavLink } from 'react-router-dom';

const adminNav = [
    { path: '/', label: 'Admin Dashboard', icon: '🔧' },
    { path: '/analytics', label: 'Analytics', icon: '📊' },
    { path: '/upload', label: 'Upload Riders', icon: '📤' },
    { path: '/riders', label: 'Riders Management', icon: '🏍️' },
    { path: '/claims', label: 'Claims Management', icon: '📋' },
    { path: '/payouts', label: 'Payout Management', icon: '💰' },
    { path: '/events', label: 'Events Management', icon: '⚡' },
];

const riderNav = [
    { path: '/', label: 'My Dashboard', icon: '🏠' },
];

export default function Sidebar({ role, onLogout, user }) {
    const isAdmin = role === 'admin' || role === 'superadmin';
    const navItems = isAdmin ? adminNav : riderNav;

    return (
        <aside className="sidebar">
            <div className="sidebar-brand">
                <h1>DisruptShield</h1>
                <p>Parametric Income Protection</p>
            </div>

            <nav className="sidebar-nav">
                {navItems.map((item) => (
                    <NavLink
                        key={item.path}
                        to={item.path}
                        className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}
                        end={item.path === '/'}
                    >
                        <span className="nav-icon">{item.icon}</span>
                        {item.label}
                    </NavLink>
                ))}
            </nav>

            {/* User info & Logout */}
            <div style={{
                padding: '16px 20px',
                borderTop: '1px solid var(--border-subtle)',
                marginTop: 'auto',
            }}>
                <div style={{ fontSize: '0.8rem', color: 'var(--text-secondary)', marginBottom: 4 }}>
                    {user?.email}
                </div>
                <div className="flex items-center justify-between">
                    <span className={`badge ${isAdmin ? 'badge-review' : 'badge-info'}`} style={{ fontSize: '0.65rem' }}>
                        {role}
                    </span>
                    <button
                        onClick={onLogout}
                        style={{
                            background: 'none',
                            border: 'none',
                            color: 'var(--status-danger)',
                            cursor: 'pointer',
                            fontSize: '0.75rem',
                            fontWeight: 600,
                            fontFamily: 'inherit',
                        }}
                    >
                        Logout →
                    </button>
                </div>
            </div>
        </aside>
    );
}
