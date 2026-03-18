import React from 'react';
import { useNavigate } from 'react-router-dom';
import Card from './Card';
import Button from './Button';
import '../../pages/Discovery/Discovery.css';

const ItemCard = ({ item, isReturned }) => {
    const navigate = useNavigate();

    return (
        <Card 
            className="item-card" 
            onClick={() => navigate(`/items/${item.id}`)}
        >
            <div className="item-image-container">
                <img
                    src={item.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}
                    alt={item.item_type}
                    className="item-image"
                />
                <div className={`status-badge ${isReturned ? 'returned' : 'lost'}`}>
                    {isReturned ? 'Returned' : 'Lost'}
                </div>
            </div>

            <div className="item-details">
                <h3 className="item-type">{item.item_type}</h3>
                
                <div className="item-info-list">
                    <p className="item-info">Location: <span>{item.found_location}</span></p>
                    <p className="item-info">Color: <span>{item.color}</span></p>
                    <p className="item-info">Date: <span>{new Date(item.created_at || item.found_datetime).toLocaleDateString()}</span></p>
                </div>

                <div className="card-actions">
                    <Button variant="secondary" size="sm" style={{ width: '100%' }}>
                        View Details
                    </Button>
                </div>
            </div>
        </Card>
    );
};

export default ItemCard;

