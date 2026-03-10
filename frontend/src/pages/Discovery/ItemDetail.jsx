import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './ItemDetail.css';

const ItemDetail = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const [showClaimForm, setShowClaimForm] = useState(false);
    const [claimData, setClaimData] = useState({
        description: '',
        declared_value: '',
        receipt_proof: ''
    });

    useEffect(() => {
        // Since we don't have a single item endpoint in spec yet, we'll fetch list and find, or assume a new endpoint
        const fetchItem = async () => {
            try {
                setLoading(true);
                // Assuming we could pass full item via state, or we fetch from search 
                // For robustness, simulating a fetch by getting found items and filtering
                const response = await api.get('/items/found', { params: { limit: 100 } });
                const items = response.data.data.items || [];
                const foundItem = items.find(i => i.id === parseInt(id));

                if (foundItem) {
                    setItem(foundItem);
                } else {
                    setError('Item not found.');
                }
            } catch (err) {
                // Ignore err to fix lint or log it
                console.error(err);
                setError('Failed to fetch item details.');
            } finally {
                setLoading(false);
            }
        };
        fetchItem();
    }, [id]);

    const handleClaimSubmit = async (e) => {
        e.preventDefault();
        try {
            await api.post('/claims/submit', {
                found_item_id: item.id,
                ...claimData,
                declared_value: parseFloat(claimData.declared_value)
            });
            alert('Claim submitted successfully!');
            navigate('/lost-items');
        } catch (err) {
            alert(err.response?.data?.message || 'Failed to submit claim.');
        }
    };

    if (loading) return <div className="loading-spinner">Loading...</div>;
    if (error) return <div className="error-message">{error}</div>;
    if (!item) return null;

    return (
        <div className="item-detail-page">
            <button className="back-btn" onClick={() => navigate(-1)}>← Back</button>

            <div className="item-detail-container glass-panel">
                <div className="item-detail-image">
                    <img src={item.image_url || 'https://via.placeholder.com/600x400?text=No+Image'} alt={item.item_type} />
                </div>

                <div className="item-detail-info">
                    <h2>{item.item_type}</h2>
                    <div className="info-grid">
                        <div className="info-item"><span>Category:</span> {item.category}</div>
                        <div className="info-item"><span>Color:</span> {item.color}</div>
                        <div className="info-item"><span>Brand:</span> {item.brand || 'N/A'}</div>
                        <div className="info-item"><span>Location Found:</span> {item.found_location}</div>
                        <div className="info-item"><span>Date Found:</span> {new Date(item.found_datetime || item.created_at).toLocaleDateString()}</div>
                    </div>
                    <div className="info-description">
                        <h3>Description</h3>
                        <p>{item.public_description || item.full_description || 'No description provided.'}</p>
                    </div>

                    {!showClaimForm ? (
                        <button className="claim-btn" onClick={() => setShowClaimForm(true)}>
                            Claim This Item
                        </button>
                    ) : (
                        <form className="claim-form" onSubmit={handleClaimSubmit}>
                            <h3>Submit Claim</h3>
                            <div className="form-group">
                                <label>Proof Description (How do we know it's yours?)</label>
                                <textarea
                                    required
                                    className="auth-input"
                                    value={claimData.description}
                                    onChange={e => setClaimData({ ...claimData, description: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Declared Value ($)</label>
                                <input
                                    type="number"
                                    step="0.01"
                                    required
                                    className="auth-input"
                                    value={claimData.declared_value}
                                    onChange={e => setClaimData({ ...claimData, declared_value: e.target.value })}
                                />
                            </div>
                            <div className="form-group">
                                <label>Receipt or Proof URL</label>
                                <input
                                    type="text"
                                    required
                                    className="auth-input"
                                    value={claimData.receipt_proof}
                                    onChange={e => setClaimData({ ...claimData, receipt_proof: e.target.value })}
                                />
                            </div>
                            <div className="form-actions">
                                <button type="submit" className="auth-primary-btn">Submit Claim</button>
                                <button type="button" className="auth-secondary-btn" onClick={() => setShowClaimForm(false)}>Cancel</button>
                            </div>
                        </form>
                    )}
                </div>
            </div>
        </div>
    );
};

export default ItemDetail;

