import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Card from '../../components/UI/Card';

const AdminReturnItem = () => {
    const [formData, setFormData] = useState({
        item_id: '',
        owner_name: '',
        date_returned: new Date().toISOString().split('T')[0],
        handover_notes: ''
    });
    const [itemDetails, setItemDetails] = useState(null);
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    const adminUser = JSON.parse(localStorage.getItem('user') || '{}');

    const fetchItemDetails = async () => {
        if (!formData.item_id) return;
        setFetching(true);
        setError('');
        try {
            const response = await api.get(`/items/found/${formData.item_id}`);
            setItemDetails(response.data.data.item);
        } catch (err) {
            setError('Item not found. Please check the ID.');
            setItemDetails(null);
        } finally {
            setFetching(false);
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            navigate('/confirmation', { 
                state: { 
                    title: 'Return Logged!', 
                    message: `Item #${formData.item_id} (${itemDetails?.item_type}) has been marked as returned to ${formData.owner_name} by admin ${adminUser.username}.` 
                } 
            });
        } catch (err) {
            setError('Failed to log return.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Return Item to Owner</h1>
                    <div className="title-underline"></div>
                </div>

                <div className="admin-return-grid" style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 'var(--space-4)' }}>
                    <Card className="return-form-card">
                        <form onSubmit={handleSubmit} className="report-form">
                            <div className="form-row" style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
                                <div style={{ flex: 1 }}>
                                    <Input
                                        label="Found Item ID"
                                        placeholder="Enter ID..."
                                        value={formData.item_id}
                                        onChange={(e) => setFormData({ ...formData, item_id: e.target.value })}
                                        required
                                    />
                                </div>
                                <Button type="button" variant="secondary" onClick={fetchItemDetails} disabled={fetching} style={{ marginBottom: '16px' }}>
                                    {fetching ? '...' : 'Fetch'}
                                </Button>
                            </div>

                            <Input
                                label="Owner Name / Recipient"
                                placeholder="Full name of the person receiving"
                                value={formData.owner_name}
                                onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                                required
                            />

                            <Input
                                label="Return Date"
                                type="date"
                                value={formData.date_returned}
                                onChange={(e) => setFormData({ ...formData, date_returned: e.target.value })}
                                required
                            />

                            <div className="form-group">
                                <label className="form-label">Admin Notes (ID Verification, etc.)</label>
                                <textarea
                                    className="form-textarea"
                                    placeholder="e.g. Verified via Student ID #12345..."
                                    value={formData.handover_notes}
                                    onChange={(e) => setFormData({ ...formData, handover_notes: e.target.value })}
                                    style={{ height: '100px' }}
                                    required
                                ></textarea>
                            </div>

                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
                                Recorded by: <strong>{adminUser.username || 'System Admin'}</strong>
                            </p>

                            <Button type="submit" variant="primary" disabled={loading || !itemDetails} style={{ width: '100%' }}>
                                {loading ? 'Processing...' : 'Confirm Handover'}
                            </Button>
                        </form>
                    </Card>

                    <Card className="item-preview-card" style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
                        {itemDetails ? (
                            <div className="item-detail-preview">
                                <h2 style={{ color: 'var(--primary)', marginBottom: 'var(--space-2)' }}>Item Preview</h2>
                                {itemDetails.main_picture && (
                                    <img src={itemDetails.main_picture} alt="Preview" style={{ width: '100%', borderRadius: '12px', marginBottom: 'var(--space-2)' }} />
                                )}
                                <div className="detail-row"><strong>Type:</strong> <span>{itemDetails.item_type}</span></div>
                                <div className="detail-row"><strong>Category:</strong> <span>{itemDetails.category}</span></div>
                                <div className="detail-row"><strong>Color:</strong> <span>{itemDetails.color || 'N/A'}</span></div>
                                <div className="detail-row"><strong>Found at:</strong> <span>{itemDetails.found_location}</span></div>
                                <div className="detail-row" style={{ marginTop: 'var(--space-2)', borderTop: '1px solid #ddd', paddingTop: 'var(--space-2)' }}>
                                    <strong>Description:</strong>
                                    <p style={{ fontSize: '14px', marginTop: '4px' }}>{itemDetails.public_description}</p>
                                </div>
                            </div>
                        ) : (
                            <div className="empty-preview" style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                <p>Enter a valid Item ID to preview details here.</p>
                                {error && <p style={{ color: 'var(--danger)', marginTop: '8px' }}>{error}</p>}
                            </div>
                        )}
                    </Card>
                </div>
            </div>
        </div>
    );
};

export default AdminReturnItem;
