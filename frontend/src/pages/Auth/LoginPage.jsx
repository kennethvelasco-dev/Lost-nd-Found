import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AuthLayout from './AuthLayout';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const LoginPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        role: 'user'
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    
    const { login } = useAuth();
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const result = await login(formData.username, formData.password, formData.role);
            if (result.success) {
                if (formData.role === 'admin') {
                    navigate('/admin/dashboard');
                } else {
                    navigate('/lost-items');
                }
            } else {
                setError(result.message || 'Invalid credentials');
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
                <h1 className="auth-title">Welcome Back</h1>
                <p className="auth-subtitle">Log in to manage your items</p>
            </div>

            {error && <div className="error-message" style={{ color: 'var(--danger)', marginBottom: 'var(--space-2)', textAlign: 'center', fontSize: '0.875rem' }}>{error}</div>}

            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="role-selector-container">
                    <label className="form-label" style={{ textAlign: 'center', display: 'block', width: '100%', marginBottom: '12px' }}>Sign in as</label>
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
                    type="text"
                    placeholder="Enter your username"
                    value={formData.username}
                    onChange={(e) => setFormData({ ...formData, username: e.target.value })}
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

                <Button type="submit" variant="primary" style={{ marginTop: 'var(--space-2)', width: '100%', padding: '16px' }} disabled={loading}>
                    {loading ? 'Authenticating...' : 'Sign In Now'}
                </Button>
            </form>

            <div className="auth-footer">
                <p>
                    Don't have an account?
                    <Link to="/signup" className="auth-switch-link">Create Account</Link>
                </p>
            </div>
        </AuthLayout>
    );
};

export default LoginPage;
