import React, { useState, useEffect } from 'react';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import api from '../../services/api';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const [stats, setStats] = useState({
        pending: 0,
        approved: 0,
        total: 0
    });
    const [pendingClaims, setPendingClaims] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchData = async () => {
        try {
            setLoading(true);
            const [statsRes, claimsRes] = await Promise.all([
                api.get('/admin/stats'),
                api.get('/admin/claims?status=pending')
            ]);
            setStats(statsRes.data.data);
            setPendingClaims(claimsRes.data.data.claims || []);
        } catch (err) {
            console.error('Failed to fetch admin data', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, []);

    const handleAction = async (claimId, action) => {
        try {
            await api.post(`/admin/claims/${claimId}/verify`, { decision: action });
            fetchData(); // Refresh
        } catch (err) {
            alert('Action failed: ' + (err.response?.data?.message || 'Unknown error'));
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Admin Console</h1>
                    <p className="auth-subtitle">Real-time statistics and system management</p>
                    <div className="title-underline"></div>
                </div>

                <div className="stats-grid">
                    <Card className="stats-card">
                        <div className="stats-value">{stats.pending}</div>
                        <div className="stats-label">Pending Claims</div>
                    </Card>
                    <Card className="stats-card">
                        <div className="stats-value">{stats.approved}</div>
                        <div className="stats-label">Approved Today</div>
                    </Card>
                    <Card className="stats-card">
                        <div className="stats-value">{stats.total}</div>
                        <div className="stats-label">Total Items</div>
                    </Card>
                </div>

                <h2 className="section-title">Pending Verifications</h2>
                {loading ? (
                    <p>Loading claims...</p>
                ) : (
                    <div className="claims-review-list">
                        {pendingClaims.map(claim => (
                            <Card key={claim.id} className="claim-review-card">
                                <div className="claim-item-info">
                                    <h3>{claim.item_name}</h3>
                                    <p className="claim-meta">Claimed by: {claim.claimant_email}</p>
                                    <p className="claim-score">Match Score: <strong>{claim.verification_score}%</strong></p>
                                </div>
                                <div className="claim-actions">
                                    <Button 
                                        variant="primary" 
                                        size="sm" 
                                        onClick={() => handleAction(claim.id, 'approved')}
                                    >
                                        Approve
                                    </Button>
                                    <Button 
                                        variant="danger" 
                                        size="sm"
                                        onClick={() => handleAction(claim.id, 'rejected')}
                                    >
                                        Reject
                                    </Button>
                                    <Button variant="neutral" size="sm">Details</Button>
                                </div>
                            </Card>
                        ))}
                        {pendingClaims.length === 0 && (
                            <div className="empty-state">
                                <p>No pending claims to review at this time.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminDashboard;
