import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AuthLayout from './AuthLayout';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const SignupPage = () => {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        username: '',
        password: '',
        confirmPassword: '',
        role: 'user',
        admin_id: ''
    });
    const [error, setError] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const navigate = useNavigate();
    const { register } = useAuth();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            return;
        }

        setIsLoading(true);
        const { confirmPassword, ...submitData } = formData;

        if (submitData.role !== 'admin') {
            delete submitData.admin_id;
        }

        const result = await register(submitData);

        if (result.success) {
            alert('Registration successful! Please login.');
            navigate('/login');
        } else {
            setError(result.message);
        }
        setIsLoading(false);
    };

    return (
        <AuthLayout>
            <div className="auth-header">
                <h1 className="auth-title">Join Community</h1>
                <p className="auth-subtitle">Create an account to get started</p>
            </div>

            {error && (
                <div className="error-message" style={{ 
                    color: 'var(--danger)', 
                    marginBottom: 'var(--space-2)', 
                    textAlign: 'center',
                    fontSize: '0.875rem',
                    fontWeight: '500'
                }}>
                    {error}
                </div>
            )}

            <form className="auth-form" onSubmit={handleSubmit}>
                <Input
                    label="Full Name"
                    type="text"
                    placeholder="John Doe"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    required
                />

                <Input
                    label="Email"
                    type="email"
                    placeholder="john@campus.edu"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    required
                />

                <Input
                    label="Username"
                    type="text"
                    placeholder="jdoe"
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

                <Input
                    label="Confirm Password"
                    type="password"
                    placeholder="••••••••"
                    value={formData.confirmPassword}
                    onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                    required
                />

                <div className="form-group">
                    <label className="form-label">Role</label>
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

                {formData.role === 'admin' && (
                    <Input
                        label="Admin School ID"
                        type="text"
                        placeholder="ADM-XXXX"
                        value={formData.admin_id}
                        onChange={(e) => setFormData({ ...formData, admin_id: e.target.value })}
                        required
                    />
                )}

                <Button type="submit" variant="primary" disabled={isLoading} style={{ marginTop: 'var(--space-2)' }}>
                    {isLoading ? 'Creating Account...' : 'Create Account'}
                </Button>
            </form>

            <div className="auth-footer">
                <p>
                    Already have an account?
                    <Link to="/login" className="auth-switch-link">Login</Link>
                </p>
            </div>
        </AuthLayout>
    );
};

export default SignupPage;

