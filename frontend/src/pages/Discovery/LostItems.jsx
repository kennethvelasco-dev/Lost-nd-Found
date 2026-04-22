import React, { useState, useEffect, useCallback } from 'react';
import ItemCard from '../../components/UI/ItemCard';
import SearchBar from '../../components/UI/SearchBar';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import { ItemGridSkeleton } from '../../components/common/Skeleton';

const LostItems = () => {
    const { loading, error, data, request } = useHttp();
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');
    const [items, setItems] = useState([]);

    const fetchItems = useCallback(async (q = '', f = '') => {
        const params = { status: 'lost' };
        if (q) params.query = q;
        if (f) params.sort = f;
        
        try {
            const payload = await request({ url: '/items/lost', params });
            if (payload) {
                const normalized = payload.items || (Array.isArray(payload) ? payload : []);
                setItems(normalized);
            }
        } catch (err) {
            console.error(err);
            setItems([]);
        }
    }, [request]);

    // When search/filter change, clear visible list immediately and refetch
    useEffect(() => {
        setItems([]);
        fetchItems(search, filter);
    }, [search, filter, fetchItems]);

    // Sync items if data updates independently
    useEffect(() => {
        if (!data) return;
        const normalized = data.items || (Array.isArray(data) ? data : []);
        setItems(normalized);
    }, [data]);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Lost & Found Directory</h1>
                    <p className="auth-subtitle">Help others find what they've lost accidentally.</p>
                    <div className="title-underline"></div>
                </div>

                <SearchBar 
                    onSearch={(q) => setSearch(q)}
                    onFilter={(f) => setFilter(f)}
                />

                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={items.length === 0}
                    emptyMessage="No items matching your search found."
                    onRetry={() => fetchItems(search, filter)}
                    skeleton={<ItemGridSkeleton count={6} />}
                >
                    <div className="grid-layout">
                        {items.map(item => (
                            <ItemCard key={item.id} item={item} type="lost" />
                        ))}
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default LostItems;
