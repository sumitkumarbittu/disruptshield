/**
 * Payouts Page — process and view payouts.
 */

import { useState } from 'react';
import { processPayout } from '../api/client';

export default function PayoutsPage() {
    const [claimId, setClaimId] = useState('');
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [processing, setProcessing] = useState(false);
    const [history, setHistory] = useState([]);

    const handleProcess = async (e) => {
        e.preventDefault();
        if (!claimId) {
            setError('Claim ID is required');
            return;
        }

        try {
            setProcessing(true);
            setError(null);
            setResult(null);
            const res = await processPayout(parseInt(claimId));
            setResult(res.data);
            setHistory((prev) => [res.data, ...prev]);
            setClaimId('');
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setProcessing(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>Payouts</h2>
                <p>Process payouts for approved claims — triggers post-payout engine</p>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}
            {result && (
                <div className="success-banner">
                    ✅ Payout processed! ₹{result.amount.toFixed(2)} credited via {result.payment_method}.
                    Transaction: <span className="font-mono">{result.transaction_ref}</span>
                </div>
            )}

            <div className="profile-grid mb-6">
                <div className="card">
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Process Payout</h3>
                    <form onSubmit={handleProcess}>
                        <div className="form-group">
                            <label className="form-label">Claim ID</label>
                            <input
                                className="form-input"
                                type="number"
                                placeholder="Enter approved claim ID"
                                value={claimId}
                                onChange={(e) => setClaimId(e.target.value)}
                                required
                            />
                        </div>
                        <button className="btn btn-primary w-full" type="submit" disabled={processing}>
                            {processing ? 'Processing...' : '💰 Process Payout'}
                        </button>
                    </form>

                    <div className="mt-4" style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>
                        <strong>Note:</strong> Processing a payout triggers the post-payout event-aware engine which:
                        <ul style={{ marginTop: 8, paddingLeft: 16, lineHeight: 2 }}>
                            <li>Updates rider risk score</li>
                            <li>Updates zone risk</li>
                            <li>Recalculates premium</li>
                            <li>Logs event impact in post_event_updates</li>
                        </ul>
                    </div>
                </div>

                <div className="card">
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Recent Payouts (Session)</h3>
                    {history.length === 0 ? (
                        <div className="empty-state" style={{ padding: 20 }}>
                            <div className="empty-state-icon">💰</div>
                            <p className="text-xs text-muted">No payouts processed in this session</p>
                        </div>
                    ) : (
                        <div>
                            {history.map((p, i) => (
                                <div key={i} className="card" style={{ padding: 16, marginBottom: 12, background: 'var(--bg-secondary)' }}>
                                    <div className="flex items-center justify-between mb-4">
                                        <span className="font-mono" style={{ fontWeight: 600, color: 'var(--status-success)' }}>
                                            ₹{p.amount.toFixed(2)}
                                        </span>
                                        <span className="badge badge-success">{p.status}</span>
                                    </div>
                                    <div className="text-xs text-muted">
                                        Claim #{p.claim_id} | Rider #{p.rider_id} | TXN: <span className="font-mono">{p.transaction_ref}</span>
                                    </div>
                                    <div className="text-xs text-muted mt-2">
                                        {p.processed_at ? new Date(p.processed_at).toLocaleString() : '—'}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
