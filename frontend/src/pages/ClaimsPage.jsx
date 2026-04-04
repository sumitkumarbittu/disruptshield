/**
 * Claims Page — submit claims and view claim decisions.
 */

import { useState, useEffect } from 'react';
import { submitClaim, getClaimsByRider, getEvents } from '../api/client';
import Loading from '../components/Loading';

export default function ClaimsPage() {
    const [claims, setClaims] = useState([]);
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);

    // Form state
    const [riderId, setRiderId] = useState('');
    const [eventId, setEventId] = useState('');
    const [disruptionScore, setDisruptionScore] = useState('');
    const [behaviorScore, setBehaviorScore] = useState('');
    const [searchRiderId, setSearchRiderId] = useState('');
    const [submitting, setSubmitting] = useState(false);

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        try {
            const res = await getEvents();
            setEvents(res.data);
        } catch (err) {
            // Silently handle — events list is supplementary
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!riderId || !eventId) {
            setError('Rider ID and Event ID are required');
            return;
        }

        try {
            setSubmitting(true);
            setError(null);
            setSuccess(null);
            const data = {
                rider_id: parseInt(riderId),
                disruption_event_id: parseInt(eventId),
            };
            if (disruptionScore) data.disruption_score = parseFloat(disruptionScore);
            if (behaviorScore) data.behavior_score = parseFloat(behaviorScore);

            const res = await submitClaim(data);
            setSuccess(`Claim ${res.data.claim_number} submitted — Decision: ${res.data.decision} (Score: ${res.data.final_score?.toFixed(3)})`);
            setRiderId('');
            setEventId('');
            setDisruptionScore('');
            setBehaviorScore('');
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setSubmitting(false);
        }
    };

    const handleSearch = async () => {
        if (!searchRiderId) return;
        try {
            setLoading(true);
            setError(null);
            const res = await getClaimsByRider(searchRiderId);
            setClaims(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>Claims</h2>
                <p>Submit and track insurance claims</p>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}
            {success && <div className="success-banner">✅ {success}</div>}

            <div className="profile-grid mb-6">
                {/* Submit Claim Form */}
                <div className="card">
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Submit New Claim</h3>
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label className="form-label">Rider ID</label>
                            <input
                                className="form-input"
                                type="number"
                                placeholder="e.g., 1"
                                value={riderId}
                                onChange={(e) => setRiderId(e.target.value)}
                                required
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Disruption Event</label>
                            <select
                                className="form-input"
                                value={eventId}
                                onChange={(e) => setEventId(e.target.value)}
                                required
                            >
                                <option value="">Select an event...</option>
                                {events.map((ev) => (
                                    <option key={ev.id} value={ev.id}>
                                        #{ev.id} — {ev.event_type} ({ev.severity}) — Zone: {ev.zone} — Score: {ev.disruption_score.toFixed(2)}
                                    </option>
                                ))}
                            </select>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Disruption Score (optional)</label>
                            <input
                                className="form-input"
                                type="number"
                                step="0.01"
                                min="0"
                                max="1"
                                placeholder="Uses event score if empty"
                                value={disruptionScore}
                                onChange={(e) => setDisruptionScore(e.target.value)}
                            />
                        </div>
                        <div className="form-group">
                            <label className="form-label">Behavior Score (optional)</label>
                            <input
                                className="form-input"
                                type="number"
                                step="0.01"
                                min="0"
                                max="1"
                                placeholder="Uses rider risk score if empty"
                                value={behaviorScore}
                                onChange={(e) => setBehaviorScore(e.target.value)}
                            />
                        </div>
                        <button className="btn btn-primary w-full" type="submit" disabled={submitting}>
                            {submitting ? 'Processing...' : '📋 Submit Claim'}
                        </button>
                    </form>
                </div>

                {/* Search Claims */}
                <div className="card">
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Search Claims by Rider</h3>
                    <div className="form-group">
                        <label className="form-label">Rider ID</label>
                        <div className="flex gap-2">
                            <input
                                className="form-input"
                                type="number"
                                placeholder="Enter rider ID"
                                value={searchRiderId}
                                onChange={(e) => setSearchRiderId(e.target.value)}
                            />
                            <button className="btn btn-secondary" onClick={handleSearch}>
                                🔍
                            </button>
                        </div>
                    </div>

                    {loading ? (
                        <Loading text="Searching..." />
                    ) : claims.length > 0 ? (
                        <div className="mt-4">
                            {claims.map((c) => (
                                <div key={c.id} className="card" style={{ padding: 16, marginBottom: 12, background: 'var(--bg-secondary)' }}>
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="font-mono text-xs">{c.claim_number}</span>
                                        <span className={`badge ${['approve', 'approved', 'paid'].includes(c.status) ? 'badge-success' :
                                                c.status === 'review' ? 'badge-review' : 'badge-danger'
                                            }`}>
                                            {c.status}
                                        </span>
                                    </div>
                                    <div className="text-xs text-muted">
                                        Score: {c.final_score?.toFixed(3)} | Decision: {c.decision} | Payout: ₹{c.payout_amount?.toFixed(2)}
                                    </div>
                                    {c.reason && (
                                        <div className="text-xs mt-2" style={{ color: 'var(--text-secondary)' }}>
                                            {c.reason}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    ) : searchRiderId ? (
                        <div className="empty-state" style={{ padding: 20 }}>No claims found</div>
                    ) : null}
                </div>
            </div>
        </div>
    );
}
