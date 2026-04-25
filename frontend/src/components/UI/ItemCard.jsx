import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from './Card';
import Button from './Button';
import LazyImage from '../common/LazyImage';
import './ItemCard.css';

const ItemCard = ({ item, isReturned }) => {
    const navigate = useNavigate();

    // Determine fallback image based on ID
    const placeholder = `/assets/item_${(item.id % 3) + 1}.jpg`;
    const displayImage = item.main_picture || item.image_url || placeholder;
    const isResolved = isReturned || item.status === 'returned';
    const isFoundType = item.type === 'found' || item.status === 'found';

    // Released items store claimant_name; original tables have recipient_name
    const displayRecipientName = item.recipient_name || item.claimant_name;

    const handleClick = () => {
        if (isReturned) {
            console.log('Inspect clicked (returned):', item.id, item.original_report_id, item.category, item.item_type);
            navigate(`/returns/${item.id}`);
        } else {
            const targetId = item.report_id || item.id;
            console.log('Inspect clicked (standard):', targetId, item.category, item.item_type);
            navigate(`/items/${targetId}`);
        }
    };

    return (
        <Card 
            className="item-card" 
            onClick={handleClick}
        >
            <div className="item-image-container">
                <LazyImage
                    src={displayImage}
                    alt={item.item_type}
                    className="item-image"
                />
                <div className={`status-badge ${isResolved ? 'returned' : (isFoundType ? 'found' : 'lost')}`}>
                    {isResolved ? 'VERIFIED' : (isFoundType ? 'FOUND' : 'LOST')}
                </div>
            </div>

            <div className="item-details">
                <h3 className="item-type">{item.item_type}</h3>
                
                <div className="item-info-grid">
                    <div className="item-info-row">
                        <span className="info-label">
                            {item.type === 'lost' ? 'Last seen at' : 'Found at'}
                        </span>
                        <span className="info-value">
                            {item.found_location ||
                             item.last_seen_location ||
                             item.location ||
                             'Unknown location'}
                        </span>
                    </div>

                    {isResolved && displayRecipientName ? (
                        <>
                            <div className="item-info-row">
                                <span className="info-label">Claimed By</span>
                                <span className="info-value" style={{ color: 'var(--success)', fontWeight: 'bold' }}>
                                    {displayRecipientName}
                                </span>
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
