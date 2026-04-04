/**
 * Rider Dashboard — personal dashboard for authenticated riders.
 * Shows: profile, policy, premium, claims, payouts.
 */

import { useState, useEffect } from 'react';
import { getRider, getPolicy, getPremiumHistory, getClaimsByRider, getPayoutHistory } from '../api/client';
import Loading from '../components/Loading';

export default function RiderDashboard({ user }) {
    const riderId = user?.rider_id;
    const [rider, setRider] = useState(null);
    const [policy, setPolicy] = useState(null);
    const [premiumHist, setPremiumHist] = useState([]);
    const [claims, setClaims] = useState([]);
    const [payouts, setPayouts] = useState([]);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState('overview');

    useEffect(() => {
        if (!riderId) return;
        fetchAll();
    }, [riderId]);

    const fetchAll = async () => {
        setLoading(true);
        const [r, p, ph, c, po] = await Promise.allSettled([
            getRider(riderId),
            getPolicy(riderId),
            getPremiumHistory(riderId),
            getClaimsByRider(riderId),
            getPayoutHistory(riderId),
        ]);
        if (r.status === 'fulfilled') setRider(r.value.data);
        if (p.status === 'fulfilled') setPolicy(p.value.data);
        if (ph.status === 'fulfilled') setPremiumHist(ph.value.data);
        if (c.status === 'fulfilled') setClaims(c.value.data);
        if (po.status === 'fulfilled') setPayouts(po.value.data);
        setLoading(false);
    };

    if (!riderId) return <div className="error-banner">⚠️ No rider linked to this account</div>;
    if (loading) return <Loading text="Loading your dashboard..." />;
    if (!rider) return <div className="error-banner">⚠️ Rider profile not found</div>;

    const tabs = ['overview', 'premium', 'claims', 'payouts'];
    const approvedClaims = claims.filter(c => ['approve', 'approved', 'paid'].includes(c.status));
    const totalPayout = payouts.reduce((s, p) => s + p.amount, 0);

    return (
        <div>
            <div className="page-header">
                <h2>Welcome, {rider.name}</h2>
                <p>Your DisruptShield dashboard</p>
            </div>

            {/* Key Stats */}
            <div className="stats-grid">
                <div className="stat-card">
                    <div className="stat-label">💎 Current Premium</div>
                    <div className="stat-value accent">₹{policy?.premium_amount?.toFixed(2) || '—'}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">🛡️ Coverage</div>
                    <div className="stat-value">₹{policy?.coverage_amount?.toFixed(2) || '—'}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">📋 Claims</div>
                    <div className="stat-value">{claims.length} <span className="text-xs text-muted">({approvedClaims.length} approved)</span></div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">💰 Total Payouts</div>
                    <div className="stat-value accent">₹{totalPayout.toFixed(2)}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">📈 Risk Score</div>
                    <div className="stat-value">{rider.risk_score.toFixed(4)}</div>
                </div>
                <div className="stat-card">
                    <div className="stat-label">💵 Weekly Income</div>
                    <div className="stat-value">₹{rider.avg_weekly_income.toLocaleString()}</div>
                </div>
            </div>

            {/* Tabs */}
            <div className="tabs">
                {tabs.map(t => (
                    <button key={t} className={`tab ${activeTab === t ? 'active' : ''}`} onClick={() => setActiveTab(t)}>
                        {t.charAt(0).toUpperCase() + t.slice(1)}
                    </button>
                ))}
            </div>

            {activeTab === 'overview' && (
                <div className="profile-grid">
                    <div className="card">
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 16 }}>Profile</h3>
                        <div className="detail-row"><span className="detail-label">ID</span><span className="detail-value mono">{rider.rider_external_id}</span></div>
                        <div className="detail-row"><span className="detail-label">Platform</span><span className="badge badge-info">{rider.platform}</span></div>
                        <div className="detail-row"><span className="detail-label">City</span><span className="detail-value">{rider.city}</span></div>
                        <div className="detail-row"><span className="detail-label">Zone</span><span className="detail-value">{rider.zone || rider.pin_code}</span></div>
                        <div className="detail-row"><span className="detail-label">Phone</span><span className="detail-value">{rider.phone || '—'}</span></div>
                    </div>
                    {policy && (
                        <div className="card">
                            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 16 }}>Policy</h3>
                            <div className="detail-row"><span className="detail-label">Policy #</span><span className="detail-value mono">{policy.policy_number}</span></div>
                            <div className="detail-row"><span className="detail-label">Status</span><span className="badge badge-success">{policy.status}</span></div>
                            <div className="detail-row"><span className="detail-label">Tier</span><span className="detail-value">{policy.city_tier}</span></div>
                            <div className="detail-row"><span className="detail-label">Base %</span><span className="detail-value">{policy.base_premium_pct}%</span></div>
                            <div className="detail-row"><span className="detail-label">Since</span><span className="detail-value">{policy.effective_from ? new Date(policy.effective_from).toLocaleDateString() : '—'}</span></div>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'premium' && (
                <div className="table-container">
                    <div className="table-header"><h3>Premium History</h3></div>
                    {premiumHist.length === 0 ? <div className="empty-state">No records</div> : (
                        <table>
                            <thead><tr><th>Date</th><th>Previous</th><th>New</th><th>Reason</th></tr></thead>
                            <tbody>
                                {premiumHist.map(h => (
                                    <tr key={h.id}>
                                        <td className="text-xs">{h.created_at ? new Date(h.created_at).toLocaleDateString() : '—'}</td>
                                        <td className="font-mono">₹{h.previous_premium?.toFixed(2) || '0'}</td>
                                        <td className="font-mono" style={{ color: 'var(--status-success)', fontWeight: 600 }}>₹{h.new_premium.toFixed(2)}</td>
                                        <td><span className="badge badge-info">{h.change_reason}</span></td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {activeTab === 'claims' && (
                <div className="table-container">
                    <div className="table-header"><h3>My Claims</h3></div>
                    {claims.length === 0 ? <div className="empty-state">No claims</div> : (
                        <table>
                            <thead><tr><th>Claim #</th><th>Status</th><th>Score</th><th>Payout</th><th>Date</th></tr></thead>
                            <tbody>
                                {claims.map(c => (
                                    <tr key={c.id}>
                                        <td className="font-mono text-xs">{c.claim_number}</td>
                                        <td><span className={`badge ${['approve', 'approved', 'paid'].includes(c.status) ? 'badge-success' : c.status === 'review' ? 'badge-review' : 'badge-danger'}`}>{c.status}</span></td>
                                        <td className="font-mono">{c.final_score?.toFixed(3) || '—'}</td>
                                        <td className="font-mono">₹{c.payout_amount?.toFixed(2) || '0'}</td>
                                        <td className="text-xs">{c.created_at ? new Date(c.created_at).toLocaleDateString() : '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {activeTab === 'payouts' && (
                <div className="table-container">
                    <div className="table-header"><h3>My Payouts</h3></div>
                    {payouts.length === 0 ? <div className="empty-state">No payouts</div> : (
                        <table>
                            <thead><tr><th>Amount</th><th>Status</th><th>Txn Ref</th><th>Date</th></tr></thead>
                            <tbody>
                                {payouts.map(p => (
                                    <tr key={p.id}>
                                        <td className="font-mono" style={{ color: 'var(--status-success)', fontWeight: 600 }}>₹{p.amount.toFixed(2)}</td>
                                        <td><span className="badge badge-success">{p.status}</span></td>
                                        <td className="font-mono text-xs">{p.transaction_ref || '—'}</td>
                                        <td className="text-xs">{p.processed_at ? new Date(p.processed_at).toLocaleString() : '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}
        </div>
    );
}
