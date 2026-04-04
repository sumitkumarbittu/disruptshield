/**
 * Login Page — Rider or Admin authentication.
 */

import { useState } from 'react';
import { riderLogin, adminLogin } from '../api/client';

export default function LoginPage({ onLogin }) {
    const [mode, setMode] = useState(null); // null | 'rider' | 'admin'
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);

    const handleLogin = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        try {
            const loginFn = mode === 'admin' ? adminLogin : riderLogin;
            const res = await loginFn(email, password);
            const data = res.data;
            localStorage.setItem('ds_token', data.access_token);
            localStorage.setItem('ds_role', data.role);
            localStorage.setItem('ds_user', JSON.stringify(data));
            onLogin(data);
        } catch (err) {
            setError(err.response?.data?.detail || 'Login failed');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div style={{
            minHeight: '100vh',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            background: 'var(--bg-primary)',
            padding: 20,
        }}>
            <div style={{ width: '100%', maxWidth: 460 }}>
                {/* Brand */}
                <div style={{ textAlign: 'center', marginBottom: 40 }}>
                    <h1 style={{
                        fontSize: '2.2rem',
                        fontWeight: 800,
                        background: 'var(--accent-gradient)',
                        WebkitBackgroundClip: 'text',
                        WebkitTextFillColor: 'transparent',
                        letterSpacing: '-0.03em',
                    }}>
                        DisruptShield
                    </h1>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.85rem', marginTop: 6 }}>
                        Parametric Income Protection Platform
                    </p>
                </div>

                {/* Role Selection */}
                {!mode && (
                    <div className="card" style={{ padding: 40, textAlign: 'center' }}>
                        <h2 style={{ fontSize: '1.15rem', fontWeight: 600, marginBottom: 28 }}>
                            Select Login Type
                        </h2>
                        <div className="flex gap-4" style={{ justifyContent: 'center' }}>
                            <button
                                className="btn btn-primary"
                                style={{ minWidth: 160, padding: '14px 24px', fontSize: '0.95rem' }}
                                onClick={() => setMode('rider')}
                            >
                                🏍️ Login as Rider
                            </button>
                            <button
                                className="btn btn-secondary"
                                style={{ minWidth: 160, padding: '14px 24px', fontSize: '0.95rem' }}
                                onClick={() => setMode('admin')}
                            >
                                🔑 Login as Admin
                            </button>
                        </div>
                        <p className="text-xs text-muted mt-6" style={{ lineHeight: 1.8 }}>
                            Rider default: rider1@disruptshield.in / rider123<br />
                            Admin default: admin@disruptshield.in / admin123
                        </p>
                    </div>
                )}

                {/* Login Form */}
                {mode && (
                    <div className="card" style={{ padding: 36 }}>
                        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 24 }}>
                            <h2 style={{ fontSize: '1.1rem', fontWeight: 600 }}>
                                {mode === 'admin' ? '🔑 Admin Login' : '🏍️ Rider Login'}
                            </h2>
                            <button
                                className="btn btn-sm btn-secondary"
                                onClick={() => { setMode(null); setError(null); setEmail(''); setPassword(''); }}
                            >
                                ← Back
                            </button>
                        </div>

                        {error && <div className="error-banner">⚠️ {error}</div>}

                        <form onSubmit={handleLogin}>
                            <div className="form-group">
                                <label className="form-label">Email</label>
                                <input
                                    className="form-input"
                                    type="email"
                                    placeholder={mode === 'admin' ? 'admin@disruptshield.in' : 'rider1@disruptshield.in'}
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    required
                                    autoFocus
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Password</label>
                                <input
                                    className="form-input"
                                    type="password"
                                    placeholder="Enter password"
                                    value={password}
                                    onChange={(e) => setPassword(e.target.value)}
                                    required
                                />
                            </div>
                            <button
                                className="btn btn-primary w-full"
                                type="submit"
                                disabled={loading}
                                style={{ padding: '14px', fontSize: '0.95rem', marginTop: 8 }}
                            >
                                {loading ? 'Signing in...' : 'Sign In'}
                            </button>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );
}
