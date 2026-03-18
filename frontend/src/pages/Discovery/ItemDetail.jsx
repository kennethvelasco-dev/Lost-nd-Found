import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';
import './ItemDetail.css';

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

    const handleClaim = () => {
        navigate(`/items/${id}/claim`);
    };

    if (loading) return <div className="page-container"><div className="container" style={{ textAlign: 'center', padding: '100px' }}>Loading...</div></div>;
    if (!item) return <div className="page-container"><div className="container" style={{ textAlign: 'center', padding: '100px' }}>Item not found</div></div>;

    return (
        <div className="page-container">
            <div className="container" style={{ maxWidth: '1000px' }}>
                <div className="pretty-header">
                    <h1 className="pretty-title">{item.item_type}</h1>
                    <div className="title-underline"></div>
                </div>

                <div className="detail-layout" style={{ display: 'grid', gridTemplateColumns: 'minmax(300px, 1fr) 1fr', gap: 'var(--space-4)' }}>
                    <div className="detail-image-section">
                        <Card className="image-card" style={{ position: 'relative', padding: 'var(--space-2)' }}>
                            <img 
                                src={images[currentImageIndex] || '/assets/logo.png'} 
                                alt={item.item_type} 
                                style={{ width: '100%', aspectRatio: '1/1', objectFit: 'cover', borderRadius: 'var(--radius-md)' }}
                            />
                            {images.length > 1 && (
                                <div className="image-nav" style={{ position: 'absolute', width: '100%', top: '50%', transform: 'translateY(-50%)', display: 'flex', justifyContent: 'space-between', padding: '0 10px', pointerEvents: 'none' }}>
                                    <button 
                                        onClick={() => setCurrentImageIndex((prev) => (prev - 1 + images.length) % images.length)}
                                        style={{ pointerEvents: 'auto', background: 'rgba(255,255,255,0.7)', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer' }}
                                    >
                                        ‹
                                    </button>
                                    <button 
                                        onClick={() => setCurrentImageIndex((prev) => (prev + 1) % images.length)}
                                        style={{ pointerEvents: 'auto', background: 'rgba(255,255,255,0.7)', border: 'none', borderRadius: '50%', width: '32px', height: '32px', cursor: 'pointer' }}
                                    >
                                        ›
                                    </button>
                                </div>
                            )}
                        </Card>
                        <div className="thumbnail-strip" style={{ display: 'flex', gap: '8px', marginTop: '12px' }}>
                            {images.map((img, idx) => (
                                <Card 
                                    key={idx} 
                                    className={`thumbnail ${idx === currentImageIndex ? 'active' : ''}`}
                                    onClick={() => setCurrentImageIndex(idx)}
                                    style={{ padding: '4px', cursor: 'pointer', opacity: idx === currentImageIndex ? 1 : 0.6 }}
                                >
                                    <img src={img} alt="thumbnail" style={{ width: '50px', height: '50px', objectFit: 'cover', borderRadius: '4px' }} />
                                </Card>
                            ))}
                        </div>
                    </div>

                    <div className="detail-info-section">
                        <Card style={{ height: '100%', display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                <h2 style={{ color: 'var(--primary)', margin: 0 }}>Item Details</h2>
                                <span className="status-badge" style={{ background: '#dcfce7', color: '#166534', padding: '4px 12px', borderRadius: '20px', fontSize: '12px', fontWeight: 700 }}>
                                    {item.status.toUpperCase()}
                                </span>
                            </div>

                            <div className="info-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-3)' }}>
                                <div className="info-item">
                                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Category</label>
                                    <p style={{ fontWeight: 600 }}>{item.category}</p>
                                </div>
                                <div className="info-item">
                                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Color</label>
                                    <p style={{ fontWeight: 600 }}>{item.color || 'N/A'}</p>
                                </div>
                                <div className="info-item">
                                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Last Seen At</label>
                                    <p style={{ fontWeight: 600 }}>{item.found_location || item.last_seen_location}</p>
                                </div>
                                <div className="info-item">
                                    <label style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Date Reported</label>
                                    <p style={{ fontWeight: 600 }}>{new Date(item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</p>
                                </div>
                            </div>

                            <div className="description-block" style={{ borderTop: '1px solid #eee', paddingTop: 'var(--space-3)' }}>
                                <label style={{ fontSize: '11px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Description</label>
                                <p style={{ marginTop: '4px', lineHeight: '1.5' }}>{item.public_description || 'No description provided.'}</p>
                            </div>

                            <div className="action-block" style={{ marginTop: 'auto' }}>
                                <Button 
                                    variant="primary" 
                                    size="lg" 
                                    style={{ width: '100%' }}
                                    onClick={handleClaim}
                                >
                                    This belongs to me
                                </Button>
                            </div>
                        </Card>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ItemDetail;
