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

    return (
        <Card 
            className="item-card" 
            onClick={() => navigate(`/items/${item.id}`)}
        >
            <div className="item-image-container">
                <img
                    src={displayImage}
                    alt={item.item_type}
                    className="item-image"
                />
                <div className={`status-badge ${isReturned || item.status === 'returned' ? 'returned' : 'lost'}`}>
                    {isReturned || item.status === 'returned' ? 'VERIFIED' : 'LOST'}
                </div>
            </div>

            <div className="item-details">
                <h3 className="item-type">{item.item_type}</h3>
                
                <div className="item-info-grid">
                    <div className="item-info-row">
                        <span className="info-label">Where</span>
                        <span className="info-value">{item.found_location || item.last_seen_location}</span>
                    </div>
                    <div className="item-info-row">
                        <span className="info-label">Color</span>
                        <span className="info-value">{item.color}</span>
                    </div>
                    <div className="item-info-row">
                        <span className="info-label">Date</span>
                        <span className="info-value">{new Date(item.created_at || item.found_datetime || item.last_seen_datetime).toLocaleDateString()}</span>
                    </div>
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
