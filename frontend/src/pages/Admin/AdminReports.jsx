import React, { useState, useEffect } from 'react';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const AdminReports = () => {
    const [pendingReports, setPendingReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [verifying, setVerifying] = useState(null);
    const [rejectionReason, setRejectionReason] = useState('');

    const fetchPending = async () => {
        try {
            const response = await api.get('/items/pending');
            setPendingReports(response.data.data.pending);
        } catch (err) {
            console.error('Failed to fetch pending reports', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchPending();
    }, []);

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

    if (loading) return <div className="page-container"><p>Fetching pending reports...</p></div>;

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Report Approval</h1>
                    <p className="auth-subtitle">Review and validate user-submitted reports before publishing.</p>
                    <div className="title-underline"></div>
                </div>

                {pendingReports.length === 0 ? (
                    <Card style={{ textAlign: 'center', padding: '60px' }}>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>All clear! No pending reports at the moment.</p>
                    </Card>
                ) : (
                    <div className="reports-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                        {pendingReports.map(report => (
                            <Card key={`${report.type}-${report.id}`} style={{ padding: 'var(--space-4)' }}>
                                <div style={{ display: 'grid', gridTemplateColumns: '250px 1fr 300px', gap: 'var(--space-4)' }}>
                                    {/* Image Section */}
                                    <div className="report-image-box">
                                        <div style={{ display: 'grid', gridTemplateColumns: '1fr', gap: '8px' }}>
                                            {report.main_picture ? (
                                                <img src={report.main_picture} alt="Primary" style={{ width: '100%', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-flat-sm)' }} />
                                            ) : (
                                                <div style={{ width: '100%', aspectRatio: '1', backgroundColor: 'var(--background)', borderRadius: 'var(--radius-sm)', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-muted)', border: '1px dashed var(--text-muted)' }}>
                                                    No Image
                                                </div>
                                            )}
                                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
                                                {report.additional_picture_1 && (
                                                    <img src={report.additional_picture_1} alt="Add. 1" style={{ width: '100%', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-flat-sm)' }} />
                                                )}
                                                {report.additional_picture_2 && (
                                                    <img src={report.additional_picture_2} alt="Add. 2" style={{ width: '100%', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-flat-sm)' }} />
                                                )}
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
                                            placeholder="Reason for rejection (if applicable)..." 
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
                )}
            </div>
        </div>
    );
};

export default AdminReports;
