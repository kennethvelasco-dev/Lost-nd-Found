import React from 'react';
import '../../pages/Discovery/Discovery.css';
import { useNavigate } from 'react-router-dom';

const ItemCard = ({ item, isReturned }) => {
    const navigate = useNavigate();

    return (
        <div className="item-card glass-panel" onClick={() => navigate(`/items/${item.id}`)}>
            <div className="item-image-container">
                <img
                    src={item.image_url || 'https://via.placeholder.com/300x200?text=No+Image'}
                    alt={item.item_type}
                    className="item-image"
                />
                {isReturned && <div className="returned-badge">Returned</div>}
            </div>

            <div className="item-details">
                <h3 className="item-type">{item.item_type}</h3>
                <p className="item-info"><span>Color:</span> {item.color}</p>
                <p className="item-info"><span>Location:</span> {item.found_location}</p>
                <p className="item-info"><span>Reported:</span> {new Date(item.created_at || item.found_datetime).toLocaleDateString()}</p>
            </div>
        </div>
    );
};

export default ItemCard;

