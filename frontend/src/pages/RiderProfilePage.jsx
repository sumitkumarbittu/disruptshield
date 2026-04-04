/**
 * Rider Profile Page — detailed view of a single rider.
 */

import { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { getRider, getPolicy, getPremiumHistory, getClaimHistory, getPayoutHistory, recalculatePremium } from '../api/client';
import Loading from '../components/Loading';

export default function RiderProfilePage() {
    const { riderId } = useParams();
    const [rider, setRider] = useState(null);
    const [policy, setPolicy] = useState(null);
    const [premiumHist, setPremiumHist] = useState([]);
    const [claims, setClaims] = useState([]);
    const [payouts, setPayouts] = useState([]);
    const [activeTab, setActiveTab] = useState('overview');
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [recalcMsg, setRecalcMsg] = useState(null);

    useEffect(() => {
        fetchAll();
    }, [riderId]);

    const fetchAll = async () => {
        try {
            setLoading(true);
            const [riderRes, policyRes, premRes, claimRes, payoutRes] = await Promise.allSettled([
                getRider(riderId),
                getPolicy(riderId),
                getPremiumHistory(riderId),
                getClaimHistory(riderId),
                getPayoutHistory(riderId),
            ]);

            if (riderRes.status === 'fulfilled') setRider(riderRes.value.data);
            else throw new Error('Rider not found');

            if (policyRes.status === 'fulfilled') setPolicy(policyRes.value.data);
            if (premRes.status === 'fulfilled') setPremiumHist(premRes.value.data);
            if (claimRes.status === 'fulfilled') setClaims(claimRes.value.data);
            if (payoutRes.status === 'fulfilled') setPayouts(payoutRes.value.data);
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleRecalculate = async () => {
        try {
            const res = await recalculatePremium(riderId);
            setRecalcMsg(`Premium recalculated: ₹${res.data.previous_premium} → ₹${res.data.new_premium}`);
            fetchAll();
        } catch (err) {
            setRecalcMsg(`Error: ${err.response?.data?.detail || err.message}`);
        }
    };

    if (loading) return <Loading text="Loading rider profile..." />;
    if (error) return <div className="error-banner">⚠️ {error}</div>;
    if (!rider) return <div className="error-banner">⚠️ Rider not found</div>;

    const tabs = ['overview', 'premium', 'claims', 'payouts'];

    return (
        <div>
            <div className="page-header">
                <Link to="/riders" style={{ color: 'var(--text-muted)', fontSize: '0.8rem', textDecoration: 'none' }}>
                    ← Back to Riders
                </Link>
                <h2 style={{ marginTop: 8 }}>Rider Profile</h2>
            </div>

            {/* Profile Header */}
            <div className="card mb-6">
                <div className="profile-header">
                    <div className="profile-avatar">
                        {rider.name.charAt(0).toUpperCase()}
                    </div>
                    <div className="profile-info">
                        <h3>{rider.name}</h3>
                        <div className="profile-meta">
                            <span>🆔 {rider.rider_external_id}</span>
                            <span>🏙️ {rider.city}</span>
                            <span>📌 {rider.pin_code}</span>
                            <span>📱 {rider.platform}</span>
                            <span className={`badge ${rider.is_active ? 'badge-success' : 'badge-danger'}`}>
                                {rider.is_active ? 'Active' : 'Inactive'}
                            </span>
                        </div>
                    </div>
                </div>

                <div className="stats-grid" style={{ marginBottom: 0 }}>
                    <div className="stat-card">
                        <div className="stat-label">Weekly Income</div>
                        <div className="stat-value">₹{rider.avg_weekly_income.toLocaleString()}</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Risk Score</div>
                        <div className={`stat-value ${rider.risk_score >= 0.5 ? '' : 'accent'}`}>
                            {rider.risk_score.toFixed(4)}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Current Premium</div>
                        <div className="stat-value accent">
                            ₹{policy ? policy.premium_amount.toFixed(2) : '—'}
                        </div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-label">Total Claims</div>
                        <div className="stat-value">{claims.length}</div>
                    </div>
                </div>
            </div>

            {recalcMsg && <div className="success-banner">{recalcMsg}</div>}

            {/* Tabs */}
            <div className="tabs">
                {tabs.map((tab) => (
                    <button
                        key={tab}
                        className={`tab ${activeTab === tab ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab)}
                    >
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </div>

            {/* Tab Content */}
            {activeTab === 'overview' && (
                <div className="profile-grid">
                    <div className="card">
                        <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 16 }}>Rider Details</h3>
                        <div className="detail-row"><span className="detail-label">External ID</span><span className="detail-value mono">{rider.rider_external_id}</span></div>
                        <div className="detail-row"><span className="detail-label">Phone</span><span className="detail-value">{rider.phone || '—'}</span></div>
                        <div className="detail-row"><span className="detail-label">Email</span><span className="detail-value">{rider.email || '—'}</span></div>
                        <div className="detail-row"><span className="detail-label">Zone</span><span className="detail-value">{rider.zone || rider.pin_code}</span></div>
                        <div className="detail-row"><span className="detail-label">Created</span><span className="detail-value">{rider.created_at ? new Date(rider.created_at).toLocaleDateString() : '—'}</span></div>
                    </div>
                    {policy && (
                        <div className="card">
                            <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 16 }}>Policy Details</h3>
                            <div className="detail-row"><span className="detail-label">Policy #</span><span className="detail-value mono">{policy.policy_number}</span></div>
                            <div className="detail-row"><span className="detail-label">Status</span><span className="badge badge-success">{policy.status}</span></div>
                            <div className="detail-row"><span className="detail-label">City Tier</span><span className="detail-value">{policy.city_tier}</span></div>
                            <div className="detail-row"><span className="detail-label">Base Premium %</span><span className="detail-value">{policy.base_premium_pct}%</span></div>
                            <div className="detail-row"><span className="detail-label">Coverage</span><span className="detail-value">₹{policy.coverage_amount.toFixed(2)}</span></div>
                            <div className="mt-4">
                                <button className="btn btn-primary btn-sm" onClick={handleRecalculate}>
                                    🔄 Recalculate Premium
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            )}

            {activeTab === 'premium' && (
                <div className="table-container">
                    <div className="table-header">
                        <h3>Premium History</h3>
                    </div>
                    {premiumHist.length === 0 ? (
                        <div className="empty-state">No premium history</div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Date</th>
                                    <th>Previous</th>
                                    <th>New</th>
                                    <th>Reason</th>
                                    <th>Income</th>
                                    <th>Zone Risk</th>
                                </tr>
                            </thead>
                            <tbody>
                                {premiumHist.map((h) => (
                                    <tr key={h.id}>
                                        <td>{h.created_at ? new Date(h.created_at).toLocaleString() : '—'}</td>
                                        <td className="font-mono">₹{h.previous_premium?.toFixed(2) || '0.00'}</td>
                                        <td className="font-mono" style={{ color: 'var(--status-success)', fontWeight: 600 }}>₹{h.new_premium.toFixed(2)}</td>
                                        <td><span className="badge badge-info">{h.change_reason}</span></td>
                                        <td className="font-mono">₹{h.weekly_income?.toLocaleString() || '—'}</td>
                                        <td className="font-mono">{h.zone_risk?.toFixed(3) || '—'}</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}
                </div>
            )}

            {activeTab === 'claims' && (
                <div className="table-container">
                    <div className="table-header">
                        <h3>Claim History</h3>
                    </div>
                    {claims.length === 0 ? (
                        <div className="empty-state">No claims submitted</div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Claim #</th>
                                    <th>Status</th>
                                    <th>Decision</th>
                                    <th>Disruption</th>
                                    <th>Behavior</th>
                                    <th>Final Score</th>
                                    <th>Payout</th>
                                    <th>Date</th>
                                </tr>
                            </thead>
                            <tbody>
                                {claims.map((c) => (
                                    <tr key={c.id}>
                                        <td className="font-mono text-xs">{c.claim_number}</td>
                                        <td>
                                            <span className={`badge ${['approve', 'approved', 'paid'].includes(c.status) ? 'badge-success' :
                                                    c.status === 'review' ? 'badge-review' : 'badge-danger'
                                                }`}>
                                                {c.status}
                                            </span>
                                        </td>
                                        <td className="text-xs">{c.decision || '—'}</td>
                                        <td className="font-mono">{c.disruption_score?.toFixed(2) || '—'}</td>
                                        <td className="font-mono">{c.behavior_score?.toFixed(2) || '—'}</td>
                                        <td className="font-mono" style={{ fontWeight: 600 }}>{c.final_score?.toFixed(3) || '—'}</td>
                                        <td className="font-mono">₹{c.payout_amount?.toFixed(2) || '0.00'}</td>
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
                    <div className="table-header">
                        <h3>Payout History</h3>
                    </div>
                    {payouts.length === 0 ? (
                        <div className="empty-state">No payouts processed</div>
                    ) : (
                        <table>
                            <thead>
                                <tr>
                                    <th>Amount</th>
                                    <th>Status</th>
                                    <th>Transaction Ref</th>
                                    <th>Method</th>
                                    <th>Processed At</th>
                                </tr>
                            </thead>
                            <tbody>
                                {payouts.map((p) => (
                                    <tr key={p.id}>
                                        <td className="font-mono" style={{ fontWeight: 600, color: 'var(--status-success)' }}>₹{p.amount.toFixed(2)}</td>
                                        <td><span className="badge badge-success">{p.status}</span></td>
                                        <td className="font-mono text-xs">{p.transaction_ref || '—'}</td>
                                        <td>{p.payment_method || '—'}</td>
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
