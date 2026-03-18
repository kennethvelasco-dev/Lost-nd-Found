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

                <div className="form-group">
                    <label className="form-label">Login as</label>
                    <select
                        style={{
                            width: '100%',
                            padding: '10px 14px',
                            borderRadius: 'var(--radius-sm)',
                            border: '1px solid #e5e7eb',
                            backgroundColor: 'white',
                            fontSize: '1rem'
                        }}
                        value={formData.role}
                        onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    >
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>

                <Button type="submit" variant="primary" style={{ marginTop: 'var(--space-2)' }} disabled={loading}>
                    {loading ? 'Logging in...' : 'Log In'}
                </Button>
            </form>

            <div className="auth-footer">
                <p>
                    Don't have an account?
                    <Link to="/signup" className="auth-switch-link">Sign up</Link>
                </p>
            </div>
        </AuthLayout>
    );
};

export default LoginPage;

