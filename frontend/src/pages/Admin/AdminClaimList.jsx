import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import './AdminClaimList.css';

const AdminClaimList = () => {
    const [claims, setClaims] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [filter, setFilter] = useState('all');
    const [search, setSearch] = useState('');
    const navigate = useNavigate();

    const fetchAllClaims = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/claims');
            setClaims(response.data.data.claims || response.data.data || []);
            setError(null);
        } catch (err) {
            if (err.response?.status === 403 || err.response?.status === 401) {
                navigate('/login');
            } else {
                setError('Failed to fetch claims list.');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchAllClaims();
    }, [navigate]);

    const filteredClaims = claims.filter(c => {
        const matchesFilter = filter === 'all' || c.status === filter;
        const matchesSearch = (c.claimant_email || '').toLowerCase().includes(search.toLowerCase()) || 
                             (c.item_name || '').toLowerCase().includes(search.toLowerCase());
        return matchesFilter && matchesSearch;
    });

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Review Claim Requests</h1>
                    <p className="auth-subtitle">Verify ownership for pending item claims</p>
                    <div className="title-underline"></div>
                </div>

                <Card className="filter-section" hover={false}>
                    <div className="filter-controls">
                        <div className="status-filters">
                            {['all', 'pending', 'approved', 'rejected', 'completed'].map(s => (
                                <button 
                                    key={s} 
                                    className={`filter-btn ${filter === s ? 'active' : ''}`}
                                    onClick={() => setFilter(s)}
                                >
                                    {s.charAt(0).toUpperCase() + s.slice(1)}
                                </button>
                            ))}
                        </div>
                        <div className="search-control">
                            <input 
                                type="text" 
                                placeholder="Search by email or item..." 
                                value={search}
                                onChange={(e) => setSearch(e.target.value)}
                                className="admin-search-input"
                            />
                        </div>
                    </div>
                </Card>

                {loading ? (
                    <div style={{ textAlign: 'center', padding: '40px' }}><p>Loading claims...</p></div>
                ) : filteredClaims.length === 0 ? (
                    <Card style={{ textAlign: 'center', padding: '40px' }}><p>No claims found matching your criteria.</p></Card>
                ) : (
                    <div className="admin-table-container">
                        <table className="admin-table">
                            <thead>
                                <tr>
                                    <th>ID</th>
                                    <th>Item</th>
                                    <th>Claimant</th>
                                    <th>Status</th>
                                    <th>Match</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredClaims.map(claim => (
                                    <tr key={claim.id}>
                                        <td>#{claim.id}</td>
                                        <td className="item-cell">{claim.item_name || `ID: ${claim.found_item_id}`}</td>
                                        <td>{claim.claimant_email}</td>
                                        <td>
                                            <span className={`admin-status-badge ${claim.status}`}>
                                                {claim.status}
                                            </span>
                                        </td>
                                        <td>{claim.verification_score || claim.score || 'N/A'}%</td>
                                        <td>
                                            <Button 
                                                variant="secondary" 
                                                size="sm" 
                                                onClick={() => navigate(`/admin/dashboard`)}
                                            >
                                                Review
                                            </Button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
};

export default AdminClaimList;
