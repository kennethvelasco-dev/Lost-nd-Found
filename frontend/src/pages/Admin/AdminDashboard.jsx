import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
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
                navigate('/login'); // Not authorized or session expired
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
            fetchClaims(); // Refresh list
        } catch (err) {
            alert(`Error verifying claim: ${err.response?.data?.message || err.message}`);
        }
    };

    return (
        <div className="admin-dashboard">
            <h2 className="admin-title">Admin Dashboard: Pending Claims</h2>

            {loading ? (
                <div className="loading-spinner">Loading claims...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : claims.length === 0 ? (
                <p className="no-items">No pending claims to review.</p>
            ) : (
                <div className="claims-list">
                    {claims.map((claim) => (
                        <div key={claim.id} className="claim-card glass-panel">
                            <div className="claim-header">
                                <h3>Claim #{claim.id}</h3>
                                <span className={`status-badge ${claim.status}`}>{claim.status}</span>
                            </div>
                            <div className="claim-body">
                                <p><strong>Item Name:</strong> {claim.item_name || `Found Item ID: ${claim.found_item_id}`}</p>
                                <p><strong>Claimant Email:</strong> {claim.claimant_email || 'N/A'}</p>
                                <p><strong>Reported Description:</strong> {claim.description}</p>
                                <p><strong>Declared Value:</strong> ${claim.declared_value}</p>
                                <p><strong>Match Score:</strong> <span className="score">{claim.score || 'N/A'}%</span></p>
                                {claim.receipt_proof && (
                                    <p><strong>Proof URL:</strong> <a href={claim.receipt_proof} target="_blank" rel="noreferrer">View Proof</a></p>
                                )}
                            </div>
                            <div className="claim-actions">
                                <button
                                    className="auth-primary-btn approve-btn"
                                    onClick={() => verifyClaim(claim.id, 'approved')}
                                >Approve</button>
                                <button
                                    className="auth-secondary-btn reject-btn"
                                    onClick={() => verifyClaim(claim.id, 'rejected')}
                                >Reject</button>
                                <button
                                    className="auth-secondary-btn complete-btn"
                                    onClick={() => verifyClaim(claim.id, 'completed', 'Handed over directly')}
                                >Complete Handover</button>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminDashboard;

