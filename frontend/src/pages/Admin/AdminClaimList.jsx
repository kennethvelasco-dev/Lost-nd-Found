import React, { useState, useEffect, useCallback } from 'react';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';

const AdminClaimList = () => {
    const { loading, error, data, request } = useHttp();
    const [verifying, setVerifying] = useState(null);

    const fetchClaims = useCallback(() => {
        request({ url: '/admin/claims' });
    }, [request]);

    useEffect(() => {
        fetchClaims();
    }, [fetchClaims]);

    const claims = data?.claims || [];

    const handleAction = async (claimId, action) => {
        setVerifying(claimId);
        try {
            await api.post(`/admin/claims/${claimId}/review`, { action });
            fetchClaims();
        } catch (err) {
            console.error('Failed to update claim', err);
        } finally {
            setVerifying(null);
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Ownership Verification</h1>
                    <p className="auth-subtitle">Review claims to ensure items return to their rightful owners.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState 
                    loading={loading} 
                    error={error} 
                    isEmpty={claims.length === 0} 
                    emptyMessage="All claims have been processed. Excellent work!"
                    onRetry={fetchClaims}
                >
                    <div className="claims-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                        {claims.map(claim => (
                            <Card key={claim.id}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <h3 style={{ color: 'var(--primary)', margin: 0 }}>Claim for: {claim.item_type}</h3>
                                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>Submitted by: <strong>{claim.user_name}</strong> on {new Date(claim.created_at).toLocaleDateString()}</p>
                                    </div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <Button 
                                            variant="secondary" 
                                            onClick={() => handleAction(claim.id, 'reject')}
                                            disabled={verifying === claim.id}
                                        >
                                            Reject
                                        </Button>
                                        <Button 
                                            variant="primary" 
                                            onClick={() => handleAction(claim.id, 'approve')}
                                            disabled={verifying === claim.id}
                                        >
                                            Approve
                                        </Button>
                                    </div>
                                </div>
                                <div style={{ marginTop: 'var(--space-3)', padding: 'var(--space-3)', background: 'rgba(0,0,0,0.02)', borderRadius: 'var(--radius-sm)', border: '1px solid rgba(0,0,0,0.05)' }}>
                                    <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px', letterSpacing: '0.5px' }}>Ownership Description</h4>
                                    <p style={{ margin: 0, fontSize: '0.95rem' }}>{claim.answers.description}</p>
                                    {claim.answers.proof && (
                                        <div style={{ marginTop: '12px', paddingTop: '12px', borderTop: '1px solid rgba(0,0,0,0.05)' }}>
                                            <h4 style={{ fontSize: '11px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '4px', letterSpacing: '0.5px' }}>Proof Provided</h4>
                                            <p style={{ margin: 0, fontSize: '0.9rem' }}>{claim.answers.proof}</p>
                                        </div>
                                    )}
                                </div>
                            </Card>
                        ))}
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default AdminClaimList;
