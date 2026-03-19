import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Card from '../../components/UI/Card';
import FileUpload from '../../components/UI/FileUpload';

const CATEGORIES = ['Personal Items', 'Electronics', 'Books & Documents', 'Keys & Cards', 'Clothing', 'Other'];
const COLORS = ['Black', 'White', 'Silver', 'Gold', 'Red', 'Blue', 'Green', 'Yellow', 'Brown', 'Other'];

import { DraftService } from '../../services/DraftService';

const ReportItem = () => {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        item_type: '',
        category: 'Personal Items',
        color: 'Black',
        last_seen_location: '',
        last_seen_datetime: '',
        public_description: '',
        private_details: '',
        images: []
    });
    const [otherCategory, setOtherCategory] = useState('');
    const [otherColor, setOtherColor] = useState('');
    const [loadingDraft, setLoadingDraft] = useState(true);

    // Initial draft load from IndexedDB
    useEffect(() => {
        const load = async () => {
            const draft = await DraftService.getDraft('report_draft');
            if (draft) setFormData(prev => ({ ...prev, ...draft }));
            setLoadingDraft(false);
        };
        load();
    }, []);

    // Save draft to IndexedDB on change
    useEffect(() => {
        if (!loadingDraft) {
            DraftService.saveDraft('report_draft', formData);
        }
    }, [formData, loadingDraft]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        const submissionData = { ...formData };
        if (formData.category === 'Other' && otherCategory) {
            submissionData.category = otherCategory;
        }
        if (formData.color === 'Other' && otherColor) {
            submissionData.color = otherColor;
        }

        // Map multi-images to backend columns
        if (Array.isArray(formData.images)) {
            submissionData.main_picture = formData.images[0] || '';
            submissionData.additional_picture_1 = formData.images[1] || '';
            submissionData.additional_picture_2 = formData.images[2] || '';
        }

        try {
            await api.post('/items/lost', submissionData);
            await DraftService.deleteDraft('report_draft'); // Clear draft
            navigate('/confirmation', { 
                state: { 
                    title: 'Report Submitted!', 
                    message: 'Your report is now pending administrator approval. You can track its status in "My Activities".' 
                } 
            });
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred during submission.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div className="container" style={{ maxWidth: '900px' }}>
                <div className="pretty-header">
                    <h1 className="pretty-title">Report Lost Item</h1>
                    <p className="auth-subtitle">Help the community find your lost belongings.</p>
                    <div className="title-underline"></div>
                </div>

                <Card>
                    <form className="report-form" onSubmit={handleSubmit} style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                        <div className="form-row">
                            <Input
                                label="Item Name"
                                placeholder="e.g. Blue HydroFlask"
                                value={formData.item_type}
                                onChange={(e) => setFormData({ ...formData, item_type: e.target.value })}
                                required
                            />
                            <div className="form-group">
                                <label className="form-label">Category</label>
                                <select 
                                    className="form-select"
                                    value={formData.category}
                                    onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                                >
                                    {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>
                        </div>

                        {formData.category === 'Other' && (
                            <Input
                                label="Specify Category"
                                placeholder="What kind of item is it?"
                                value={otherCategory}
                                onChange={(e) => setOtherCategory(e.target.value)}
                                required
                            />
                        )}

                        <div className="form-row">
                            <div className="form-group">
                                <label className="form-label">Primary Color</label>
                                <select 
                                    className="form-select"
                                    value={formData.color}
                                    onChange={(e) => setFormData({ ...formData, color: e.target.value })}
                                >
                                    {COLORS.map(c => <option key={c} value={c}>{c}</option>)}
                                </select>
                            </div>
                            <Input
                                label="Last Seen Location"
                                placeholder="e.g. Gym Locker Room"
                                value={formData.last_seen_location}
                                onChange={(e) => setFormData({ ...formData, last_seen_location: e.target.value })}
                                required
                            />
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

                        <div className="form-row">
                            <div style={{ flex: 1 }}>
                                <Input
                                    label="Last Seen Date/Time"
                                    type="datetime-local"
                                    value={formData.last_seen_datetime}
                                    onChange={(e) => setFormData({ ...formData, last_seen_datetime: e.target.value })}
                                    required
                                />
                            </div>
                            <div style={{ flex: 1 }}>
                                <FileUpload 
                                    label="Evidence Photos"
                                    initialFiles={formData.images || []}
                                    onFilesChange={(files) => setFormData({ ...formData, images: files })}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Public Description</label>
                            <textarea
                                className="form-textarea"
                                placeholder="Mention visible marks, stickers, or case details..."
                                value={formData.public_description}
                                onChange={(e) => setFormData({ ...formData, public_description: e.target.value })}
                                required
                                style={{ minHeight: '100px' }}
                            ></textarea>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Private Ownership Details</label>
                            <textarea
                                className="form-textarea"
                                placeholder="Mention contents or unique serials NOT visible to others..."
                                value={formData.private_details}
                                onChange={(e) => setFormData({ ...formData, private_details: e.target.value })}
                                required
                                style={{ minHeight: '80px' }}
                            ></textarea>
                        </div>

                        {error && <p style={{ color: 'var(--danger)', fontSize: '14px' }}>{error}</p>}

                        <Button type="submit" variant="primary" disabled={loading} style={{ width: '100%', padding: '16px' }}>
                            {loading ? 'Publishing...' : 'Submit Lost Item Report'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ReportItem;
