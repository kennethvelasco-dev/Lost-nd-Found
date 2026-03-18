import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AuthLayout from './AuthLayout';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const SignupPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        confirmPassword: '',
        role: 'user'
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { signup } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        
        if (formData.password !== formData.confirmPassword) {
            return setError('Passwords do not match');
        }

        setLoading(true);

        try {
            const result = await signup(formData.username, formData.email, formData.password, formData.role);
            if (result.success) {
                navigate('/login');
            } else {
                setError(result.message || 'Registration failed');
            }
        } catch (err) {
            setError('An unexpected error occurred. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <AuthLayout>
            <div className="auth-header">
                <h1 className="auth-title">Create Account</h1>
                <p className="auth-subtitle">Join the Campus Lost & Found community</p>
            </div>

            {error && <div className="error-message" style={{ color: 'var(--danger)', marginBottom: 'var(--space-2)', textAlign: 'center', fontSize: '0.875rem' }}>{error}</div>}

            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="role-selector-container">
                    <label className="form-label" style={{ textAlign: 'center', display: 'block', width: '100%', marginBottom: '12px' }}>Register as</label>
                    <div className="role-selector">
                        <button 
                            type="button" 
                            className={`role-tab ${formData.role === 'user' ? 'active' : ''}`}
                            onClick={() => setFormData({ ...formData, role: 'user' })}
                        >
                            User
                        </button>
                        <button 
                            type="button" 
                            className={`role-tab ${formData.role === 'admin' ? 'active' : ''}`}
                            onClick={() => setFormData({ ...formData, role: 'admin' })}
                        >
                            Admin
                        </button>
                    </div>
                </div>

                <Input
                    label="Username"
                    placeholder="Choose a unique username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                    required
                />

                <Input
                    label="Email"
                    type="email"
                    placeholder="yourname@university.edu"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                />

                <Input
                    label="Password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.password}
                    onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                    required
                />

                <Input
                    label="Confirm Password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    required
                />

                <Button type="submit" variant="primary" style={{ marginTop: 'var(--space-2)', width: '100%', padding: '16px' }} disabled={loading}>
                    {loading ? 'Creating Account...' : 'Sign Up Now'}
                </Button>
            </form>

            <div className="auth-footer">
                <p>
                    Already have an account?
                    <Link to="/login" className="auth-switch-link">Sign In</Link>
                </p>
            </div>
        </AuthLayout>
    );
};

export default SignupPage;
