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
        <div className="container admin-dashboard">
            <div className="page-header">
                <h1 className="page-title">Transaction Reports</h1>
                <p className="auth-subtitle">History of all verified item handovers and resolutions</p>
            </div>

            <div className="admin-section-title">
                <span>Completed Transactions</span>
                <Button variant="secondary" size="sm" onClick={fetchReports}>Refresh</Button>
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
                <div className="claims-container">
                    {reports.map((report) => (
                        <Card key={report.claim_id} className="admin-claim-card" hover={false}>
                            <div className="claim-card-header">
                                <span className="claim-id">TRANSACTION #{report.claim_id}</span>
                                <span className="admin-status-badge completed">Completed</span>
                            </div>
                            
                            <div className="claim-card-body">
                                <div className="claim-main-info">
                                    <p className="claim-info-row">Item: <span>{report.item_name}</span></p>
                                    <p className="claim-info-row">Claimant: <span>{report.claimant_email}</span></p>
                                    <p className="claim-info-row">Admin: <span>{report.admin_username}</span></p>
                                    <p className="claim-info-row">Date: <span>{new Date(report.transaction_timestamp).toLocaleString()}</span></p>
                                </div>
                                
                                <div className="claim-proof-section">
                                    <p className="proof-label">Verification Details</p>
                                    <p className="proof-text">{report.verification_details}</p>
                                </div>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminReports;

