import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';

const ItemDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [currentImageIndex, setCurrentImageIndex] = useState(0);

    useEffect(() => {
        const fetchItem = async () => {
            try {
                const response = await api.get(`/items/found/${id}`);
                setItem(response.data.data.item || response.data.data);
            } catch (err) {
                console.error('Failed to fetch item details', err);
            } finally {
                setLoading(false);
            }
        };
        fetchItem();
    }, [id]);

    const images = item ? [
        item.main_picture,
        item.additional_picture_1,
        item.additional_picture_2,
        item.additional_picture_3
    ].filter(Boolean) : [];

    if (loading) return <div className="page-container"><div className="container" style={{ textAlign: 'center', padding: '100px' }}>Analyzing item records...</div></div>;
    if (!item) return <div className="page-container"><div className="container" style={{ textAlign: 'center', padding: '100px' }}>Item not found in our database.</div></div>;

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">{item.item_type}</h1>
                    <div className="title-underline"></div>
                </div>

                <div className="detail-layout" style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1fr) 1.2fr', gap: 'var(--space-5)', alignItems: 'start' }}>
                    <div className="image-section">
                        <Card style={{ padding: '10px' }}>
                            <img 
                                src={images[currentImageIndex] || '/assets/logo.png'} 
                                alt={item.item_type} 
                                style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover', borderRadius: 'var(--radius-md)', boxShadow: 'var(--nm-inset)' }}
                            />
                            {images.length > 1 && (
                                <div style={{ display: 'flex', gap: '10px', marginTop: '15px', justifyContent: 'center' }}>
                                    {images.map((img, idx) => (
                                        <Card 
                                            key={idx} 
                                            onClick={() => setCurrentImageIndex(idx)}
                                            style={{ padding: '4px', cursor: 'pointer', opacity: idx === currentImageIndex ? 1 : 0.5 }}
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
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <div>
                                    <h2 style={{ color: 'var(--primary)', fontSize: '2rem', margin: 0 }}>{item.item_type}</h2>
                                    <span style={{ color: 'var(--text-muted)', fontSize: '0.85rem', textTransform: 'uppercase', letterSpacing: '1px' }}>ID: #{item.id}</span>
                                </div>
                                <span style={{ background: '#dcfce7', color: '#166534', padding: '6px 16px', borderRadius: '25px', fontSize: '13px', fontWeight: 800 }}>{item.status.toUpperCase()}</span>
                            </div>

                            <div className="specs-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                                <div className="spec-item">
                                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Category</label>
                                    <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.category}</p>
                                </div>
                                <div className="spec-item">
                                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Primary Color</label>
                                    <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.color || 'N/A'}</p>
                                </div>
                                <div className="spec-item">
                                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Location Discovered</label>
                                    <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{item.found_location || item.last_seen_location}</p>
                                </div>
                                <div className="spec-item">
                                    <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '4px' }}>Date Reported</label>
                                    <p style={{ margin: 0, fontWeight: 700, fontSize: '1.1rem' }}>{new Date(item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</p>
                                </div>
                            </div>

                            <div style={{ background: 'var(--background)', padding: 'var(--space-3)', borderRadius: 'var(--radius-sm)', boxShadow: 'var(--nm-inset)' }}>
                                <label style={{ display: 'block', fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase', marginBottom: '8px' }}>Public Description</label>
                                <p style={{ margin: 0, lineHeight: 1.6 }}>{item.public_description || 'No specific description provided by the reporter.'}</p>
                            </div>

                            <Button 
                                variant="primary" 
                                size="lg" 
                                style={{ width: '100%', marginTop: 'var(--space-2)' }}
                                onClick={() => navigate(`/items/${id}/claim`)}
                            >
                                This Belongs to Me
                            </Button>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ItemDetail;
