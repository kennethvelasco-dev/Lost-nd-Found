import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import FileUpload from '../../components/UI/FileUpload';

const COLORS = ['Black', 'White', 'Silver', 'Gold', 'Red', 'Blue', 'Green', 'Yellow', 'Brown', 'Other'];

const ClaimForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const [item, setItem] = useState(null);
    const [loading, setLoading] = useState(true);
    const [submitting, setSubmitting] = useState(false);
    const [formData, setFormData] = useLocalStorage(`claim_draft_${id}`, {
        color: 'Black',
        description: '',
        images: [] // Changed from proof to images array
    });
    const [otherColor, setOtherColor] = useState('');

    useEffect(() => {
        const fetchItem = async () => {
            try {
                const response = await api.get(`/items/found/${id}`);
                setItem(response.data.data.item || response.data.data);
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

        const finalColor = formData.color === 'Other' && otherColor ? otherColor : formData.color;

        try {
            const claimData = {
                found_item_id: id,
                description: formData.description,
                declared_value: 0,
                color: finalColor
            };

            // Map images
            if (formData.images && formData.images.length > 0) {
                claimData.receipt_proof = formData.images[0];
                claimData.additional_proof_1 = formData.images[1] || '';
                claimData.additional_proof_2 = formData.images[2] || '';
            }

            await api.post('/claims', claimData);
            window.localStorage.removeItem(`claim_draft_${id}`); // Clear draft
            navigate('/confirmation', { 
                state: { title: 'Claim Submitted!', message: 'The administrator will review your claim and notify you soon.' } 
            });
        } catch (err) {
            console.error(err);
        } finally {
            setSubmitting(false);
        }
    };

    if (loading) return <div className="page-container"><p>Loading item details...</p></div>;

    return (
        <div className="page-container">
            <div className="container" style={{ maxWidth: '800px' }}>
                <div className="pretty-header">
                    <h1 className="pretty-title">Submit Ownership Claim</h1>
                    <div className="title-underline"></div>
                </div>

                <Card className="claim-form-card">
                    <h2 style={{ color: 'var(--primary)', marginBottom: 'var(--space-3)' }}>
                        Claiming: {item?.item_type}
                    </h2>
                    
                    <form onSubmit={handleSubmit} className="report-form">
                        <div className="form-group">
                            <label className="form-label">Primary Color of your item</label>
                            <select 
                                className="form-select"
                                value={formData.color}
                                onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                            >
                                {COLORS.map(c => <option key={c} value={c}>{c}</option>)}
                            </select>
                        </div>

                        {formData.color === 'Other' && (
                            <Input
                                label="Specify Color"
                                placeholder="Describe the color(s)..."
                                value={otherColor}
                                onChange={(e) => setOtherColor(e.target.value)}
                                required
                            />
                        )}

                        <div className="form-group">
                            <label className="form-label">Detailed Description</label>
                            <textarea 
                                className="form-textarea"
                                placeholder="Describe unique features, markings, or contents..."
                                value={formData.description}
                                onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                required
                                style={{ minHeight: '120px' }}
                            ></textarea>
                        </div>

                        <div className="form-group">
                            <FileUpload 
                                label="Proof of Ownership Photos"
                                initialFiles={formData.images || []}
                                onFilesChange={(files) => setFormData({ ...formData, images: files })}
                            />
                        </div>

                        <Button type="submit" variant="primary" disabled={submitting} style={{ width: '100%', marginTop: 'var(--space-3)' }}>
                            {submitting ? 'Submitting Claim...' : 'Submit Claim'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ClaimForm;
