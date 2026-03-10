import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import AuthLayout from './AuthLayout';

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
        // Prepare data for backend. We don't send confirmPassword.
        const { confirmPassword, ...submitData } = formData;

        // Only send admin_id if role is admin
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
            <h2 className="auth-title">Join Community</h2>
            {error && <div className="error-message" style={{ color: '#ef4444', marginBottom: '1rem', textAlign: 'center' }}>{error}</div>}
            <form className="auth-form" onSubmit={handleSubmit}>
                <div className="form-group">
                    <label>Full Name</label>
                    <input
                        type="text"
                        className="auth-input"
                        placeholder="John Doe"
                        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Email</label>
                    <input
                        type="email"
                        className="auth-input"
                        placeholder="john@campus.edu"
                        onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Username</label>
                    <input
                        type="text"
                        className="auth-input"
                        placeholder="jdoe"
                        onChange={(e) => setFormData({ ...formData, username: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Password</label>
                    <input
                        type="password"
                        className="auth-input"
                        placeholder="••••••••"
                        onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Confirm Password</label>
                    <input
                        type="password"
                        className="auth-input"
                        placeholder="••••••••"
                        onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                        required
                    />
                </div>

                <div className="form-group">
                    <label>Role</label>
                    <select
                        className="auth-select"
                        value={formData.role}
                        onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                    >
                        <option value="user">User</option>
                        <option value="admin">Admin</option>
                    </select>
                </div>

                {formData.role === 'admin' && (
                    <div className="form-group">
                        <label>Admin School ID</label>
                        <input
                            type="text"
                            className="auth-input"
                            placeholder="ADM-XXXX"
                            required
                            onChange={(e) => setFormData({ ...formData, admin_id: e.target.value })}
                        />
                    </div>
                )}

                <button type="submit" className="auth-primary-btn" disabled={isLoading}>
                    {isLoading ? 'Creating Account...' : 'Create Account'}
                </button>
            </form>

            <p className="auth-switch">
                Already have an account?
                <Link to="/login" className="auth-switch-link">Login</Link>
            </p>
        </AuthLayout>
    );
};

export default SignupPage;

