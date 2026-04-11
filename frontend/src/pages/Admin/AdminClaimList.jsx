import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import { ClaimListSkeleton } from '../../components/common/Skeleton';

const AdminClaimList = () => {
    const { loading, error, data, request } = useHttp();
    const navigate = useNavigate();

    const fetchClaims = useCallback(() => {
        // Explicitly filter for pending only
        request({ url: '/claims/pending', params: { status: 'pending' } });
    }, [request]);

    useEffect(() => {
        fetchClaims();
    }, [fetchClaims]);

    const claims = data || [];

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Pending Claims</h1>
                    <p className="auth-subtitle">Verify ownership details for new claim requests.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={claims.length === 0}
                    emptyMessage="No pending claims at the moment. Good job!"
                    onRetry={fetchClaims}
                    skeleton={<ClaimListSkeleton rows={4} />}
                >
                    <div className="claims-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                        {claims.map(claim => (
                            <Card key={claim.id}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
                                            <h3 style={{ color: 'var(--primary)', margin: 0 }}>{claim.item_type}</h3>
                                            <span style={{ 
                                                fontSize: '10px', 
                                                padding: '2px 8px', 
                                                borderRadius: '10px', 
                                                background: 'var(--warning)', 
                                                color: 'white',
                                                fontWeight: 'bold',
                                                textTransform: 'uppercase'
                                            }}>
                                                PENDING REVIEW
                                            </span>
                                        </div>
                                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                            Claimed by: <strong>{claim.user_name}</strong> • {new Date(claim.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <Button 
                                            variant="primary" 
                                            onClick={() => navigate(`/admin/claims/${claim.id}`)}
                                        >
                                            Review Detail
                                        </Button>
                                    </div>
                                </div>
                                <div style={{ marginTop: 'var(--space-3)', display: 'grid', gridTemplateColumns: '1fr 2fr', gap: 'var(--space-4)' }}>
                                    {claim.main_picture && (
                                        <div style={{ height: '100px', borderRadius: 'var(--radius-sm)', overflow: 'hidden', border: '1px solid rgba(0,0,0,0.05)' }}>
                                            <img src={claim.main_picture} alt="Preview" style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                        </div>
                                    )}
                                    <div style={{ fontSize: '0.85rem' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Confidence Score:</span>
                                            <strong style={{ color: claim.score >= 70 ? 'var(--success)' : 'var(--warning)' }}>{claim.score}%</strong>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Color/Brand:</span>
                                            <span>{claim.item_color || 'N/A'} • {claim.item_brand || 'N/A'}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                            <span style={{ color: 'var(--text-secondary)' }}>Incident Date:</span>
                                            <span>{claim.incident_date ? new Date(claim.incident_date).toLocaleDateString() : 'N/A'}</span>
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

export default AdminClaimList;

