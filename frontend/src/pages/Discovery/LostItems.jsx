import React, { useState, useEffect } from 'react';
import ItemCard from '../../components/UI/ItemCard';
import SearchBar from '../../components/UI/SearchBar';
import api from '../../services/api';

const LostItems = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);

    const fetchItems = async (query = '', filter = '') => {
        try {
            setLoading(true);
            let endpoint = '/items/found';
            const params = {};

            if (query) {
                endpoint = '/items/search';
                params.query = query;
            }

            if (filter) {
                params.sort = filter; // Backend sort/filter logic
            }

            const response = await api.get(endpoint, { params });
            setItems(response.data.data.items || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch items. Please try again later.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems();
    }, []);

    return (
        <div className="lost-items-page">
            <SearchBar
                onSearch={(q) => fetchItems(q)}
                onFilter={(f) => fetchItems('', f)}
            />

            {loading ? (
                <div className="loading-spinner">Loading items...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : (
                <div className="items-grid">
                    {items.map(item => (
                        <ItemCard key={item.id} item={item} />
                    ))}
                    {items.length === 0 && <p className="no-items">No items found.</p>}
                </div>
            )}
        </div>
    );
};

export default LostItems;

