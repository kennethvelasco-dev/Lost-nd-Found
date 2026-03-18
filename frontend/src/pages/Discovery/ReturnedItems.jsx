import React, { useState, useEffect } from 'react';
import Card from '../../components/UI/Card';
import SearchBar from '../../components/UI/SearchBar';
import api from '../../services/api';
import './ReturnedItems.css';

const ReturnedItems = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchItems = async (query = '') => {
        try {
            setLoading(true);
            const response = await api.get('/items/found', {
                params: { query, status: 'returned' }
            });
            setItems(response.data.data.items || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch transaction history.');
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    return (
        <div className="page-container">
            <div className="container returned-items-page">
                <div className="pretty-header">
                    <h1 className="pretty-title">Verified Handovers</h1>
                    <p className="auth-subtitle">A history of items successfully reconnected with their owners.</p>
                    <div className="title-underline"></div>
                </div>

                <SearchBar onSearch={(q) => fetchItems(q)} />

                {loading ? (
                    <div className="loading-state">Loading history...</div>
                ) : (
                    <div className="returned-list">
                        {items.map(item => (
                            <Card key={item.id} className="returned-item-card" hover={false}>
                                <div className="returned-marker">VERIFIED RETURN</div>
                                <div className="returned-grid">
                                    <div className="returned-img-container">
                                        <img src={item.main_picture || '/assets/logo.png'} alt={item.item_type} />
                                    </div>
                                    <div className="returned-info">
                                        <h3>{item.item_type}</h3>
                                        <div className="meta-grid">
                                            <div className="meta-item">
                                                <label>Category</label>
                                                <span>{item.category}</span>
                                            </div>
                                            <div className="meta-item">
                                                <label>Location Found</label>
                                                <span>{item.found_location}</span>
                                            </div>
                                            <div className="meta-item">
                                                <label>Date Found</label>
                                                <span>{new Date(item.found_datetime).toLocaleDateString()}</span>
                                            </div>
                                            <div className="meta-item">
                                                <label>Resolution</label>
                                                <span className="success-text">Returned to Owner</span>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        ))}
                        {items.length === 0 && (
                            <div className="empty-state">
                                <p>No completed returns to display yet.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReturnedItems;
