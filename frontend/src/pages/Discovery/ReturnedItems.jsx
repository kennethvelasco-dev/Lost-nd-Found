import React, { useState, useEffect, useCallback } from 'react';
import ItemCard from '../../components/UI/ItemCard';
import SearchBar from '../../components/UI/SearchBar';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';

const ReturnedItems = () => {
    const { loading, error, data, request } = useHttp();
    const [search, setSearch] = useState('');
    const [filter, setFilter] = useState('');

    const fetchItems = useCallback(async (q = '', f = '') => {
        const params = { status: 'returned' };
        if (q) params.query = q;
        if (f) params.sort = f;
        
        try {
            await request({ url: '/items/returned', params });
        } catch (err) {
            console.error(err);
        }
    }, [request]);

    useEffect(() => {
        fetchItems(search, filter);
    }, [search, filter, fetchItems]);

    const items = data?.items || (Array.isArray(data) ? data : []);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Successful Returns</h1>
                    <p className="auth-subtitle">A collection of items that found their way back home.</p>
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
                    emptyMessage="No successful returns matching your search found."
                    onRetry={() => fetchItems(search, filter)}
                >
                    <div className="grid-layout">
                        {items.map(item => (
                            <ItemCard key={item.id} item={item} type="returned" />
                        ))}
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default ReturnedItems;
