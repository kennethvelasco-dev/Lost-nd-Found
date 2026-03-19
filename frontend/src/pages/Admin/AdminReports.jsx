import React, { useState, useEffect, useCallback } from 'react';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';

const AdminReports = () => {
    const { loading, error, data, request } = useHttp();
    const [verifying, setVerifying] = useState(null);
    const [rejectionReason, setRejectionReason] = useState('');

    const fetchPending = useCallback(() => {
        request({ url: '/items/pending' });
    }, [request]);

    useEffect(() => {
        fetchPending();
    }, [fetchPending]);

    const pendingReports = data?.pending || [];

    const handleVerify = async (reportId, type, decision) => {
        if (decision === 'rejected' && !rejectionReason) {
            alert('Please provide a reason for rejection.');
            return;
        }

        setVerifying(reportId);
        try {
            await api.post(`/items/reports/${reportId}/verify`, {
                type,
                decision,
                reason: rejectionReason
            });
            setRejectionReason('');
            fetchPending();
        } catch (err) {
            console.error('Verification failed', err);
        } finally {
            setVerifying(null);
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Report Oversight</h1>
                    <p className="auth-subtitle">Validate and approve user reports for the public directory.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState 
                    loading={loading} 
                    error={error} 
                    isEmpty={pendingReports.length === 0} 
                    emptyMessage="All reports have been reviewed. No pending tasks."
                    onRetry={fetchPending}
                >
                    <div className="reports-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                        {pendingReports.map(report => (
                            <Card key={`${report.type}-${report.id}`} style={{ padding: 'var(--space-4)' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr 300px', gap: 'var(--space-4)' }}>
                                    {/* Image Section */}
                                    <div className="report-image-box">
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
                                            {report.main_picture ? (
                                                <img src={report.main_picture} alt="Primary" style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-flat-sm)' }} />
                                            ) : (
                                                <div style={{ width: '100%', aspectRatio: '1', backgroundColor: 'var(--background)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', border: '1px dashed var(--text-muted)' }}>
                                                    No Primary Image
                                                </div>
                                            )}
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                                {report.additional_picture_1 && <img src={report.additional_picture_1} alt="Alt 1" style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', borderRadius: 'var(--radius-sm)' }} />}
                                                {report.additional_picture_2 && <img src={report.additional_picture_2} alt="Alt 2" style={{ width: '100%', aspectRatio: '1', objectFit: 'cover', borderRadius: 'var(--radius-sm)' }} />}
                                            </div>
                                        </div>
                                    </div>

                                    {/* Info Section */}
                                    <div className="report-info-box">
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px', marginBottom: '10px' }}>
                                            <span style={{ fontSize: '10px', fontWeight: 800, padding: '4px 8px', borderRadius: '12px', backgroundColor: report.type === 'lost' ? '#fee2e2' : '#dcfce7', color: report.type === 'lost' ? '#ef4444' : '#22c55e', textTransform: 'uppercase' }}>
                                                {report.type}
                                            </span>
                                            <h2 style={{ margin: 0, fontSize: '1.4rem' }}>{report.item_type}</h2>
                                        </div>
                                        <p style={{ margin: '4px 0', fontWeight: 600 }}>{report.category} • {report.color}</p>
                                        <p style={{ margin: '4px 0', fontSize: '14px', color: 'var(--text-muted)' }}>Location: {report.last_seen_location || report.found_location}</p>
                                        <div style={{ marginTop: '12px', padding: '12px', borderRadius: 'var(--radius-sm)', backgroundColor: 'var(--background)', boxShadow: 'var(--nm-inset-sm)' }}>
                                            <p style={{ margin: 0, fontSize: '14px' }}>{report.public_description}</p>
                                        </div>
                                    </div>

                                    {/* Action Section */}
                                    <div className="report-action-box" style={{ display: 'flex', flexDirection: 'column', gap: '15px', justifyContent: 'center' }}>
                                        <textarea 
                                            className="form-textarea" 
                                            placeholder="Reason if rejecting..." 
                                            value={rejectionReason}
                                            onChange={(e) => setRejectionReason(e.target.value)}
                                            style={{ minHeight: '80px', fontSize: '13px' }}
                                        ></textarea>
                                        <div style={{ display: 'flex', gap: '10px' }}>
                                            <Button 
                                                variant="success" 
                                                onClick={() => handleVerify(report.id, report.type, 'approved')}
                                                disabled={verifying === report.id}
                                                style={{ flex: 1 }}
                                            >
                                                Approve
                                            </Button>
                                            <Button 
                                                variant="danger" 
                                                onClick={() => handleVerify(report.id, report.type, 'rejected')}
                                                disabled={verifying === report.id}
                                                style={{ flex: 1 }}
                                            >
                                                Reject
                                            </Button>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default AdminReports;
