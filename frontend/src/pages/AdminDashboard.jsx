/**
 * Admin Dashboard — analytics + data management for admins.
 * Does NOT contain generation tasks (locked to backend scripts).
 */

import { useState, useEffect } from 'react';
import { getDashboardSummary } from '../api/client';
import Loading from '../components/Loading';

export default function AdminDashboard() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => { fetchSummary(); }, []);

    const fetchSummary = async () => {
        try {
            setLoading(true);
            const res = await getDashboardSummary();
            setSummary(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading text="Loading admin dashboard..." />;

    const stats = summary ? [
        { label: 'Total Riders', value: summary.total_riders, icon: '🏍️' },
        { label: 'Active Policies', value: summary.active_policies, icon: '📄' },
        { label: 'Total Claims', value: summary.total_claims, icon: '📋' },
        { label: 'Approved', value: summary.approved_claims, icon: '✅', accent: true },
        { label: 'Rejected', value: summary.rejected_claims, icon: '❌' },
        { label: 'In Review', value: summary.review_claims, icon: '🔍' },
        { label: 'Total Payouts', value: `₹${summary.total_payouts.toLocaleString()}`, icon: '💰', accent: true },
        { label: 'Active Events', value: `${summary.active_events} / ${summary.total_events}`, icon: '⚡' },
        { label: 'Avg Premium', value: `₹${summary.avg_premium.toFixed(2)}`, icon: '💎' },
        { label: 'Avg Risk Score', value: summary.avg_risk_score.toFixed(4), icon: '📈' },
    ] : [];

    return (
        <div>
            <div className="page-header">
                <h2>Admin Dashboard</h2>
                <p>System analytics and metrics</p>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {/* System Constraints Info */}
            <div className="card mb-6">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>🔧 System Operations</h3>
                <p className="text-xs text-muted mt-4">
                    Data generation is locked in the production environment.
                    Please execute the backend <code>POST /admin/seed-data</code> endpoint safely or run the <code>scripts.seed_data</code> physically on the backend interface.
                </p>
            </div>

            {/* Stats */}
            {summary && (
                <div className="stats-grid">
                    {stats.map((s, i) => (
                        <div className="stat-card" key={i}>
                            <div className="stat-label"><span style={{ marginRight: 6 }}>{s.icon}</span>{s.label}</div>
                            <div className={`stat-value ${s.accent ? 'accent' : ''}`}>{s.value}</div>
                        </div>
                    ))}
                </div>
            )}

            {/* System Flow */}
            <div className="card mt-6">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>System Flow</h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 2 }}>
                    <code style={{ color: 'var(--accent-primary)' }}>Riders Created</code>
                    {' → '}
                    <code style={{ color: 'var(--text-accent)' }}>Policies Created</code>
                    {' → '}
                    <code style={{ color: 'var(--status-success)' }}>Premium Calculated</code>
                    {' → '}
                    <code style={{ color: 'var(--status-warning)' }}>Events Occur</code>
                    {' → '}
                    <code style={{ color: 'var(--status-info)' }}>Submit Claims</code>
                    {' → '}
                    <code style={{ color: 'var(--status-review)' }}>Fusion Decision</code>
                    {' → '}
                    <code style={{ color: 'var(--status-success)' }}>Process Payout</code>
                    {' → '}
                    <code style={{ color: 'var(--accent-primary)' }}>Post-Payout Engine</code>
                </div>
            </div>
        </div>
    );
}
