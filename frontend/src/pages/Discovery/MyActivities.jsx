import React, { useEffect } from 'react';
import Card from '../../components/UI/Card';
import { useHttp } from '../../hooks/useHttp';
import StatusState from '../../components/UI/StatusState';
import { ActivitySkeleton } from '../../components/common/Skeleton';
import './Discovery.css';

const MyActivities = () => {
    const { loading, error, data, request } = useHttp();

    useEffect(() => {
        request({ url: '/items/my-activities' });
    }, [request]);

    const activities = data || { reports: [], claims: [] };
    const { request: dismissRequest } = useHttp();

    const handleDismiss = async (id, type) => {
        const endpoint = type === 'claim' ? `/items/claims/${id}/dismiss` : `/items/reports/${type}/${id}/dismiss`;
        try {
            await dismissRequest({ url: endpoint, method: 'POST' });
            request({ url: '/items/my-activities' }); // Refresh list
        } catch (err) {
            console.error('Dismissal failed', err);
        }
    };

    const getStatusTheme = (status) => {
        const s = status?.toLowerCase();
        if (['approved', 'lost', 'found', 'completed', 'reported_lost'].includes(s)) {
            return {
                color: 'var(--success)',
                bg: 'rgba(34, 197, 94, 0.08)',
                border: 'var(--success)'
            };
        }
        if (s === 'rejected') {
            return {
                color: 'var(--danger)',
                bg: 'rgba(239, 68, 68, 0.08)',
                border: 'var(--danger)'
            };
        }
        return {
            color: 'var(--secondary-dark)',
            bg: 'rgba(251, 191, 36, 0.08)',
            border: 'var(--secondary)'
        };
    };

    const StatusBadge = ({ status }) => {
        const theme = getStatusTheme(status);
        const displayStatus = (status === 'reported_lost' || status === 'lost') ? 'Approved' : status?.replace('_', ' ');
        return (
            <span style={{ 
                fontSize: '10px', 
                fontWeight: 800, 
                padding: '4px 8px', 
                borderRadius: '12px', 
                backgroundColor: `${theme.color}20`, 
                color: theme.color,
                textTransform: 'uppercase',
                letterSpacing: '0.5px'
            }}>
                {displayStatus || 'unknown'}
            </span>
        );
    };

    const ActivityCard = ({ item, type }) => {
        const status = item.status || item.decision || 'pending';
        const theme = getStatusTheme(status);
        const canDismiss = ['approved', 'rejected', 'lost', 'found', 'completed'].includes(status.toLowerCase());

        return (
            <Card style={{ position: 'relative', overflow: 'hidden' }}>
                {canDismiss && (
                    <button 
                        onClick={() => handleDismiss(type === 'report' ? item.id : item.claim_id, type === 'report' ? item.type : 'claim')}
                        style={{
                            position: 'absolute',
                            top: '12px',
                            right: '12px',
                            background: 'none',
                            border: 'none',
                            fontSize: '18px',
                            cursor: 'pointer',
                            color: 'var(--text-muted)',
                            opacity: 0.6,
                            transition: 'all 0.2s ease',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            zIndex: 2,
                            padding: '4px'
                        }}
                        onMouseEnter={(e) => e.target.style.opacity = '1'}
                        onMouseLeave={(e) => e.target.style.opacity = '0.6'}
                        title="Dismiss from activities"
                    >
                        ✕
                    </button>
                )}
                <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '8px', alignItems: 'center', paddingRight: canDismiss ? '30px' : '0' }}>
                    <h3 style={{ margin: 0, fontSize: '1.1rem' }}>
                        {type === 'report' ? item.item_type : `Claim #${item.claim_id}`}
                    </h3>
                    <StatusBadge status={status} />
                </div>
                <p style={{ fontSize: '13px', color: 'var(--text-secondary)', margin: '4px 0' }}>
                    {type === 'report' 
                        ? `${item.category} • Incident on ${new Date(item.incident_date).toLocaleDateString()}`
                        : `#${item.found_item_id || item.lost_item_id || '???'}-${item.item_type || 'Unknown Item'}`
                    }
                </p>
                <div style={{ fontSize: '11px', color: 'var(--text-muted)', display: 'flex', gap: '8px', marginTop: '4px' }}>
                    <span>{type === 'report' ? 'Report Date:' : 'Claim Request Date:'} {new Date(type === 'report' ? item.report_date : item.created_at).toLocaleDateString()}</span>
                    {type === 'report' && (
                        <span>• Location: {item.last_seen_location || item.found_location}</span>
                    )}
                </div>
                {(item.rejection_reason || item.decision_reason || (status.toLowerCase() === 'approved')) && (
                    <div style={{ 
                        marginTop: '12px', 
                        padding: '12px', 
                        borderRadius: 'var(--radius-sm)', 
                        backgroundColor: theme.bg, 
                        borderLeft: `4px solid ${theme.border}` 
                    }}>
                        <p style={{ margin: 0, fontSize: '12px', color: theme.color, fontWeight: 700 }}>
                            {status.toLowerCase() === 'approved' ? 'Action Required:' : 'Admin Feedback:'}
                        </p>
                        <p style={{ margin: '4px 24px 0 0', fontSize: '13px', color: 'var(--text)' }}>
                            {status.toLowerCase() === 'approved' 
                                ? 'Your claim has been approved! Please visit the Administrative Office with your valid ID to claim your item.' 
                                : (item.rejection_reason || item.decision_reason)
                            }
                        </p>
                    </div>
                )}
                {item.handover_notes && (
                    <div style={{ marginTop: '12px', fontSize: '12px', color: 'var(--text-secondary)', borderTop: '1px dashed var(--border-color)', paddingTop: '8px' }}>
                        <strong>Return Log:</strong> {item.handover_notes}
                    </div>
                )}
            </Card>
        );
    };

    const hasAnyActivity = activities.reports.length > 0 || activities.claims.length > 0;

    return (
        <div className="page-container">
            <div className="container">
                <div className="pretty-header">
                    <h1 className="pretty-title">My Activities</h1>
                    <p className="auth-subtitle">Track the status of your reports and claims in real-time.</p>
                    <div className="title-underline"></div>
                </div>

                <StatusState
                    loading={loading}
                    error={error}
                    isEmpty={!hasAnyActivity}
                    emptyMessage="You haven't reported or claimed any items yet."
                    onRetry={() => request({ url: '/items/my-activities' })}
                    skeleton={<ActivitySkeleton rows={3} />}
                >
                    <div className="activities-layout" style={{ 
                        display: 'grid', 
                        gridTemplateColumns: 'repeat(auto-fit, minmax(400px, 1fr))', 
                        gap: 'var(--space-5)',
                        marginTop: 'var(--space-4)'
                    }}>
                        {/* Reports Section */}
                        <div className="activity-section">
                            <h2 style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                My Reports
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                                {activities.reports.map(report => (
                                    <ActivityCard key={report.id} item={report} type="report" />
                                ))}
                                {activities.reports.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No reports filed.</p>}
                            </div>
                        </div>

                        {/* Claims Section */}
                        <div className="activity-section">
                            <h2 style={{ marginBottom: 'var(--space-3)', display: 'flex', alignItems: 'center', gap: '8px' }}>
                                My Claims
                            </h2>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-3)' }}>
                                {activities.claims.map(claim => (
                                    <ActivityCard key={claim.claim_id} item={claim} type="claim" />
                                ))}
                                {activities.claims.length === 0 && <p style={{ color: 'var(--text-muted)' }}>No claims submitted.</p>}
                            </div>
                        </div>
                    </div>
                </StatusState>
            </div>
        </div>
    );
};

export default MyActivities;
