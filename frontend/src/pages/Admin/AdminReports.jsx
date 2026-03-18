import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import './AdminDashboard.css';

const AdminReports = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const fetchReports = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/reports/transactions');
            setReports(response.data.data.transactions || response.data.data || []);
            setError(null);
        } catch (err) {
            if (err.response?.status === 403 || err.response?.status === 401) {
                navigate('/login');
            } else {
                setError('Failed to fetch transaction reports.');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
    }, [navigate]);

    return (
        <div className="page-container">
            <div className="container admin-reports">
                <div className="page-header">
                    <h1 className="page-title">Transaction Reports</h1>
                    <div className="admin-section-header" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: 'var(--space-3)' }}>
                        <p className="auth-subtitle" style={{ margin: 0 }}>History of all verified item handovers and resolutions</p>
                        <Button variant="secondary" size="sm" onClick={fetchReports}>Refresh</Button>
                    </div>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: 'var(--space-4) 0' }}>
                        <p>Loading transaction history...</p>
                    </div>
                ) : error ? (
                    <Card style={{ textAlign: 'center', color: 'var(--danger)' }}>{error}</Card>
                ) : reports.length === 0 ? (
                    <Card style={{ textAlign: 'center', padding: 'var(--space-4) 0' }}>
                        <p className="no-items">No completed transactions found in the system yet.</p>
                    </Card>
                ) : (
                    <div className="reports-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                        {reports.map((report) => (
                            <Card key={report.claim_id} className="admin-claim-card" hover={false} style={{ padding: 'var(--space-3)' }}>
                                <div className="claim-card-header" style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-2)' }}>
                                    <span className="claim-id" style={{ fontWeight: 700, color: 'var(--primary)' }}>TRANSACTION #{report.claim_id}</span>
                                    <span className="admin-status-badge completed" style={{ backgroundColor: '#dcfce7', color: '#166534', padding: '4px 8px', borderRadius: '4px', fontSize: '12px' }}>Completed</span>
                                </div>
                                
                                <div className="claim-card-body">
                                    <div className="claim-main-info" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)', marginBottom: 'var(--space-2)' }}>
                                        <p className="claim-info-row"><strong>Item:</strong> {report.item_name}</p>
                                        <p className="claim-info-row"><strong>Claimant:</strong> {report.claimant_email}</p>
                                        <p className="claim-info-row"><strong>Admin:</strong> {report.admin_username}</p>
                                        <p className="claim-info-row"><strong>Date:</strong> {new Date(report.transaction_timestamp).toLocaleString()}</p>
                                    </div>
                                    
                                    <div className="claim-proof-section" style={{ borderTop: '1px solid #e5e7eb', paddingTop: 'var(--space-2)' }}>
                                        <p className="proof-label" style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: '4px' }}>Verification Details</p>
                                        <p className="proof-text">{report.verification_details}</p>
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
