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
            setItemDetails(response.data.data.item || response.data.data);
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
            await api.post('/admin/resolve-item', {
                item_id: formData.item_id,
                owner_name: formData.owner_name,
                handover_notes: formData.handover_notes,
                date_returned: formData.date_returned
            });
            
            navigate('/confirmation', { 
                state: { 
                    title: 'Return Logged!', 
                    message: `Item #${formData.item_id} has been marked as returned to ${formData.owner_name} by admin ${adminUser.username}.` 
                } 
            });
        } catch (err) {
            setError(err.response?.data?.message || 'Failed to log return.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Process Handover</h1>
                    <p className="auth-subtitle">Verify recipient identity and log item resolution.</p>
                    <div className="title-underline"></div>
                </div>

                <div className="admin-return-grid" style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1fr) 1fr', gap: 'var(--space-4)' }}>
                    <Card>
                        <form onSubmit={handleSubmit} className="report-form" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
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
                                label="Recipient Name"
                                placeholder="Full name from ID verification"
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
                                <label className="form-label">Handover Notes</label>
                                <textarea
                                    className="form-textarea"
                                    placeholder="Verified via Student Card #12345..."
                                    value={formData.handover_notes}
                                    onChange={(e) => setFormData({ ...formData, handover_notes: e.target.value })}
                                    style={{ height: '100px' }}
                                    required
                                ></textarea>
                            </div>

                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
                                Authorized by: <strong>{adminUser.username}</strong>
                            </p>

                            <Button type="submit" variant="primary" disabled={loading || !itemDetails} style={{ width: '100%' }}>
                                {loading ? 'Logging Resolution...' : 'Complete Return'}
                            </Button>
                        </form>
                    </Card>

                    <Card style={{ display: 'flex', flexDirection: 'column', justifyContent: 'center', background: 'var(--background)', boxShadow: 'var(--nm-inset)', padding: 'var(--space-4)' }}>
                        {itemDetails ? (
                            <div className="item-detail-preview">
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
                                    <h2 style={{ color: 'var(--primary)', margin: 0 }}>Item Preview</h2>
                                    <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>ID: #{itemDetails.id}</span>
                                </div>
                                {itemDetails.main_picture && (
                                    <img src={itemDetails.main_picture} alt="Preview" style={{ width: '100%', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-3)', boxShadow: 'var(--nm-flat-sm)' }} />
                                )}
                                <div className="preview-info" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Type:</strong> <span>{itemDetails.item_type}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Category:</strong> <span>{itemDetails.category}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Color:</strong> <span>{itemDetails.color || 'N/A'}</span></div>
                                    <div style={{ marginTop: '10px', borderTop: '1px solid rgba(0,0,0,0.05)', paddingTop: '10px' }}>
                                        <p style={{ fontSize: '14px', color: 'var(--text-muted)' }}>{itemDetails.public_description}</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', color: 'var(--text-muted)' }}>
                                <p>Enter a valid Item ID and click <strong>Fetch</strong> to preview details before resolving.</p>
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
