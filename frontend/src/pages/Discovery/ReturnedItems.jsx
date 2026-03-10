import React, { useState, useEffect } from 'react';
import ItemCard from '../../components/UI/ItemCard';
import SearchBar from '../../components/UI/SearchBar';
import api from '../../services/api';

const ReturnedItems = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchItems = async (query = '') => {
        try {
            setLoading(true);
            // For now, we use the same items/found endpoint but we'll eventually filter by 'returned' status
            // Once the backend supports a specific returned items endpoint, we will update this.
            // Currently, 'returned' items are just those with a completed handover/claim status.
            const response = await api.get('/items/found', {
                params: {
                    query,
                    status: 'completed' // Assuming the backend filters by status
                }
            });
            setItems(response.data.data.items || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch returned items.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    return (
        <div className="returned-items-page">
            <SearchBar
                onSearch={(q) => fetchItems(q)}
                onFilter={(f) => fetchItems('', f)}
            />

            {loading ? (
                <div className="loading-spinner">Loading...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : (
                <div className="items-grid">
                    {items.map(item => (
                        <ItemCard key={item.id} item={item} isReturned={true} />
                    ))}
                    {items.length === 0 && <p className="no-items">No returned items to display.</p>}
                </div>
            )}
        </div>
    );
};

export default ReturnedItems;

