import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Card from '../../components/UI/Card';
import './ClaimForm.css';

const ClaimForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useState({
        description: '',
        declared_value: '',
        receipt_proof: ''
    });

    useEffect(() => {
        const fetchItem = async () => {
            try {
                const response = await api.get('/items/found');
                const foundItem = (response.data.data.items || []).find(i => i.id === parseInt(id));
                if (foundItem) setItem(foundItem);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        };
        fetchItem();
    }, [id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        try {
            await api.post('/claims/submit', {
                found_item_id: item.id,
                ...formData,
                declared_value: parseFloat(formData.declared_value)
            });
            navigate('/claim-confirmation', { state: { itemType: item.item_type } });
        } catch (err) {
            alert(err.response?.data?.message || 'Failed to submit claim.');
            setSubmitting(false);
        }
    };

    if (loading) return (
        <div className="container" style={{ padding: 'var(--space-4) 0', textAlign: 'center' }}>
            <p>Loading item details...</p>
        </div>
    );

    if (!item) return (
        <div className="container" style={{ padding: 'var(--space-4) 0', textAlign: 'center' }}>
            <p>Item not found.</p>
            <Button variant="neutral" onClick={() => navigate('/lost-items')}>Back to Discovery</Button>
        </div>
    );

    return (
        <div className="container claim-form-page">
            <div className="page-header">
                <h1 className="page-title">Submit a Claim</h1>
                <p className="auth-subtitle">Provide details to verify your ownership of the {item.item_type}</p>
            </div>

            <div className="claim-form-layout">
                <Card className="claim-item-summary" hover={false}>
                    <div className="summary-image">
                        <img src={item.image_url || 'https://via.placeholder.com/300x200?text=No+Image'} alt={item.item_type} />
                    </div>
                    <div className="summary-details">
                        <h3>{item.item_type}</h3>
                        <p>Found at: <span>{item.found_location}</span></p>
                        <p>Date: <span>{new Date(item.found_datetime || item.created_at).toLocaleDateString()}</span></p>
                    </div>
                </Card>

                <Card className="claim-form-card" hover={false}>
                    <form onSubmit={handleSubmit} className="auth-form">
                        <Input
                            label="Proof of Ownership"
                            type="textarea"
                            placeholder="Describe specific marks, contents, or details only the owner would know..."
                            value={formData.description}
                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                            required
                            style={{ minHeight: '120px' }}
                        />

                        <Input
                            label="Estimated Value ($)"
                            type="number"
                            step="0.01"
                            placeholder="0.00"
                            value={formData.declared_value}
                            onChange={(e) => setFormData({ ...formData, declared_value: e.target.value })}
                            required
                        />

                        <Input
                            label="Proof / Receipt URL (Optional)"
                            type="text"
                            placeholder="Link to a photo or digital receipt"
                            value={formData.receipt_proof}
                            onChange={(e) => setFormData({ ...formData, receipt_proof: e.target.value })}
                        />

                        <div className="claim-form-footer">
                            <p className="claim-disclaimer">
                                By submitting this claim, you certify that the information provided is accurate and you are the rightful owner of this item.
                            </p>
                            <div className="claim-actions">
                                <Button type="submit" variant="primary" disabled={submitting} style={{ flex: 1 }}>
                                    {submitting ? 'Submitting...' : 'Confirm & Submit Claim'}
                                </Button>
                                <Button type="button" variant="neutral" onClick={() => navigate(-1)}>
                                    Cancel
                                </Button>
                            </div>
                        </div>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ClaimForm;
