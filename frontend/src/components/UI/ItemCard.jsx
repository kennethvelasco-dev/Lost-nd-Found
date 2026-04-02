import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from './Card';
import Button from './Button';
import './ItemCard.css';

const ItemCard = ({ item, isReturned }) => {
    const navigate = useNavigate();

    // Determine fallback image based on ID
    const placeholder = `/assets/item_${(item.id % 3) + 1}.jpg`;
    const displayImage = item.main_picture || item.image_url || placeholder;
    const isResolved = isReturned || item.status === 'found';

    return (
        <Card 
            className="item-card" 
            onClick={() => navigate(`/items/${item.report_id || item.id}`)}
        >
            <div className="item-image-container">
                <img
                    src={displayImage}
                    alt={item.item_type}
                    className="item-image"
                />
                <div className={`status-badge ${isResolved ? 'returned' : 'lost'}`}>
                    {isResolved ? 'VERIFIED' : 'LOST'}
                </div>
            </div>

            <div className="item-details">
                <h3 className="item-type">{item.item_type}</h3>
                
                <div className="item-info-grid">
                    <div className="item-info-row">
                        <span className="info-label">{item.type === 'lost' ? 'Lost at' : 'Found at'}</span>
                        <span className="info-value">{item.found_location || item.last_seen_location}</span>
                    </div>
                    {isResolved && item.recipient_name ? (
                        <>
                            <div className="item-info-row">
                                <span className="info-label">Claimed By</span>
                                <span className="info-value" style={{ color: 'var(--success)', fontWeight: 'bold' }}>{item.recipient_name}</span>
                            </div>
                            <div className="item-info-row">
                                <span className="info-label">Returned On</span>
                                <span className="info-value">{new Date(item.resolved_at || item.created_at).toLocaleDateString()}</span>
                            </div>
                        </>
                    ) : (
                        <>
                            <div className="item-info-row">
                                <span className="info-label">Color</span>
                                <span className="info-value">{item.color || 'N/A'}</span>
                            </div>
                            <div className="item-info-row">
                                <span className="info-label">{item.type === 'lost' ? 'Lost on' : 'Found on'}</span>
                                <span className="info-value">{new Date(item.created_at || item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</span>
                            </div>
                        </>
                    )}
                </div>

                <div className="card-actions">
                    <Button variant="secondary" size="sm" style={{ width: '100%', marginTop: '15px' }}>
                        Inspect Item
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default ItemCard;
