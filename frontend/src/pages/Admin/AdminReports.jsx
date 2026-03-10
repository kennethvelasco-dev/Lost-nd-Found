import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../../services/api';
import './AdminDashboard.css';

const AdminReports = () => {
    const [reports, setReports] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState(null);
    const navigate = useNavigate();

    const fetchReports = async () => {
        try {
            setLoading(true);
            const response = await api.get('/admin/reports/transactions');
            setReports(response.data.data.transactions || response.data.data || []);
            setError(null);
        } catch (err) {
            if (err.response?.status === 403 || err.response?.status === 401) {
                navigate('/login');
            } else {
                setError('Failed to fetch transaction reports.');
            }
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchReports();
    }, [navigate]);

    return (
        <div className="admin-dashboard">
            <h2 className="admin-title">Transaction Reports</h2>

            {loading ? (
                <div className="loading-spinner">Loading reports...</div>
            ) : error ? (
                <div className="error-message">{error}</div>
            ) : reports.length === 0 ? (
                <p className="no-items">No completed transactions found.</p>
            ) : (
                <div className="claims-list">
                    {reports.map((report) => (
                        <div key={report.claim_id} className="claim-card glass-panel">
                            <div className="claim-header">
                                <h3>Transaction #{report.claim_id}</h3>
                                <span className="status-badge completed">Completed</span>
                            </div>
                            <div className="claim-body">
                                <p><strong>Item Name:</strong> {report.item_name}</p>
                                <p><strong>Admin Username:</strong> {report.admin_username}</p>
                                <p><strong>Claimant Email:</strong> {report.claimant_email}</p>
                                <p><strong>Verification Details:</strong> {report.verification_details}</p>
                                <p><strong>Handover Timestamp:</strong> {new Date(report.transaction_timestamp).toLocaleString()}</p>
                            </div>
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default AdminReports;

