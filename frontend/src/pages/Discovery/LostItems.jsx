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
        <div className="container lost-items-page">
            <div className="page-header">
                <h1 className="page-title">Items Discovery</h1>
                <p className="auth-subtitle">Browse items found on campus or report a lost one</p>
            </div>

            <SearchBar
                onSearch={(q) => fetchItems(q)}
                onFilter={(f) => fetchItems('', f)}
            />

            {loading ? (
                <div className="loading-container">
                    <p>Searching for items...</p>
                </div>
            ) : error ? (
                <div className="error-message" style={{ textAlign: 'center', color: 'var(--danger)' }}>
                    {error}
                </div>
            ) : (
                <div className="items-grid">
                    {items.map(item => (
                        <ItemCard key={item.id} item={item} />
                    ))}
                    {items.length === 0 && (
                        <div className="no-items">
                            <p>No lost items found matching your search.</p>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default LostItems;

