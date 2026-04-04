/**
 * Riders List Page — view all registered riders.
 */

import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { getRiders } from '../api/client';
import Loading from '../components/Loading';

export default function RidersPage() {
    const [riders, setRiders] = useState([]);
    const [total, setTotal] = useState(0);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [page, setPage] = useState(0);
    const limit = 50;

    useEffect(() => {
        fetchRiders();
    }, [page]);

    const fetchRiders = async () => {
        try {
            setLoading(true);
            const res = await getRiders(page * limit, limit);
            setRiders(res.data.riders);
            setTotal(res.data.total);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    if (loading) return <Loading text="Loading riders..." />;

    return (
        <div>
            <div className="page-header">
                <h2>Riders</h2>
                <p>{total} registered delivery partners</p>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}

            {riders.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">🏍️</div>
                    <p>No riders registered yet.</p>
                    <Link to="/upload" className="btn btn-primary mt-4">Upload Riders CSV</Link>
                </div>
            ) : (
                <>
                    <div className="table-container">
                        <table>
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Rider ID</th>
                                    <th>Name</th>
                                    <th>Platform</th>
                                    <th>City</th>
                                    <th>Pin Code</th>
                                    <th>Weekly Income</th>
                                    <th>Risk Score</th>
                                    <th>Status</th>
                                    <th>Action</th>
                                </tr>
                            </thead>
                            <tbody>
                                {riders.map((rider) => (
                                    <tr key={rider.id}>
                                        <td className="font-mono text-xs">{rider.id}</td>
                                        <td className="font-mono text-xs">{rider.rider_external_id}</td>
                                        <td style={{ fontWeight: 500, color: 'var(--text-primary)' }}>{rider.name}</td>
                                        <td>
                                            <span className="badge badge-info">
                                                {rider.platform}
                                            </span>
                                        </td>
                                        <td>{rider.city}</td>
                                        <td className="font-mono text-xs">{rider.pin_code}</td>
                                        <td className="font-mono">₹{rider.avg_weekly_income.toLocaleString()}</td>
                                        <td>
                                            <span className={`badge ${rider.risk_score >= 0.5 ? 'badge-danger' : rider.risk_score >= 0.25 ? 'badge-warning' : 'badge-success'}`}>
                                                {rider.risk_score.toFixed(3)}
                                            </span>
                                        </td>
                                        <td>
                                            <span className={`badge ${rider.is_active ? 'badge-success' : 'badge-danger'}`}>
                                                {rider.is_active ? 'Active' : 'Inactive'}
                                            </span>
                                        </td>
                                        <td>
                                            <Link to={`/riders/${rider.id}`} className="btn btn-sm btn-secondary">
                                                View
                                            </Link>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>

                    <div className="flex items-center justify-between mt-4">
                        <span className="text-sm text-muted">
                            Showing {page * limit + 1}–{Math.min((page + 1) * limit, total)} of {total}
                        </span>
                        <div className="flex gap-2">
                            <button
                                className="btn btn-sm btn-secondary"
                                onClick={() => setPage(Math.max(0, page - 1))}
                                disabled={page === 0}
                            >
                                ← Previous
                            </button>
                            <button
                                className="btn btn-sm btn-secondary"
                                onClick={() => setPage(page + 1)}
                                disabled={(page + 1) * limit >= total}
                            >
                                Next →
                            </button>
                        </div>
                    </div>
                </>
            )}
        </div>
    );
}
