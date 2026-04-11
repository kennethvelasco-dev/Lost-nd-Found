import React, { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';

const AdminApprovedClaims = () => {
    const { loading, error, data, request } = useHttp();
    const navigate = useNavigate();

    const fetchClaims = useCallback(() => {
        // Explicitly filter for approved only
        request({ url: '/claims', params: { status: 'approved' } });
    }, [request]);

    useEffect(() => {
        fetchClaims();
    }, [fetchClaims]);

    const claims = data || [];

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Approved Pickups</h1>
                    <p className="auth-subtitle">Manage items ready for physical handover to their owners.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState 
                    loading={loading} 
                    error={error} 
                    isEmpty={claims.length === 0} 
                    emptyMessage="No approved claims waiting for pickup."
                    onRetry={fetchClaims}
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
                                                background: 'var(--success)', 
                                                color: 'white',
                                                fontWeight: 'bold',
                                                textTransform: 'uppercase'
                                            }}>
                                                READY FOR PICKUP
                                            </span>
                                        </div>
                                        <p style={{ color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                            Owner: <strong>{claim.user_name}</strong> • Approved on {new Date(claim.created_at).toLocaleDateString()}
                                        </p>
                                    </div>
                                    <div style={{ display: 'flex', gap: '10px' }}>
                                        <Button 
                                            variant="secondary" 
                                            onClick={() => navigate(`/admin/claims/${claim.id}`)}
                                        >
                                            View Narrative
                                        </Button>
                                        <Button 
                                            variant="success" 
                                            onClick={() => navigate('/admin/return-item', { 
                                                state: { 
                                                    itemId: claim.item_id || claim.found_item_id || claim.lost_item_id,
                                                    claim_id: claim.id,
                                                    claimantName: claim.claimant_name || claim.user_name,
                                                    category: claim.category,
                                                    itemType: claim.item_type || claim.category,
                                                    color: claim.item_color,
                                                    brand: claim.item_brand,
                                                    dateLost: claim.lost_date || claim.answers?.claimed_datetime || claim.answers?.lost_datetime,
                                                    dateFound: claim.found_date || claim.incident_date
                                                } 
                                            })}
                                            style={{ background: 'var(--success)', color: 'white' }}
                                        >
                                            Process Return Log
                                        </Button>
                                    </div>
                                </div>
                                <div style={{ marginTop: 'var(--space-3)', display: 'grid', gridTemplateColumns: 'minmax(120px, 1fr) 2fr', gap: 'var(--space-4)', background: 'rgba(0,0,0,0.02)', padding: '12px', borderRadius: 'var(--radius-sm)' }}>
                                    {claim.main_picture ? (
                                        <img src={claim.main_picture} alt="Thumbnail" style={{ width: '100%', height: '100px', objectFit: 'cover', borderRadius: '4px' }} />
                                    ) : (
                                        <div style={{ height: '100px', background: 'var(--border-color)', borderRadius: '4px', display: 'flex', alignItems: 'center', justifyContent: 'center', color: 'var(--text-secondary)', fontSize: '10px' }}>NO IMAGE</div>
                                    )}
                                    <div style={{ fontSize: '0.85rem', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                                        <div><strong>Pickup Location:</strong> {claim.pickup_location || 'Admin Office (Default)'}</div>
                                        <div style={{ marginTop: '4px' }}><strong>Instructions:</strong> User has been notified to present Student ID for verification.</div>
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

export default AdminApprovedClaims;
