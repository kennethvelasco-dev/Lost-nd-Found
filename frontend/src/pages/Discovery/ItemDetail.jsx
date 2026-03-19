import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';

const ItemDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { loading, error, data: item, request } = useHttp();
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        request({ url: `/items/found/${id}` });
    }, [id, request]);

    const images = item ? [
        item.main_picture,
        item.additional_picture_1,
        item.additional_picture_2,
        item.additional_picture_3
    ].filter(Boolean) : [];

    return (
        <div className="page-container">
            <div className="container">
                <StatusState 
                    loading={loading} 
                    error={error} 
                    isEmpty={!item && !loading && !error} 
                    emptyMessage="We couldn't find the item you're looking for. It may have been removed or resolved."
                    onRetry={() => request({ url: `/items/found/${id}` })}
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
                                        <img 
                                            src={images[currentImageIndex] || '/assets/logo.png'} 
                                            alt={item.item_type} 
                                            style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover', borderRadius: 'var(--radius-md)', boxShadow: 'var(--nm-inset)' }}
                                        />
                                        {images.length > 1 && (
                                            <div style={{ display: 'flex', gap: '10px', marginTop: '15px', justifyContent: 'center', flexWrap: 'wrap' }}>
                                                {images.map((img, idx) => (
                                                    <Card 
                                                        key={idx} 
                                                        onClick={() => setCurrentImageIndex(idx)}
                                                        style={{ padding: '4px', cursor: 'pointer', opacity: idx === currentImageIndex ? 1 : 0.5, transform: idx === currentImageIndex ? 'scale(1.05)' : 'scale(1)', transition: '0.2s' }}
                                                    >
                                                        <img src={img} alt="thumb" style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '4px' }} />
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
                                                background: item.status === 'approved' ? '#dcfce7' : '#fee2e2', 
                                                color: item.status === 'approved' ? '#166534' : '#ef4444', 
                                                padding: '6px 16px', 
                                                borderRadius: '25px', 
                                                fontSize: '12px', 
                                                fontWeight: 800,
                                                textTransform: 'uppercase'
                                            }}>
                                                {item.status}
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
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>Location Context</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.found_location || item.last_seen_location}</p>
                                            </div>
                                            <div className="spec-item">
                                                <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '4px', fontWeight: 700 }}>Last Activity</label>
                                                <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{new Date(item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</p>
                                            </div>
                                        </div>

                                        <div style={{ background: 'var(--background)', padding: 'var(--space-4)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-inset)' }}>
                                            <label style={{ display: 'block', fontSize: '10px', color: 'var(--text-secondary)', textTransform: 'uppercase', marginBottom: '8px', fontWeight: 700 }}>Public Description</label>
                                            <p style={{ margin: 0, lineHeight: 1.6 }}>{item.public_description || 'The reporter has not provided a public summary for this item.'}</p>
                                        </div>

                                        <Button 
                                            variant="primary" 
                                            size="lg" 
                                            style={{ width: '100%', marginTop: 'var(--space-2)', padding: '18px' }}
                                            onClick={() => navigate(`/items/${id}/claim`)}
                                        >
                                            Begin Ownership Claim
                                        </Button>
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
