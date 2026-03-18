import React from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import Button from '../../components/UI/Button';
import Card from '../../components/UI/Card';
import './ConfirmationPage.css';

const ConfirmationPage = () => {
    const location = useLocation();
    const navigate = useNavigate();
    const itemType = location.state?.itemType || 'item';

    return (
        <div className="container confirmation-page">
            <Card className="confirmation-card" hover={false}>
                <div className="confirmation-icon">✅</div>
                <h1 className="confirmation-title">Claim Submitted!</h1>
                <p className="confirmation-message">
                    Your claim for the <strong>{itemType}</strong> has been successfully received. 
                    Our administrators will review your proof and contact you soon.
                </p>
                
                <div className="confirmation-steps">
                    <h3>Next Steps:</h3>
                    <ul>
                        <li>Wait for administrator review (usually 1-3 business days).</li>
                        <li>Check your email for notifications.</li>
                        <li>Prepare original proof if required for pickup.</li>
                    </ul>
                </div>

                <div className="confirmation-actions">
                    <Button variant="primary" onClick={() => navigate('/lost-items')}>
                        Back to Discovery
                    </Button>
                    <Button variant="secondary" onClick={() => navigate('/user/profile')}>
                        View My Claims
                    </Button>
                </div>
            </Card>
        </div>
    );
};

export default ConfirmationPage;
