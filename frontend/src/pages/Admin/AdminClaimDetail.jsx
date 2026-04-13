import React, { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';

const AdminClaimDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { loading, error, data, request } = useHttp();
    const [verifying, setVerifying] = useState(false);
    const [selectedPhoto, setSelectedPhoto] = useState(null);

    const fetchDetail = useCallback(() => {
        request({ url: `/claims/${id}` });
    }, [id, request]);

    useEffect(() => {
        fetchDetail();
    }, [fetchDetail]);

    const handleAction = async (action) => {
        setVerifying(true);
        try {
            let decision = action;
            if (action === 'approve') decision = 'approved';
            if (action === 'reject') decision = 'rejected';

            await api.post(`/claims/${id}/verify`, { decision });
            fetchDetail();
            if (decision === 'approved') {
                navigate('/admin/claims');
            }
        } catch (err) {
            alert(`Error: ${err.response?.data?.message || err.message}`);
        } finally {
            setVerifying(false);
        }
    };

    const claim = data;
    const status = claim?.status || claim?.decision || 'pending';

    if (!claim && !loading && !error) return null;

    return (
        <div className="page-container">
            <div className="container" style={{ maxWidth: '1000px' }}>
                <div className="pretty-header">
                    <div style={{ display: 'flex', alignItems: 'center', gap: '15px' }}>
                        <Button variant="secondary" size="sm" onClick={() => navigate(-1)}>← Back</Button>
                        <h1 className="pretty-title" style={{ margin: 0 }}>Verification Center</h1>
                    </div>
                    <p className="auth-subtitle">Phase 2: Side-by-Side Detailed Ownership Audit</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState loading={loading} error={error} isEmpty={!claim} onRetry={fetchDetail}>
                    {claim && (
                        <div className="verification-grid" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 'var(--space-4)' }}>
                            {/* Top Status Bar */}
                            <Card style={{ borderLeft: `5px solid ${status === 'approved' ? 'var(--success)' : status === 'rejected' ? 'var(--danger)' : 'var(--warning)'}` }}>
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <h2 style={{ margin: 0, color: 'var(--primary)' }}>Claim #{claim.id}</h2>
                                            <span style={{ 
                                                fontSize: '11px', 
                                                background: 'rgba(0,0,0,0.05)', 
                                                padding: '2px 8px', 
                                                borderRadius: '4px',
                                                color: 'var(--text-secondary)',
                                                fontWeight: 'bold'
                                            }}>
                                                Item ID: #{claim.item_id || claim.found_item_id || claim.lost_item_id || 'GENERAL'}
                                            </span>
                                        </div>
                                        <h3 style={{ margin: '4px 0', fontSize: '1.2rem' }}>{claim.item_type || 'Unknown Item'}</h3>
                                        <p style={{ margin: '4px 0 0 0', color: 'var(--text-secondary)', fontSize: '0.9rem' }}>
                                            Submitted by <strong>{claim.claimant_name || claim.user_name}</strong> • {new Date(claim.created_at).toLocaleString()}
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontWeight: 800, textTransform: 'uppercase' }}>Category</div>
                                        <div style={{ fontSize: '14px', fontWeight: 'bold', color: 'var(--primary)' }}>{claim.category || 'Uncategorized'}</div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <span style={{ 
                                            padding: '6px 16px', 
                                            borderRadius: '20px', 
                                            background: status === 'approved' ? 'var(--success)' : status === 'rejected' ? 'var(--danger)' : 'var(--warning)', 
                                            color: 'white',
                                            fontWeight: 'bold',
                                            fontSize: '12px',
                                            textTransform: 'uppercase'
                                        }}>
                                            {status === 'approved' ? 'Ready for Pickup' : status}
                                        </span>
                                    </div>
                                </div>
                            </Card>

                            <div style={{ display: 'grid', gridTemplateColumns: '2fr 1fr', gap: 'var(--space-4)' }}>
                                {/* Left: Comparison Table */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                                    <Card title="Detailed Attribute Comparison">
                                        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '0.95rem' }}>
                                            <thead>
                                                <tr style={{ textAlign: 'left', borderBottom: '2px solid var(--border-color)' }}>
                                                    <th style={{ padding: '12px 8px', color: 'var(--text-secondary)', fontSize: '11px', textTransform: 'uppercase' }}>Feature</th>
                                                    <th style={{ padding: '12px 8px', background: 'rgba(var(--primary-rgb), 0.05)', color: 'var(--primary)' }}>Original Report</th>
                                                    <th style={{ padding: '12px 8px', background: 'rgba(var(--success-rgb), 0.05)', color: 'var(--success)' }}>Claimant's Narrative</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Category</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.category}</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.answers?.claimed_category || 'N/A'}</td>
                                                </tr>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Item Type</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.item_type}</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.answers?.claimed_item_type || 'N/A'}</td>
                                                </tr>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Color</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.item_color || 'N/A'}</td>
                                                    <td style={{ padding: '12px 8px', color: claim.item_color?.toLowerCase() === claim.answers?.claimed_color?.toLowerCase() ? 'var(--success)' : 'inherit' }}>
                                                        {claim.answers?.claimed_color || 'N/A'}
                                                    </td>
                                                </tr>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Brand</td>
                                                    <td style={{ padding: '12px 8px' }}>{claim.item_brand || 'N/A'}</td>
                                                    <td style={{ padding: '12px 8px', color: claim.item_brand?.toLowerCase() === claim.answers?.claimed_brand?.toLowerCase() ? 'var(--success)' : 'inherit' }}>
                                                        {claim.answers?.claimed_brand || 'N/A'}
                                                    </td>
                                                </tr>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Incident Date</td>
                                                    <td style={{ padding: '12px 8px' }}>
                                                        {claim.incident_date ? new Date(claim.incident_date).toLocaleDateString() : 'N/A'}
                                                    </td>
                                                    <td style={{ padding: '12px 8px' }}>
                                                        {claim.answers?.claimed_datetime || claim.answers?.lost_datetime
                                                            ? new Date(claim.answers?.claimed_datetime || claim.answers?.lost_datetime).toLocaleDateString()
                                                            : 'N/A'}
                                                    </td>
                                                </tr>
                                                <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                                                    <td style={{ padding: '12px 8px', fontWeight: 'bold' }}>Where</td>
                                                    <td style={{ padding: '12px 8px' }}>
                                                        {claim.location || claim.found_location || claim.last_seen_location || 'N/A'}
                                                    </td>
                                                    <td style={{ padding: '12px 8px' }}>
                                                        {claim.answers?.lost_location_claimed ||
                                                         claim.answers?.claimed_location ||
                                                         'N/A'}
                                                    </td>
                                                </tr>
                                            </tbody>
                                        </table>
                                    </Card>

                                    <Card title="Claimant's Personal Explanation">
                                        <p style={{ margin: 0, fontStyle: 'italic', fontSize: '1.1rem', lineHeight: '1.6', color: 'var(--text-main)' }}>
                                            "{claim.answers?.description || 'No detailed explanation provided.'}"
                                        </p>
                                        {claim.answers?.declared_value > 0 && (
                                            <div style={{ marginTop: '15px', padding: '10px', background: 'rgba(var(--primary-rgb), 0.05)', borderRadius: 'var(--radius-sm)' }}>
                                                <strong>Declared Value:</strong> ${claim.answers.declared_value}
                                            </div>
                                        )}
                                    </Card>
                                </div>

                                {/* Right: Confidence Score */}
                                <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                                    <Card style={{ textAlign: 'center', height: '100%', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                                        <h4 style={{ fontSize: '12px', textTransform: 'uppercase', color: 'var(--text-secondary)', marginBottom: '8px' }}>Confidence</h4>
                                        <div style={{ 
                                            width: '100px', 
                                            height: '100px', 
                                            border: `8px solid ${claim.score >= 70 ? 'var(--success)' : claim.score >= 40 ? 'var(--warning)' : 'var(--danger)'}`, 
                                            borderRadius: '50%', 
                                            display: 'flex', 
                                            alignItems: 'center', 
                                            justifyContent: 'center',
                                            margin: '0 auto var(--space-2)'
                                        }}>
                                            <strong style={{ fontSize: '1.5rem' }}>{claim.score}%</strong>
                                        </div>
                                        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', margin: 0 }}>Automated Match Logic</p>
                                    </Card>
                                </div>
                            </div>

                            {/* Visual Evidence Section */}
                             <div style={{ 
                                display: 'grid', 
                                gridTemplateColumns: claim.answers?.receipt_proof ? '1fr 1fr' : '1fr', 
                                gap: 'var(--space-4)' 
                            }}>
                                <Card title="📦 Photos uploaded from the report" style={{ display: 'flex', flexDirection: 'column', borderTop: '4px solid var(--primary)' }}>
                                    <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>This is the photo uploaded when the item was first found.</p>
                                    {claim.main_picture ? (
                                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.02)' }}>
                                            <img 
                                                src={claim.main_picture} 
                                                alt="Reported" 
                                                onClick={() => setSelectedPhoto(claim.main_picture)}
                                                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain', cursor: 'zoom-in' }} 
                                            />
                                        </div>
                                    ) : (
                                        <div style={{ height: '200px', background: 'var(--border-color)', display: 'flex', alignItems: 'center', justifyContent: 'center', borderRadius: 'var(--radius-sm)' }}>No Image Provided</div>
                                    )}
                                </Card>

                                {claim.answers?.receipt_proof && (
                                    <Card title="📄 Photos for claim evidence" style={{ display: 'flex', flexDirection: 'column', borderTop: '4px solid var(--success)' }}>
                                        <p style={{ fontSize: '12px', color: 'var(--text-secondary)', marginBottom: '8px' }}>This is the evidence photo uploaded by {claim.claimant_name || 'the claimant'}.</p>
                                        <div style={{ flex: 1, display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', borderRadius: 'var(--radius-sm)', background: 'rgba(0,0,0,0.02)' }}>
                                            <img 
                                                src={claim.answers.receipt_proof} 
                                                alt="Proof" 
                                                onClick={() => setSelectedPhoto(claim.answers.receipt_proof)}
                                                style={{ maxWidth: '100%', maxHeight: '400px', objectFit: 'contain', cursor: 'zoom-in' }} 
                                            />
                                        </div>
                                    </Card>
                                )}
                            </div>

                            {/* Bottom Actions */}
                            <Card style={{ display: 'flex', justifyContent: 'center', gap: 'var(--space-4)', padding: 'var(--space-4)', background: 'rgba(var(--primary-rgb), 0.02)' }}>
                                {status === 'pending' ? (
                                    <>
                                        <Button
                                            variant="secondary"
                                            onClick={() => handleAction('reject')}
                                            disabled={verifying}
                                            style={{ minWidth: '140px' }}
                                        >
                                            Reject Claim
                                        </Button>
                                        <Button
                                            variant="primary"
                                            size="lg"
                                            onClick={() => handleAction('approve')}
                                            disabled={verifying}
                                            style={{
                                                minWidth: '200px',
                                                boxShadow: '0 8px 20px rgba(22, 163, 74, 0.3)',
                                                fontWeight: 800,
                                                textTransform: 'uppercase',
                                            }}
                                        >
                                            {verifying ? 'Approving...' : 'Approve Claim'}
                                        </Button>
                                    </>
                                ) : status === 'approved' ? (
                                    <Button 
                                        variant="success" 
                                        size="lg"
                                        style={{ background: 'var(--success)', color: 'white' }}
                                        onClick={() => {
                                            navigate('/admin/return-item', { 
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
                                            });
                                        }}
                                    >
                                        Finalize Handover & Log Return
                                    </Button>
                                ) : (
                                    <p style={{ margin: 0, fontWeight: 'bold' }}>This claim has been {status}.</p>
                                )}
                            </Card>
                        </div>
                    )}
                </StatusState>
            </div>

            {/* Zoom Modal */}
            {selectedPhoto && (
                <div 
                    onClick={() => setSelectedPhoto(null)}
                    style={{ position: 'fixed', top: 0, left: 0, width: '100vw', height: '100vh', background: 'rgba(0,0,0,0.9)', display: 'flex', justifyContent: 'center', alignItems: 'center', zIndex: 1000, cursor: 'zoom-out' }}
                >
                    <img src={selectedPhoto} alt="Zoom" style={{ maxWidth: '95%', maxHeight: '95%', borderRadius: 'var(--radius-md)' }} />
                </div>
            )}
        </div>
    );
};

export default AdminClaimDetail;
