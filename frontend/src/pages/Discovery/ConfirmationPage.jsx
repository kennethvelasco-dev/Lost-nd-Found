import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';
import './ConfirmationPage.css';

const ConfirmationPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const itemType = location.state?.itemType || 'item';

    const title = location.state?.title || 'Submitted Successfully!';
    const message = location.state?.message || `Your request for the ${itemType} has been successfully received.`;
    const nextSteps = location.state?.nextSteps || [
        "Wait for administrator review (usually 1-3 business days).",
        "Check your email for notifications.",
        "Prepare original proof if required for pickup."
    ];

    return (
        <div className="container confirmation-page">
            <Card className="confirmation-card" hover={false}>
                <div className="confirmation-icon">✅</div>
                <h1 className="confirmation-title">{title}</h1>
                <p className="confirmation-message">{message}</p>
                
                {nextSteps.length > 0 && (
                    <div className="confirmation-steps">
                        <h3>Next Steps:</h3>
                        <ul>
                            {nextSteps.map((step, idx) => (
                                <li key={idx}>{step}</li>
                            ))}
                        </ul>
                    </div>
                )}

                <div className="confirmation-actions">
                    <Button variant="primary" onClick={() => navigate('/lost-items')}>
                        Back to Discovery
                    </Button>
                    {JSON.parse(localStorage.getItem('user') || '{}').role === 'admin' ? (
                        <Button variant="secondary" onClick={() => navigate('/admin/dashboard')}>
                            Admin Dashboard
                        </Button>
                    ) : (
                        <Button variant="secondary" onClick={() => navigate('/user/profile')}>
                            View My Claims
                        </Button>
                    )}
                </div>
            </Card>
        </div>
    );
};

export default ConfirmationPage;
