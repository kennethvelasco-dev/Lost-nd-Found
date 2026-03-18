import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import './AdminDashboard.css';

const AdminDashboard = () => {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const fetchClaims = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/claims');
            setClaims(response.data.data.claims || response.data.data || []);
            setError(null);
        } catch (err) {
            if (err.response?.status === 403 || err.response?.status === 401) {
                navigate('/login');
            } else {
                setError('Failed to fetch pending claims.');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClaims();
    }, [navigate]);

    const verifyClaim = async (claimId, decision, notes = '') => {
        try {
            await api.post(`/admin/claims/${claimId}/verify`, { decision, handover_notes: notes });
            alert(`Claim ${decision} successfully`);
            fetchClaims();
        } catch (err) {
            alert(`Error verifying claim: ${err.response?.data?.message || err.message}`);
        }
    };

    const stats = {
        pending: claims.filter(c => c.status === 'pending').length,
        approved: claims.filter(c => c.status === 'approved').length,
        total: claims.length
    };

    return (
        <div className="container admin-dashboard">
            <div className="page-header">
                <h1 className="page-title">Admin Dashboard</h1>
                <p className="auth-subtitle">Manage claim requests and item verifications</p>
            </div>

            <div className="stats-grid">
                <Card className="stat-card">
                    <span className="stat-value">{stats.pending}</span>
                    <span className="stat-label">Pending</span>
                </Card>
                <Card className="stat-card">
                    <span className="stat-value">{stats.approved}</span>
                    <span className="stat-label">Approved</span>
                </Card>
                <Card className="stat-card">
                    <span className="stat-value">{stats.total}</span>
                    <span className="stat-label">Total Claims</span>
                </Card>
            </div>

            <div className="admin-section-title">
                <span>Pending Verifications</span>
                <Button variant="secondary" size="sm" onClick={fetchClaims}>Refresh</Button>
            </div>

            {loading ? (
                <div style={{ textAlign: 'center', padding: 'var(--space-4) 0' }}>
                    <p>Loading claim requests...</p>
                </div>
            ) : error ? (
                <Card style={{ textAlign: 'center', color: 'var(--danger)' }}>{error}</Card>
            ) : claims.length === 0 ? (
                <Card style={{ textAlign: 'center', padding: 'var(--space-4) 0' }}>
                    <p className="no-items">No pending claims to review at this time.</p>
                </Card>
            ) : (
                <div className="claims-container">
                    {claims.map((claim) => (
                        <Card key={claim.id} className="admin-claim-card" hover={false}>
                            <div className="claim-card-header">
                                <span className="claim-id">CLAIM #{claim.id}</span>
                                <span className={`admin-status-badge ${claim.status}`}>{claim.status}</span>
                            </div>
                            
                            <div className="claim-card-body">
                                <div className="claim-main-info">
                                    <p className="claim-info-row">Item: <span>{claim.item_name || `Item ID: ${claim.found_item_id}`}</span></p>
                                    <p className="claim-info-row">Claimant: <span>{claim.claimant_email}</span></p>
                                    <p className="claim-info-row">Value: <span>${claim.declared_value}</span></p>
                                    <div className="match-score-pill">
                                        ⚡ {claim.score || 'N/A'}% Match
                                    </div>
                                </div>
                                
                                <div className="claim-proof-section">
                                    <p className="proof-label">User Provided Proof</p>
                                    <p className="proof-text">{claim.description}</p>
                                    {claim.receipt_proof && (
                                        <div style={{ marginTop: '8px' }}>
                                            <a href={claim.receipt_proof} target="_blank" rel="noreferrer" style={{ fontSize: '0.8125rem', color: 'var(--primary)', fontWeight: '600' }}>
                                                View Attachment ↗
                                            </a>
                                        </div>
                                    )}
                                </div>
                            </div>

                            <div className="claim-card-footer">
                                <Button 
                                    variant="secondary" 
                                    size="sm" 
                                    onClick={() => verifyClaim(claim.id, 'rejected')}
                                    style={{ borderColor: 'var(--danger)', color: 'var(--danger)' }}
                                >
                                    Reject
                                </Button>
                                <Button 
                                    variant="primary" 
                                    size="sm" 
                                    onClick={() => verifyClaim(claim.id, 'approved')}
                                >
                                    Approve Claim
                                </Button>
                                <Button 
                                    variant="neutral" 
                                    size="sm" 
                                    onClick={() => verifyClaim(claim.id, 'completed', 'Handover confirmed')}
                                >
                                    Handover
                                </Button>
                            </div>
                        </Card>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;

