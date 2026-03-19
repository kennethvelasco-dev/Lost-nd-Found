```javascript
import React, { useState, useEffect } from 'react';
import Card from '../../components/UI/Card';
import SearchBar from '../../components/UI/SearchBar';
import api from '../../services/api';

import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';

const ReturnedItems = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const { loading, error, data, request } = useHttp();

    useEffect(() => {
        fetchItems();
    }, []);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Verified Handovers</h1>
                    <p className="auth-subtitle">Successful reunions across our campus community.</p>
                    <div className="title-underline"></div>
                </div>

                <SearchBar onSearch={(q) => fetchItems(q)} />

                {loading ? (
                    <div className="loading-state" style={{ textAlign: 'center', padding: '100px' }}>Searching history...</div>
                ) : (
                    <div className="returned-list" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)', marginTop: 'var(--space-4)' }}>
                        {items.map(item => (
                            <Card key={item.id} className="returned-item-card">
                                <div style={{ display: 'flex', gap: 'var(--space-4)', alignItems: 'center' }}>
                                    <div className="returned-img-container" style={{ width: '150px', height: '150px', borderRadius: 'var(--radius-md)', overflow: 'hidden', boxShadow: 'var(--nm-inset)' }}>
                                        <img src={item.main_picture || '/assets/logo.png'} alt={item.item_type} style={{ width: '100%', height: '100%', objectFit: 'cover' }} />
                                    </div>
                                    <div className="returned-info" style={{ flex: 1 }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                            <h3 style={{ color: 'var(--primary)', fontSize: '1.5rem', margin: 0 }}>{item.item_type}</h3>
                                            <span style={{ background: '#dcfce7', color: '#166534', padding: '4px 12px', borderRadius: '20px', fontSize: '11px', fontWeight: 800 }}>VERIFIED</span>
                                        </div>
                                        <div className="meta-grid" style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: 'var(--space-3)', marginTop: 'var(--space-3)' }}>
                                            <div className="meta-item">
                                                <label style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Resolution</label>
                                                <p style={{ fontWeight: 600 }}>Returned to Owner</p>
                                            </div>
                                            <div className="meta-item">
                                                <label style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Item ID</label>
                                                <p style={{ fontWeight: 600 }}>#{item.id}</p>
                                            </div>
                                            <div className="meta-item">
                                                <label style={{ fontSize: '10px', color: 'var(--text-muted)', textTransform: 'uppercase' }}>Date Resolved</label>
                                                <p style={{ fontWeight: 600 }}>{new Date(item.found_datetime).toLocaleDateString()}</p>
                                            </div>
                                        </div>
                                    </div>
                                </div>
                            </Card>
                        ))}
                    </div>
                )}
            </div>
        </div>
    );
};

export default ReturnedItems;
