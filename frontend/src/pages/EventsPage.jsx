/**
 * Events Page — create and view disruption events.
 */

import { useState, useEffect } from 'react';
import { createEvent, getEvents } from '../api/client';
import Loading from '../components/Loading';

export default function EventsPage() {
    const [events, setEvents] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [success, setSuccess] = useState(null);
    const [showForm, setShowForm] = useState(false);

    // Form state
    const [form, setForm] = useState({
        event_type: 'heavy_rain',
        zone: '',
        pin_code: '',
        city: '',
        disruption_score: '0.65',
        description: '',
        duration_hours: '4',
    });

    useEffect(() => {
        fetchEvents();
    }, []);

    const fetchEvents = async () => {
        try {
            setLoading(true);
            const res = await getEvents();
            setEvents(res.data);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setLoading(false);
        }
    };

    const handleCreate = async (e) => {
        e.preventDefault();
        try {
            setError(null);
            setSuccess(null);
            const data = {
                event_type: form.event_type,
                zone: form.zone,
                pin_code: form.pin_code || form.zone,
                city: form.city,
                disruption_score: parseFloat(form.disruption_score),
                description: form.description,
                duration_hours: parseFloat(form.duration_hours) || 4.0,
            };
            const res = await createEvent(data);
            setSuccess(`Event #${res.data.id} created — ${res.data.event_type} (${res.data.severity}) in zone ${res.data.zone}`);
            setShowForm(false);
            fetchEvents();
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        }
    };

    const severityColor = (severity) => {
        switch (severity) {
            case 'extreme': return 'badge-danger';
            case 'high': return 'badge-warning';
            case 'moderate': return 'badge-info';
            default: return 'badge-info';
        }
    };

    const typeIcon = (type) => {
        switch (type) {
            case 'heavy_rain': return '🌧️';
            case 'flood': return '🌊';
            case 'aqi_spike': return '💨';
            case 'curfew': return '🚫';
            default: return '⚡';
        }
    };

    return (
        <div>
            <div className="page-header flex items-center justify-between">
                <div>
                    <h2>Disruption Events</h2>
                    <p>Monitor and create disruption events</p>
                </div>
                <button className="btn btn-primary" onClick={() => setShowForm(!showForm)}>
                    {showForm ? '✕ Cancel' : '⚡ Create Event'}
                </button>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}
            {success && <div className="success-banner">✅ {success}</div>}

            {/* Create Event Form */}
            {showForm && (
                <div className="card mb-6" style={{ maxWidth: 640 }}>
                    <h3 style={{ fontSize: '1rem', fontWeight: 600, marginBottom: 20 }}>Create Disruption Event</h3>
                    <form onSubmit={handleCreate}>
                        <div className="profile-grid" style={{ gridTemplateColumns: '1fr 1fr' }}>
                            <div className="form-group">
                                <label className="form-label">Event Type</label>
                                <select
                                    className="form-input"
                                    value={form.event_type}
                                    onChange={(e) => setForm({ ...form, event_type: e.target.value })}
                                >
                                    <option value="heavy_rain">🌧️ Heavy Rain</option>
                                    <option value="flood">🌊 Flood</option>
                                    <option value="aqi_spike">💨 AQI Spike</option>
                                    <option value="curfew">🚫 Curfew / Strike</option>
                                </select>
                            </div>
                            <div className="form-group">
                                <label className="form-label">Disruption Score (0-1)</label>
                                <input
                                    className="form-input"
                                    type="number"
                                    step="0.01"
                                    min="0"
                                    max="1"
                                    value={form.disruption_score}
                                    onChange={(e) => setForm({ ...form, disruption_score: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Zone</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g., 400001"
                                    value={form.zone}
                                    onChange={(e) => setForm({ ...form, zone: e.target.value })}
                                    required
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">City</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g., Mumbai"
                                    value={form.city}
                                    onChange={(e) => setForm({ ...form, city: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Pin Code</label>
                                <input
                                    className="form-input"
                                    placeholder="e.g., 400001"
                                    value={form.pin_code}
                                    onChange={(e) => setForm({ ...form, pin_code: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label className="form-label">Duration (hours)</label>
                                <input
                                    className="form-input"
                                    type="number"
                                    step="0.5"
                                    min="0.5"
                                    value={form.duration_hours}
                                    onChange={(e) => setForm({ ...form, duration_hours: e.target.value })}
                                />
                            </div>
                        </div>
                        <div className="form-group">
                            <label className="form-label">Description</label>
                            <input
                                className="form-input"
                                placeholder="Brief description of the disruption"
                                value={form.description}
                                onChange={(e) => setForm({ ...form, description: e.target.value })}
                            />
                        </div>
                        <button className="btn btn-primary" type="submit">⚡ Create Event</button>
                    </form>
                </div>
            )}

            {/* Events List */}
            {loading ? (
                <Loading text="Loading events..." />
            ) : events.length === 0 ? (
                <div className="empty-state">
                    <div className="empty-state-icon">⚡</div>
                    <p>No disruption events recorded yet</p>
                </div>
            ) : (
                <div className="table-container">
                    <table>
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Type</th>
                                <th>Severity</th>
                                <th>Zone</th>
                                <th>City</th>
                                <th>Score</th>
                                <th>Duration</th>
                                <th>Multiplier</th>
                                <th>Status</th>
                                <th>Created</th>
                            </tr>
                        </thead>
                        <tbody>
                            {events.map((ev) => (
                                <tr key={ev.id}>
                                    <td className="font-mono text-xs">{ev.id}</td>
                                    <td>
                                        <span style={{ marginRight: 6 }}>{typeIcon(ev.event_type)}</span>
                                        {ev.event_type.replace('_', ' ')}
                                    </td>
                                    <td><span className={`badge ${severityColor(ev.severity)}`}>{ev.severity}</span></td>
                                    <td className="font-mono">{ev.zone}</td>
                                    <td>{ev.city || '—'}</td>
                                    <td className="font-mono" style={{ fontWeight: 600 }}>{ev.disruption_score.toFixed(2)}</td>
                                    <td>{ev.duration_hours ? `${ev.duration_hours}h` : '—'}</td>
                                    <td className="font-mono">{ev.severity_multiplier.toFixed(2)}</td>
                                    <td>
                                        <span className={`badge ${ev.is_active ? 'badge-success' : 'badge-danger'}`}>
                                            {ev.is_active ? 'Active' : 'Ended'}
                                        </span>
                                    </td>
                                    <td className="text-xs">{ev.created_at ? new Date(ev.created_at).toLocaleDateString() : '—'}</td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            )}
        </div>
    );
}
