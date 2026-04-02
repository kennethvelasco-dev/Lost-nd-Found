import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import FileUpload from '../../components/UI/FileUpload';
import { DraftService } from '../../services/DraftService';

const COLORS = ['Black', 'White', 'Silver', 'Gold', 'Red', 'Blue', 'Green', 'Yellow', 'Brown', 'Other'];

const ClaimForm = () => {
    const { id } = useParams();
    const navigate = useNavigate();
    const { loading, error, data, request } = useHttp();
    const [submitting, setSubmitting] = useState(false);
    const [submitError, setSubmitError] = useState('');
    const [formData, setFormData] = useState({
        color: 'Black',
        description: '',
        lost_location: '',
        lost_datetime: '',
        images: []
    });
    const [otherColor, setOtherColor] = useState('');
    const [loadingDraft, setLoadingDraft] = useState(true);

    // Fetch Item details
    useEffect(() => {
        request({ url: `/items/${id}` });
    }, [id, request]);

    const item = data?.item || data;

    // Initial draft load from IndexedDB
    useEffect(() => {
        const load = async () => {
            const draft = await DraftService.getDraft(`claim_draft_${id}`);
            if (draft) setFormData(prev => ({ ...prev, ...draft }));
            setLoadingDraft(false);
        };
        load();
    }, [id]);

    // Save draft on change
    useEffect(() => {
        if (!loadingDraft) {
            DraftService.saveDraft(`claim_draft_${id}`, formData);
        }
    }, [formData, loadingDraft, id]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setSubmitting(true);
        setSubmitError('');

        const finalColor = formData.color === 'Other' && otherColor ? otherColor : formData.color;

        try {
            const claimData = {
                found_item_id: item.id,
                description: formData.description,
                lost_location: formData.lost_location,
                lost_datetime: formData.lost_datetime,
                declared_value: 0,
                color: finalColor,
                brand: formData.brand,
                category: item.category, // Pass the category through for verification indexing
                item_type: item.item_type
            };

            if (formData.images && formData.images.length > 0) {
                claimData.receipt_proof = formData.images[0];
                claimData.additional_proof_1 = formData.images[1] || '';
                claimData.additional_proof_2 = formData.images[2] || '';
            }

            await api.post('/claims/submit', claimData);
            await DraftService.deleteDraft(`claim_draft_${id}`);
            navigate('/confirmation', { 
                state: { 
                    title: 'Claim Submitted!', 
                    message: 'Our administration team will review your proof of ownership and contact you shortly.' 
                } 
            });
        } catch (err) {
            console.error('Submission Error:', err.response?.data || err);
            // Better error extraction for the user
            const backendError = err.response?.data?.error || err.response?.data?.message;
            const msg = typeof backendError === 'string' ? backendError : 'Submission failed. Please try again.';
            setSubmitError(msg);
        } finally {
            setSubmitting(false);
        }
    };

    return (
        <div className="page-container">
            <div className="container" style={{ maxWidth: '800px' }}>
                <StatusState 
                    loading={loading} 
                    error={error} 
                    onRetry={() => request({ url: `/items/${id}` })}
                >
                    {item && (
                        <>
                            <div className="pretty-header">
                                <h1 className="pretty-title">Ownership Verification</h1>
                                <p className="auth-subtitle">Provide details to verify this item belongs to you.</p>
                                <div className="title-underline"></div>
                            </div>

                            <Card className="claim-form-card">
                                <div style={{ marginBottom: 'var(--space-4)', borderBottom: '1px solid rgba(0,0,0,0.05)', paddingBottom: 'var(--space-3)' }}>
                                    <h2 style={{ color: 'var(--primary)', margin: 0, fontSize: '1.4rem' }}>
                                        Verification for: {item.item_type}
                                    </h2>
                                    <p style={{ color: 'var(--text-secondary)', fontSize: '13px', margin: '4px 0 0 0' }}>Category: {item.category}</p>
                                </div>
                                
                                <form onSubmit={handleSubmit} className="report-form" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-4)' }}>
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
                                            placeholder="e.g. Neon Green with stripes"
                                            value={otherColor}
                                            onChange={(e) => setOtherColor(e.target.value)}
                                            required
                                        />
                                    )}

                                    <div className="form-group">
                                        <Input
                                            label="Item Brand (if any)"
                                            placeholder="e.g. Apple, Nike, etc."
                                            value={formData.brand || ''}
                                            onChange={(e) => setFormData({ ...formData, brand: e.target.value })}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">When did you lose it?</label>
                                        <input 
                                            type="datetime-local" 
                                            className="form-input"
                                            value={formData.lost_datetime}
                                            onChange={(e) => setFormData({ ...formData, lost_datetime: e.target.value })}
                                            required
                                            style={{ width: '100%', padding: '12px', border: '1px solid rgba(0,0,0,0.1)', borderRadius: 'var(--radius-sm)' }}
                                        />
                                    </div>

                                    <div className="form-group">
                                        <Input
                                            label="Where exactly did you last have it?"
                                            placeholder="e.g. Near the main building lobby"
                                            value={formData.lost_location}
                                            onChange={(e) => setFormData({ ...formData, lost_location: e.target.value })}
                                            required
                                        />
                                    </div>

                                    <div className="form-group">
                                        <label className="form-label">Private Identification Details</label>
                                        <textarea 
                                            className="form-textarea"
                                            placeholder="Describe unique markings, serial numbers, case details, or contents..."
                                            value={formData.description}
                                            onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                            required
                                            style={{ minHeight: '140px' }}
                                        ></textarea>
                                        <p style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '6px' }}>
                                            💡 Be as specific as possible. This information is private and only seen by admins.
                                        </p>
                                    </div>

                                    <div className="form-group">
                                        <FileUpload 
                                            label="Ownership Evidence (Photos/Receipts)"
                                            initialFiles={formData.images || []}
                                            onFilesChange={(files) => setFormData({ ...formData, images: files })}
                                        />
                                    </div>

                                    {submitError && <p style={{ color: 'var(--danger)', fontSize: '14px' }}>{submitError}</p>}

                                    <Button type="submit" variant="primary" disabled={submitting} style={{ width: '100%', padding: '16px', marginTop: 'var(--space-2)' }}>
                                        {submitting ? 'Verifying & Submitting...' : 'Submit Claim Request'}
                                    </Button>
                                </form>
                            </Card>
                        </>
                    )}
                </StatusState>
            </div>
        </div>
    );
};

export default ClaimForm;
