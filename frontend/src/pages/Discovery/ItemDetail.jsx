import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
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
        const fetchItem = async () => {
            try {
                setLoading(true);
                const response = await api.get('/items/found', { params: { limit: 100 } });
                const items = response.data.data.items || [];
                const foundItem = items.find(i => i.id === parseInt(id));

                if (foundItem) {
                    setItem(foundItem);
                } else {
                    setError('Item not found.');
                }
            } catch (err) {
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

    if (loading) return (
        <div className="container" style={{ padding: 'var(--space-4) 0', textAlign: 'center' }}>
            <p>Loading item details...</p>
        </div>
    );
    
    if (error) return (
        <div className="container" style={{ padding: 'var(--space-4) 0', textAlign: 'center' }}>
            <div className="error-message" style={{ color: 'var(--danger)' }}>{error}</div>
            <Button variant="neutral" style={{ marginTop: 'var(--space-2)' }} onClick={() => navigate('/lost-items')}>
                Back to List
            </Button>
        </div>
    );

    if (!item) return null;

    return (
        <div className="container item-detail-page">
            <div className="back-link" onClick={() => navigate(-1)}>
                <span>←</span> Back to Discovery
            </div>

            <div className="item-detail-container">
                <div className="item-detail-image-section">
                    <img 
                        src={item.image_url || 'https://via.placeholder.com/800x600?text=No+Image'} 
                        alt={item.item_type} 
                    />
                </div>

                <div className="item-detail-info-section">
                    <div className="item-header">
                        <span className="item-category-badge">{item.category}</span>
                        <h1 className="item-detail-title">{item.item_type}</h1>
                    </div>

                    <div className="info-grid">
                        <div>
                            <p className="info-item-label">Color</p>
                            <p className="info-item-value">{item.color}</p>
                        </div>
                        <div>
                            <p className="info-item-label">Brand</p>
                            <p className="info-item-value">{item.brand || 'N/A'}</p>
                        </div>
                        <div>
                            <p className="info-item-label">Location Found</p>
                            <p className="info-item-value">{item.found_location}</p>
                        </div>
                        <div>
                            <p className="info-item-label">Date Found</p>
                            <p className="info-item-value">{new Date(item.found_datetime || item.created_at).toLocaleDateString()}</p>
                        </div>
                    </div>

                    <div className="info-description-section">
                        <h3 className="description-label">Description</h3>
                        <p className="description-text">
                            {item.public_description || item.full_description || 'No detailed description available for this item.'}
                        </p>
                    </div>

                    <div className="claim-section">
                        {!showClaimForm ? (
                            <Button 
                                variant="primary" 
                                style={{ padding: '14px 40px' }}
                                onClick={() => setShowClaimForm(true)}
                            >
                                Claim This Item
                            </Button>
                        ) : (
                            <div className="claim-form-container">
                                <h3 className="claim-form-title">Submit Claim</h3>
                                <form onSubmit={handleClaimSubmit}>
                                    <Input
                                        label="Proof Description"
                                        placeholder="How can we verify this item belongs to you?"
                                        type="textarea"
                                        required
                                        value={claimData.description}
                                        onChange={e => setClaimData({ ...claimData, description: e.target.value })}
                                        style={{ minHeight: '100px' }}
                                    />
                                    
                                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-2)' }}>
                                        <Input
                                            label="Declared Value ($)"
                                            type="number"
                                            step="0.01"
                                            required
                                            value={claimData.declared_value}
                                            onChange={e => setClaimData({ ...claimData, declared_value: e.target.value })}
                                        />
                                        <Input
                                            label="Receipt or Proof URL"
                                            type="text"
                                            placeholder="Optional URL to proof"
                                            value={claimData.receipt_proof}
                                            onChange={e => setClaimData({ ...claimData, receipt_proof: e.target.value })}
                                        />
                                    </div>

                                    <div className="claim-form-actions">
                                        <Button type="submit" variant="primary">Submit Claim</Button>
                                        <Button type="button" variant="neutral" onClick={() => setShowClaimForm(false)}>
                                            Cancel
                                        </Button>
                                    </div>
                                </form>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ItemDetail;

