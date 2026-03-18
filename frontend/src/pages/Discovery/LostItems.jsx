import React, { useState, useEffect } from 'react';
import ItemCard from '../../components/UI/ItemCard';
import SearchBar from '../../components/UI/SearchBar';
import api from '../../services/api';

const LostItems = () => {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');

    const fetchItems = async (query = '', sort = '') => {
        try {
            setLoading(true);
            let endpoint = '/items/found';
            const params = { status: 'found' };

            if (query) {
                endpoint = '/items/search';
                params.query = query;
            }

            if (sort) {
                params.sort = sort;
            }

            const response = await api.get(endpoint, { params });
            setItems(response.data.data.items || response.data.data || []);
            setError(null);
        } catch (err) {
            setError('Failed to fetch items. Please try again later.');
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchItems(search, filter);
    }, [search, filter]);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Lost & Found Directory</h1>
                    <p className="auth-subtitle">Search for items reported across campus.</p>
                    <div className="title-underline"></div>
                </div>

                <SearchBar 
                    onSearch={(q) => setSearch(q)}
                    onFilter={(f) => setFilter(f)}
                />

                {loading ? (
                    <div className="loading-container" style={{ textAlign: 'center', padding: '100px' }}>
                        <p style={{ color: 'var(--text-muted)', fontSize: '1.2rem' }}>Scanning for matching items...</p>
                    </div>
                ) : error ? (
                    <div className="error-message" style={{ textAlign: 'center', padding: '60px' }}>
                        {error}
                    </div>
                ) : (
                    <div className="grid-layout">
                        {items.map(item => (
                            <ItemCard key={item.id} item={item} />
                        ))}
                        {items.length === 0 && (
                            <div className="no-items" style={{ gridColumn: '1/-1', textAlign: 'center', padding: '100px' }}>
                                <p style={{ color: 'var(--text-muted)' }}>No items found matching your search.</p>
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default LostItems;
