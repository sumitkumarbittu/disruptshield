/**
 * Dashboard Page — aggregated analytics view.
 */

import { useState, useEffect } from 'react';
import { getDashboardSummary } from '../api/client';
import Loading from '../components/Loading';

export default function DashboardPage() {
    const [summary, setSummary] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    useEffect(() => {
        fetchSummary();
    }, []);

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

    if (loading) return <Loading text="Loading dashboard..." />;

    if (error) {
        return (
            <div>
                <div className="page-header">
                    <h2>Dashboard</h2>
                    <p>System overview and analytics</p>
                </div>
                <div className="error-banner">⚠️ {error}</div>
            </div>
        );
    }

    const stats = [
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
    ];

    return (
        <div>
            <div className="page-header">
                <h2>Dashboard</h2>
                <p>Real-time system overview and analytics</p>
            </div>

            <div className="stats-grid">
                {stats.map((stat, i) => (
                    <div className="stat-card" key={i}>
                        <div className="stat-label">
                            <span style={{ marginRight: 6 }}>{stat.icon}</span>
                            {stat.label}
                        </div>
                        <div className={`stat-value ${stat.accent ? 'accent' : ''}`}>
                            {stat.value}
                        </div>
                    </div>
                ))}
            </div>

            <div className="card mt-6">
                <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 16 }}>System Flow</h3>
                <div style={{ fontSize: '0.85rem', color: 'var(--text-secondary)', lineHeight: 2 }}>
                    <code style={{ color: 'var(--accent-primary)' }}>CSV Upload</code>
                    {' → '}
                    <code style={{ color: 'var(--text-accent)' }}>Riders Created</code>
                    {' → '}
                    <code style={{ color: 'var(--accent-secondary)' }}>Policies Created</code>
                    {' → '}
                    <code style={{ color: 'var(--status-success)' }}>Premium Calculated</code>
                    {' → '}
                    <code style={{ color: 'var(--status-warning)' }}>Disruption Event</code>
                    {' → '}
                    <code style={{ color: 'var(--status-info)' }}>Claim Submitted</code>
                    {' → '}
                    <code style={{ color: 'var(--status-review)' }}>Fusion Decision</code>
                    {' → '}
                    <code style={{ color: 'var(--status-success)' }}>Payout Processed</code>
                    {' → '}
                    <code style={{ color: 'var(--accent-primary)' }}>Post-Payout Engine</code>
                </div>
            </div>
        </div>
    );
}
