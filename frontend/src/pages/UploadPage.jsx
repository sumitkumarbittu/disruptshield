/**
 * Upload Riders Page — CSV file upload for bulk rider creation.
 */

import { useState, useRef } from 'react';
import { uploadRidersCSV } from '../api/client';

export default function UploadPage() {
    const [file, setFile] = useState(null);
    const [uploading, setUploading] = useState(false);
    const [result, setResult] = useState(null);
    const [error, setError] = useState(null);
    const [dragging, setDragging] = useState(false);
    const fileInputRef = useRef(null);

    const handleDrop = (e) => {
        e.preventDefault();
        setDragging(false);
        const droppedFile = e.dataTransfer.files[0];
        if (droppedFile && droppedFile.name.endsWith('.csv')) {
            setFile(droppedFile);
            setError(null);
        } else {
            setError('Please drop a CSV file');
        }
    };

    const handleFileSelect = (e) => {
        const selectedFile = e.target.files[0];
        if (selectedFile) {
            setFile(selectedFile);
            setError(null);
        }
    };

    const handleUpload = async () => {
        if (!file) return;

        try {
            setUploading(true);
            setError(null);
            setResult(null);
            const res = await uploadRidersCSV(file);
            setResult(res.data);
            setFile(null);
        } catch (err) {
            setError(err.response?.data?.detail || err.message);
        } finally {
            setUploading(false);
        }
    };

    return (
        <div>
            <div className="page-header">
                <h2>Upload Riders</h2>
                <p>Bulk import riders via CSV file to create riders and policies</p>
            </div>

            {error && <div className="error-banner">⚠️ {error}</div>}
            {result && (
                <div className="success-banner">
                    ✅ Upload complete! Created {result.riders_created} riders and {result.policies_created} policies.
                    {result.errors.length > 0 && (
                        <div className="mt-2 text-xs" style={{ opacity: 0.8 }}>
                            {result.errors.length} warning(s): {result.errors.slice(0, 3).join('; ')}
                            {result.errors.length > 3 && ` and ${result.errors.length - 3} more...`}
                        </div>
                    )}
                </div>
            )}

            <div
                className={`upload-zone ${dragging ? 'dragging' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDrop={handleDrop}
                onDragOver={(e) => { e.preventDefault(); setDragging(true); }}
                onDragLeave={() => setDragging(false)}
            >
                <span className="upload-icon">{file ? '📄' : '☁️'}</span>
                {file ? (
                    <>
                        <div className="upload-text">{file.name}</div>
                        <div className="upload-hint">
                            {(file.size / 1024).toFixed(1)} KB — Click or drop another file to replace
                        </div>
                    </>
                ) : (
                    <>
                        <div className="upload-text">Drop your CSV file here, or click to browse</div>
                        <div className="upload-hint">
                            Required columns: rider_id, name, phone, email, platform, city, pin_code, avg_weekly_income
                        </div>
                    </>
                )}
                <input
                    ref={fileInputRef}
                    type="file"
                    accept=".csv"
                    onChange={handleFileSelect}
                    style={{ display: 'none' }}
                />
            </div>

            <div className="mt-6 flex gap-3">
                <button
                    className="btn btn-primary"
                    onClick={handleUpload}
                    disabled={!file || uploading}
                >
                    {uploading ? (
                        <>
                            <div className="spinner" style={{ width: 16, height: 16, borderWidth: 2 }} />
                            Uploading...
                        </>
                    ) : (
                        <>📤 Upload & Create Riders</>
                    )}
                </button>
                {file && (
                    <button
                        className="btn btn-secondary"
                        onClick={() => { setFile(null); setResult(null); }}
                    >
                        Clear
                    </button>
                )}
            </div>

            <div className="card mt-6" style={{ maxWidth: 640 }}>
                <h3 style={{ fontSize: '0.95rem', fontWeight: 600, marginBottom: 12 }}>CSV Format</h3>
                <div className="font-mono text-xs" style={{ color: 'var(--text-muted)', lineHeight: 1.8 }}>
                    rider_id,name,phone,email,platform,city,pin_code,avg_weekly_income<br />
                    ZOM-4923,Amit Kumar,9876543210,amit@email.com,zomato,Mumbai,400001,2400<br />
                    SWG-1029,Priya Singh,9876543211,priya@email.com,swiggy,Chennai,600001,1800
                </div>
            </div>
        </div>
    );
}
