import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import AuthLayout from './AuthLayout';
import Button from '../../components/UI/Button';
import Input from '../../components/UI/Input';

const LoginPage = () => {
    const [formData, setFormData] = useState({
        username: '',
        password: '',
        role: 'user'
    });
    const navigate = useNavigate();

    const handleSubmit = (e) => {
        e.preventDefault();
        console.log('Login attempt:', formData);
        // TODO: Integrate with AuthContext
        navigate('/lost-items');
    };

    return (
        <AuthLayout>
            <div className="auth-header">
                <h1 className="auth-title">Welcome Back</h1>
                <p className="auth-subtitle">Log in to manage your items</p>
            </div>

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

                <Button type="submit" variant="primary" style={{ marginTop: 'var(--space-2)' }}>
                    Log In
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

