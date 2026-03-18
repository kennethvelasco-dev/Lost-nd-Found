import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Card from '../../components/UI/Card';
import './ReportItem.css';

const CATEGORIES = ['Personal Items', 'Electronics', 'Books & Documents', 'Keys & Cards', 'Clothing', 'Other'];
const COLORS = ['Black', 'White', 'Silver', 'Gold', 'Red', 'Blue', 'Green', 'Yellow', 'Brown', 'Other'];

const ReportItem = () => {
    const [formData, setFormData] = useState({
        item_type: '',
        category: 'Personal Items',
        color: 'Black',
        last_seen_location: '',
        last_seen_datetime: '',
        public_description: '',
        private_details: ''
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await api.post('/items/lost', formData);
            navigate('/confirmation', { 
                state: { title: 'Report Submitted!', message: 'We will notify you if a matching item is found.' } 
            });
        } catch (err) {
            setError(err.response?.data?.message || 'An error occurred during submission.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div className="container report-container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Report Lost Item</h1>
                    <div className="title-underline"></div>
                </div>

                <Card className="report-card">
                    <p className="auth-subtitle" style={{ textAlign: 'center', marginBottom: 'var(--space-4)' }}>
                        Precision reports lead to faster reunions. Please be as descriptive as possible.
                    </p>

                    {error && <div className="error-message">{error}</div>}

                    <form className="report-form" onSubmit={handleSubmit}>
                        <div className="form-row">
                            <Input
                                label="What did you lose?"
                                placeholder="e.g. iPhone 13, Leather Wallet"
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
                                placeholder="e.g. Student Center Lounge"
                                value={formData.last_seen_location}
                                onChange={(e) => setFormData({ ...formData, last_seen_location: e.target.value })}
                                required
                            />
                        </div>

                        <div className="form-row">
                            <Input
                                label="Last Seen Date/Time"
                                type="datetime-local"
                                value={formData.last_seen_datetime}
                                onChange={(e) => setFormData({ ...formData, last_seen_datetime: e.target.value })}
                                required
                            />
                        </div>

                        <div className="form-group">
                            <label className="form-label">Public Description</label>
                            <textarea
                                className="form-textarea"
                                placeholder="Visible to anyone searching. Mention brand, visible damage, or stickers..."
                                value={formData.public_description}
                                onChange={(e) => setFormData({ ...formData, public_description: e.target.value })}
                                required
                            ></textarea>
                        </div>

                        <div className="form-group">
                            <label className="form-label">Private Details (Ownership Proof)</label>
                            <textarea
                                className="form-textarea"
                                placeholder="NOT visible to other users. Contents of wallet, serial numbers, wallpapers..."
                                value={formData.private_details}
                                onChange={(e) => setFormData({ ...formData, private_details: e.target.value })}
                            ></textarea>
                        </div>

                        <Button type="submit" variant="primary" disabled={loading} style={{ width: '100%', marginTop: 'var(--space-3)' }}>
                            {loading ? 'Submitting Report...' : 'Publish Lost Report'}
                        </Button>
                    </form>
                </Card>
            </div>
        </div>
    );
};

export default ReportItem;
