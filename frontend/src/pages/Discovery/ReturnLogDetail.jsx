import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import StatusState from '../../components/UI/StatusState';

const ReturnLogDetail = () => {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const res = await api.get(`/items/released/${id}`);
                setData(res.data?.data || res.data);
            } catch (err) {
                setError(err.response?.data?.message || 'Failed to load return log.');
            } finally {
                setLoading(false);
            }
        };
        fetchDetail();
    }, [id]);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Return Log Detail</h1>
                    <p className="auth-subtitle">See how this item was matched and returned.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={!data}
                    emptyMessage="Return log not found."
                    onRetry={null}
                >
                    {data && (
                        <Card style={{ padding: 'var(--space-4)' }}>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                                {/* Header */}
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <h2 style={{ margin: 0 }}>
                                            {data.item_type}{' '}
                                            <span style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                                ({data.category || 'Uncategorized'})
                                            </span>
                                        </h2>
                                        <p style={{ margin: '4px 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                            Original Report ID:&nbsp;
                                            <strong>{data.original_report_id}</strong>
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right', fontSize: '0.8rem', color: 'var(--text-secondary)' }}>
                                        <div style={{ fontWeight: 600, color: 'var(--success)' }}>Verified Return</div>
                                        <div>
                                            {data.resolved_at
                                                ? new Date(data.resolved_at).toLocaleString()
                                                : 'Return date not recorded'}
                                        </div>
                                    </div>
                                </div>

                                {/* Two-column layout */}
                                <div style={{ display: 'grid', gridTemplateColumns: 'minmax(260px, 1.2fr) 1fr', gap: 'var(--space-4)' }}>
                                    {/* Images column */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                                        <div>
                                            <h3 style={{ marginBottom: '8px', fontSize: '0.95rem' }}>Original Report Photo</h3>
                                            {data.main_picture ? (
                                                <img
                                                    src={data.main_picture}
                                                    alt="Original report"
                                                    loading="lazy"
                                                    style={{
                                                        width: '100%',
                                                        maxHeight: '260px',
                                                        objectFit: 'cover',
                                                        borderRadius: 'var(--radius-md)',
                                                        border: '1px solid rgba(0,0,0,0.1)'
                                                    }}
                                                />
                                            ) : (
                                                <div style={{
                                                    width: '100%',
                                                    height: '130px',
                                                    borderRadius: 'var(--radius-md)',
                                                    border: '1px dashed rgba(0,0,0,0.2)',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '0.8rem',
                                                    color: 'var(--text-secondary)'
                                                }}>
                                                    No original photo on file
                                                </div>
                                            )}
                                        </div>

                                        <div>
                                            <h3 style={{ marginBottom: '8px', fontSize: '0.95rem' }}>Handover Proof Photo</h3>
                                            {data.turnover_proof ? (
                                                <img
                                                    src={data.turnover_proof}
                                                    alt="Handover proof"
                                                    loading="lazy"
                                                    style={{
                                                        width: '100%',
                                                        maxHeight: '260px',
                                                        objectFit: 'cover',
                                                        borderRadius: 'var(--radius-md)',
                                                        border: '1px solid rgba(0,0,0,0.1)'
                                                    }}
                                                />
                                            ) : (
                                                <div style={{
                                                    width: '100%',
                                                    height: '130px',
                                                    borderRadius: 'var(--radius-md)',
                                                    border: '1px dashed rgba(0,0,0,0.2)',
                                                    display: 'flex',
                                                    alignItems: 'center',
                                                    justifyContent: 'center',
                                                    fontSize: '0.8rem',
                                                    color: 'var(--text-secondary)'
                                                }}>
                                                    No turnover proof uploaded
                                                </div>
                                            )}
                                        </div>
                                    </div>

                                    {/* Details column */}
                                    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)', fontSize: '0.9rem' }}>
                                        <div style={{ borderBottom: '1px solid rgba(0,0,0,0.05)', paddingBottom: '8px' }}>
                                            <h3 style={{ margin: 0, fontSize: '0.95rem' }}>Return Summary</h3>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Returned to (Claimant):</span>
                                            <strong>{data.claimant_name || 'Unknown claimant'}</strong>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Student / Recipient ID:</span>
                                            <span>{data.recipient_id || 'Not recorded'}</span>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Processed by (Admin username):</span>
                                            <span>{data.released_by_admin || 'Unknown admin'}</span>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Admin Office ID:</span>
                                            <span>{data.admin_office_id || 'Not recorded'}</span>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Item origin:</span>
                                            <span>{data.item_source === 'lost' ? 'Lost report' : 'Found report'}</span>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Reported location:</span>
                                            <span>{data.last_seen_location || data.found_location || 'Not specified'}</span>
                                        </div>

                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Color / Brand:</span>
                                            <span>{data.color || 'N/A'} • {data.brand || 'N/A'}</span>
                                        </div>

                                        <div style={{ marginTop: 'var(--space-2)' }}>
                                            <h4 style={{ marginBottom: '6px', fontSize: '0.9rem' }}>Public Description</h4>
                                            <p style={{ margin: 0, color: 'var(--text-secondary)' }}>
                                                {data.public_description || 'No public description was added to this report.'}
                                            </p>
                                        </div>

                                        <div style={{ marginTop: 'var(--space-2)' }}>
                                            <h4 style={{ marginBottom: '6px', fontSize: '0.9rem' }}>Handover Notes (Admin Narrative)</h4>
                                            <p style={{ margin: 0, whiteSpace: 'pre-wrap' }}>
                                                {data.handover_notes || 'No additional handover notes were recorded for this return.'}
                                            </p>
                                        </div>
                                    </div>
                                </div>
                            </div>
                        </Card>
                    )}
                </StatusState>
            </div>
        </div>
    );
};

export default ReturnLogDetail;
