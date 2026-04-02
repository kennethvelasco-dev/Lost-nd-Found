import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import api from '../../services/api';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';
import Card from '../../components/UI/Card';

import FileUpload from '../../components/UI/FileUpload';

const AdminReturnItem = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const adminUser = JSON.parse(localStorage.getItem('user') || '{}');

    // Extract state passed from AdminClaimDetail or AdminApprovedClaims
    const { itemId, claim_id, claimantName, category, itemType, color, brand, dateLost, dateFound } = location.state || {};

    const [formData, setFormData] = useState({
        item_id: itemId || '',
        claim_id: claim_id || '',
        owner_name: claimantName || '',
        recipient_id: '', // Student ID / ID Number
        date_returned: new Date().toISOString().split('T')[0],
        handover_notes: (category && itemType) 
            ? `Verified ${color || ''} ${brand || ''} ${itemType} (${category}). Recipient presented valid ID matching claimant name.`
            : ''
    });

    const [turnoverProof, setTurnoverProof] = useState([]);
    const [itemDetails, setItemDetails] = useState(null);
    const [loading, setLoading] = useState(false);
    const [fetching, setFetching] = useState(false);
    const [error, setError] = useState('');

    const fetchItemDetails = async (idToFetch) => {
        const id = idToFetch || formData.item_id;
        if (!id) return;
        setFetching(true);
        setError('');
        try {
            const response = await api.get(`/items/${id}`);
            // Check nesting based on API response structure
            setItemDetails(response.data?.data?.item || response.data?.data || response.data);
        } catch (err) {
            setError('Item not found. Please check the ID.');
            setItemDetails(null);
        } finally {
            setFetching(false);
        }
    };

    // Auto-fetch if itemId is provided via state
    useEffect(() => {
        if (itemId) {
            fetchItemDetails(itemId);
        }
    }, [itemId]);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (!turnoverProof || turnoverProof.length === 0) {
            setError('A turnover proof photo is mandatory to finalize the log.');
            setLoading(false);
            return;
        }

        try {
            await api.post('/admin/resolve-item', {
                item_id: formData.item_id,
                claim_id: formData.claim_id,
                owner_name: formData.owner_name,
                recipient_id: formData.recipient_id,
                handover_notes: formData.handover_notes,
                date_returned: formData.date_returned,
                turnover_proof: turnoverProof[0]
            });
            
            navigate('/confirmation', { 
                state: { 
                    title: 'Return Logged!', 
                    message: `Item #${formData.item_id} has been officially returned to ${formData.owner_name} (ID: ${formData.recipient_id}). The return log is now finalized.`,
                    nextSteps: []
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
                    <h1 className="pretty-title">Process Return Log</h1>
                    <p className="auth-subtitle">Face-to-face verification and final item handover.</p>
                    <div className="title-underline"></div>
                </div>

                <div className="admin-return-grid" style={{ display: 'grid', gridTemplateColumns: 'minmax(350px, 1fr) 1fr', gap: 'var(--space-4)' }}>
                    <Card>
                        <form onSubmit={handleSubmit} className="report-form" style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                            <div className="form-row" style={{ display: 'flex', gap: '10px', alignItems: 'flex-end' }}>
                                <div style={{ flex: 1 }}>
                                    <Input
                                        label="Item ID"
                                        placeholder="Enter ID..."
                                        value={formData.item_id}
                                        onChange={(e) => setFormData({ ...formData, item_id: e.target.value })}
                                        required
                                        // Allow overwrite for admin flexibility
                                    />
                                </div>
                                <Button type="button" variant="secondary" onClick={() => fetchItemDetails()} disabled={fetching} style={{ marginBottom: '16px' }}>
                                    {fetching ? '...' : 'Fetch'}
                                </Button>
                            </div>

                            <Input
                                label="Recipient Full Name"
                                placeholder="Verified Name from ID"
                                value={formData.owner_name}
                                onChange={(e) => setFormData({ ...formData, owner_name: e.target.value })}
                                required
                            />

                            <Input
                                label="Student ID / ID Number"
                                placeholder="Enter ID Number for audit trail"
                                value={formData.recipient_id}
                                onChange={(e) => setFormData({ ...formData, recipient_id: e.target.value })}
                                required
                            />

                            <Input
                                label="Handover Date"
                                type="date"
                                value={formData.date_returned}
                                onChange={(e) => setFormData({ ...formData, date_returned: e.target.value })}
                                required
                            />

                            <FileUpload 
                                label="Turnover Proof (Mandatory Photo)"
                                initialFiles={turnoverProof}
                                onFilesChange={(files) => setTurnoverProof(files)}
                                maxFiles={1}
                            />

                            <div className="form-group">
                                <label className="form-label">Handover Notes</label>
                                <textarea
                                    className="form-textarea"
                                    placeholder="Verified identity and signed handover receipt..."
                                    value={formData.handover_notes}
                                    onChange={(e) => setFormData({ ...formData, handover_notes: e.target.value })}
                                    style={{ height: '80px' }}
                                    required
                                ></textarea>
                            </div>

                            <p style={{ fontSize: '12px', color: 'var(--text-muted)', marginBottom: 'var(--space-2)' }}>
                                Handover Processed by Admin: <strong>{adminUser.username}</strong>
                            </p>

                            <Button type="submit" variant="primary" disabled={loading || !itemDetails} style={{ width: '100%' }}>
                                {loading ? 'Filing Log...' : 'File Log Return'}
                            </Button>
                        </form>
                    </Card>

                    <Card style={{ display: 'flex', flexDirection: 'column', background: 'rgba(0,0,0,0.02)', padding: 'var(--space-4)' }}>
                        {itemDetails ? (
                            <div className="item-detail-preview">
                                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 'var(--space-3)' }}>
                                    <h2 style={{ color: 'var(--primary)', margin: 0 }}>Item Preview</h2>
                                    <span style={{ fontSize: '11px', fontWeight: 800, color: 'var(--text-muted)' }}>ID: #{itemDetails.id}</span>
                                </div>
                                {itemDetails.main_picture && (
                                    <img src={itemDetails.main_picture} alt="Preview" style={{ width: '100%', maxHeight: '250px', objectFit: 'cover', borderRadius: 'var(--radius-md)', marginBottom: 'var(--space-3)', border: '1px solid rgba(0,0,0,0.1)' }} />
                                )}
                                <div className="preview-info" style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Type:</strong> <span>{itemDetails.item_type}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Category:</strong> <span>{itemDetails.category}</span></div>
                                    <div style={{ display: 'flex', justifyContent: 'space-between' }}><strong>Color:</strong> <span>{itemDetails.color || 'N/A'}</span></div>
                                    <div style={{ marginTop: '10px', borderTop: '1px solid rgba(0,0,0,0.05)', paddingTop: '10px' }}>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '4px' }}>
                                            <strong>Date Lost (Claimant):</strong> 
                                            <span>{dateLost ? new Date(dateLost).toLocaleDateString() : (itemDetails.last_seen_datetime ? new Date(itemDetails.last_seen_datetime).toLocaleDateString() : 'N/A')}</span>
                                        </div>
                                        <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '10px' }}>
                                            <strong>Date Found (Report):</strong> 
                                            <span>{dateFound ? new Date(dateFound).toLocaleDateString() : (itemDetails.found_datetime ? new Date(itemDetails.found_datetime).toLocaleDateString() : 'N/A')}</span>
                                        </div>
                                        <p style={{ fontSize: '14px', color: 'var(--text-muted)', fontStyle: 'italic', margin: 0 }}>{itemDetails.public_description}</p>
                                    </div>
                                </div>
                            </div>
                        ) : (
                            <div style={{ textAlign: 'center', color: 'var(--text-muted)', paddingTop: 'var(--space-5)' }}>
                                <p>Load an item to verify details before filing the return log.</p>
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
