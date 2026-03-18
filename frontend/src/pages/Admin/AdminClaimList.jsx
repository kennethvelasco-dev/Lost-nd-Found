import React, { useState, useEffect } from 'react';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import api from '../../services/api';

const AdminClaimList = () => {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchClaims = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/claims');
            setClaims(response.data.data.claims || []);
        } catch (err) {
            console.error('Failed to fetch claims', err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchClaims();
    }, []);

    const handleAction = async (claimId, action) => {
        try {
            await api.post(`/admin/claims/${claimId}/review`, { action });
            fetchClaims();
        } catch (err) {
            console.error('Failed to update claim', err);
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Review Owner Claims</h1>
                    <p className="auth-subtitle">Verify ownership for pending found items.</p>
                    <div className="title-underline"></div>
                </div>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '100px' }}>Loading pending reviews...</div>
                ) : (
                    <div className="claims-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                        {claims.map(claim => (
                            <Card key={claim.id}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h3 style={{ color: 'var(--primary)', margin: 0 }}>Claim for: {claim.item_type}</h3>
                                        <p style={{ color: 'var(--text-muted)', fontSize: '0.9rem' }}>Submitted by: <strong>{claim.user_name}</strong> on {new Date(claim.created_at).toLocaleDateString()}</p>
                                    </div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <Button variant="secondary" size="sm" onClick={() => handleAction(claim.id, 'reject')}>Reject</Button>
                                        <Button variant="primary" size="sm" onClick={() => handleAction(claim.id, 'approve')}>Approve</Button>
                                    </div>
                                </div>
                                <div style={{ marginTop: 'var(--space-3)', padding: 'var(--space-3)', background: 'var(--background)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-inset)' }}>
                                    <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>Ownership Description</h4>
                                    <p style={{ margin: 0 }}>{claim.answers.description}</p>
                                    {claim.answers.proof && (
                                        <div style={{ marginTop: '10px' }}>
                                            <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-muted)', marginBottom: '4px' }}>Proof Provided</h4>
                                            <p style={{ margin: 0, fontSize: '0.9rem' }}>{claim.answers.proof}</p>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        ))}
                        {claims.length === 0 && (
                            <div style={{ textAlign: 'center', padding: '100px', color: 'var(--text-muted)' }}>No pending claims to review.</div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminClaimList;
