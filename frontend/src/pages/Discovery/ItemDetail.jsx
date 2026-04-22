import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';
import LazyImage from '../../components/common/LazyImage';
import { ItemDetailSkeleton } from '../../components/common/Skeleton';

const ItemDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();

    const { loading, error, data, request } = useHttp();
    const { loading: releasedLoading, error: releasedError, data: releasedData, request: releasedRequest } = useHttp();

    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        request({ url: `/items/${id}` });
    }, [id, request]);

    const item = data;

    // If navigated from ReturnedItems, we might have `state.isFromReleased = true`
    const fromReleasedList = location.state?.fromReleased === true;

    // Load released snapshot when item is returned, or if forced via state
    useEffect(() => {
        if (!item) return;

        const isReturnedStatus = item.status === 'returned';
        const shouldFetchReleased = isReturnedStatus || fromReleasedList;

        if (shouldFetchReleased && item.report_id) {
            releasedRequest({ url: `/items/released/${item.report_id}` });
        }
    }, [item, fromReleasedList, releasedRequest]);

    const releasedSnapshot = releasedData;
    const images = item ? [
        item.main_picture,
        item.additional_picture_1,
        item.additional_picture_2,
        item.additional_picture_3
    ].filter(Boolean) : [];

    // Precompute status styling for the badge (when item is loaded)
    const isReturned = item?.status === 'returned';
    // Active states: approved (lost), found (found), reported_lost (lost)
    const isActive = ['approved', 'found', 'reported_lost'].includes(item?.status);
    
    const statusBg = isReturned ? '#e0f2fe' : (isActive ? '#dcfce7' : '#fee2e2');
    const statusColor = isReturned ? '#0369a1' : (isActive ? '#166534' : '#ef4444');

    return (
        <div className="page-container">
            <div className="container">
                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={!item && !loading && !error}
                    emptyMessage="We couldn't find the item you're looking for. It may have been removed or resolved."
                    onRetry={() => request({ url: `/items/${id}` })}
                    skeleton={<ItemDetailSkeleton />}
                >
                    {item && (
                        <>
                            <div className="pretty-header">
                                <h1 className="pretty-title">{item.item_type}</h1>
                                <div className="title-underline"></div>
                            </div>

                            <div className="detail-layout" style={{ 
                                display: 'grid', 
                                gridTemplateColumns: 'repeat(auto-fit, minmax(350px, 1fr))', 
                                gap: 'var(--space-5)', 
                                alignItems: 'start',
                                marginTop: 'var(--space-4)' 
                            }}>
                                <div className="image-section">
                                    <Card style={{ padding: '10px' }}>
                                        <LazyImage
                                            src={images[currentImageIndex] || '/assets/pub_logo.png'}
                                            alt={item.item_type}
                                            className="detail-main-image"
                                        />
                                        {images.length > 1 && (
                                            <div style={{ display: 'flex', gap: '10px', marginTop: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
                                                {images.map((img, idx) => (
                                                    <Card 
                                                        key={idx} 
                                                        onClick={() => setCurrentImageIndex(idx)}
                                                        style={{ padding: '4px', cursor: 'pointer', opacity: idx === currentImageIndex ? 1 : 0.5, transform: idx === currentImageIndex ? 'scale(1.05)' : 'scale(1)', transition: '0.2s' }}
                                                    >
                                                        <LazyImage src={img} alt={`Thumbnail ${idx + 1}`} className="detail-thumb-image" />
                                                    </Card>
                                                ))}
                                            </div>
                                        )}
                                    </Card>
                                </div>

                                <div className="info-section">
                                    <Card style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                            <div>
                                                <h2 style={{ color: 'var(--primary)', fontSize: '2rem', margin: '0 0 4px 0' }}>{item.item_type}</h2>
                                                <span style={{ color: 'var(--text-secondary)', fontSize: '0.8rem', textTransform: 'uppercase', letterSpacing: '1px' }}>System ID: #{item.id}</span>
                                            </div>
                                            <span style={{ 
                                                background: statusBg, 
                                                color: statusColor, 
                                                padding: '6px 16px', 
                                                borderRadius: '25px', 
                                                fontSize: '12px', 
                                                fontWeight: 800,
                                                textTransform: 'uppercase'
                                            }}>
                                                {isReturned ? 'returned' : item.status}
                                            </span>
                                        </div>

                                        <div className="specs-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                                            <div className="spec-item">
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>Category</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.category}</p>
                                            </div>
                                            <div className="spec-item">
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>Visual Color</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.color || 'No primary color'}</p>
                                            </div>
                                            <div className="spec-item">
                                                <label
                                                    style={{
                                                        display: 'block',
                                                        fontSize: '10px',
                                                        color: 'var(--text-secondary)',
                                                        textTransform: 'uppercase',
                                                        marginBottom: '4px',
                                                        fontWeight: 700
                                                    }}
                                                >
                                
                                                    {item.type === 'lost' ? 'Last seen at' : 'Found at'}
                                                </label>
                                                <p
                                                    style={{
                                                        margin: 0,
                                                        fontWeight: 700,
                                                        fontSize: '1.1rem'
                                                    }}
                                                >
                                                    {item.found_location || item.last_seen_location || 'Unknown location'}
                                                </p>
                                            </div>
                                            <div className="spec-item">
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>{item.type === 'lost' ? 'Lost on' : 'Found on'}</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{new Date(item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</p>
                                            </div>
                                            <div className="spec-item">
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>Reported on</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{new Date(item.created_at).toLocaleDateString()}</p>
                                            </div>
                                        </div>

                                        <div style={{ background: 'var(--background)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-inset)' }}>
                                            <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 700 }}>Public Description</label>
                                            <p style={{ margin: 0, lineHeight: 1.6 }}>{item.public_description || 'The reporter has not provided a public summary for this item.'}</p>
                                        </div>

                                        {/* Return Log / Released Snapshot */}
                                        {item.status === 'returned' && (
                                            <Card style={{ marginTop: 'var(--space-3)', borderLeft: '4px solid var(--primary)' }}>
                                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: 'var(--space-2)' }}>
                                                    <div>
                                                        <h3 style={{ margin: 0, fontSize: '1.2rem', color: 'var(--primary)' }}>Return Summary</h3>
                                                        <p style={{ margin: '4px 0 0', fontSize: '0.85rem', color: 'var(--text-secondary)' }}>
                                                            This item has been verified and released to its rightful owner.
                                                        </p>
                                                    </div>
                                                    {releasedLoading && (
                                                        <span style={{ fontSize: '0.75rem', color: 'var(--text-muted)' }}>Loading log...</span>
                                                    )}
                                                    {releasedError && (
                                                        <span style={{ fontSize: '0.75rem', color: 'var(--danger)' }}>Failed to load log</span>
                                                    )}
                                                </div>

                                                {releasedSnapshot && (
                                                    <div style={{ display: 'grid', gridTemplateColumns: releasedSnapshot.turnover_proof ? '1.5fr 1fr' : '1fr', gap: 'var(--space-3)' }}>
                                                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '0.9rem' }}>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Claimant / Recipient</span>
                                                                <span style={{ fontWeight: 700 }}>{releasedSnapshot.claimant_name || item.recipient_name || 'N/A'}</span>
                                                            </div>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Recipient ID</span>
                                                                <span>{releasedSnapshot.recipient_id || 'N/A'}</span>
                                                            </div>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Released By</span>
                                                                <span>{releasedSnapshot.released_by_admin || 'N/A'}</span>
                                                            </div>
                                                            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
                                                                <span style={{ fontWeight: 600, color: 'var(--text-secondary)' }}>Released On</span>
                                                                <span>{new Date(releasedSnapshot.resolved_at || item.resolved_at || item.created_at).toLocaleString()}</span>
                                                            </div>
                                                            {releasedSnapshot.handover_notes && (
                                                                <div style={{ marginTop: '8px', paddingTop: '8px', borderTop: '1px dashed var(--border-color)' }}>
                                                                    <span style={{ display: 'block', fontWeight: 600, fontSize: '0.8rem', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px' }}>
                                                                        Handover Notes
                                                                    </span>
                                                                    <p style={{ margin: 0, fontSize: '0.9rem' }}>{releasedSnapshot.handover_notes}</p>
                                                                </div>
                                                            )}
                                                        </div>

                                                            {releasedSnapshot.turnover_proof && (
                                                                <div style={{ 
                                                                    borderRadius: 'var(--radius-sm)', 
                                                                    overflow: 'hidden', 
                                                                    background: 'rgba(0,0,0,0.02)', 
                                                                    border: '1px solid var(--border-color)',
                                                                    maxHeight: '200px'
                                                                }}>
                                                                    <LazyImage
                                                                        src={releasedSnapshot.turnover_proof}
                                                                        alt="Turnover proof"
                                                                        className="detail-main-image"
                                                                        style={{ height: '100%', objectFit: 'cover' }}
                                                                    />
                                                                </div>
                                                            )}
                                                    </div>
                                                )}
                                            </Card>
                                        )}

                                        {/* Claim CTA only for items that are not yet returned */}
                                        {(item.type === 'found' || item.type === 'lost') && item.status !== 'returned' && (
                                            <Button 
                                                variant="primary" 
                                                size="lg" 
                                                style={{ width: '100%', marginTop: 'var(--space-2)', padding: '18px' }}
                                                onClick={() => navigate(`/items/${id}/claim`)}
                                            >
                                                Begin Ownership Claim
                                            </Button>
                                        )}
                                    </Card>
                                </div>
                            </div>
                        </>
                    )}
                </StatusState>
            </div>
        </div>
    );
};

export default ItemDetail;
