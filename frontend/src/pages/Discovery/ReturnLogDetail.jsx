import React, { useEffect, useState } from 'react';
import { useParams } from 'react-router-dom';
import api from '../../services/api';
import Card from '../../components/UI/Card';
import StatusState from '../../components/UI/StatusState';

const ReturnLogDetail = () => {
    const { id } = useParams();
    const [data, setData] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        const fetchDetail = async () => {
            try {
                const res = await api.get(`/items/released/${id}`);
                setData(res.data?.data || res.data);
            } catch (err) {
                setError(err.response?.data?.message || 'Failed to load return log.');
            } finally {
                setLoading(false);
            }
        };
        fetchDetail();
    }, [id]);

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">Return Log Detail</h1>
                    <p className="auth-subtitle">See how this item was matched and returned.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={!data}
                    emptyMessage="Return log not found."
                    onRetry={null}
                >
                    {data && (
                        <Card>
                            <h2 style={{ marginTop: 0 }}>
                                {data.item_type} ({data.category})
                            </h2>
                            <p><strong>Claimed by:</strong> {data.claimant_name || 'Unknown'}</p>
                            <p><strong>Recipient ID:</strong> {data.recipient_id || 'N/A'}</p>
                            <p><strong>Returned on:</strong> {data.resolved_at ? new Date(data.resolved_at).toLocaleString() : 'N/A'}</p>
                            <p><strong>Processed by:</strong> {data.released_by_admin || 'Admin'}</p>
                            <p><strong>Original report ID:</strong> {data.original_report_id}</p>
                            <p><strong>Location:</strong> {data.last_seen_location || data.found_location || 'N/A'}</p>
                            <p><strong>Notes:</strong></p>
                            <p style={{ whiteSpace: 'pre-wrap' }}>{data.handover_notes || 'No extra notes recorded.'}</p>
                        </Card>
                    )}
                </StatusState>
            </div>
        </div>
    );
};

export default ReturnLogDetail;
