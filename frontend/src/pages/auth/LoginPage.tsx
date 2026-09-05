import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export default function LoginPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const { login } = useAuth();
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      const user = await login(email, password);
      toast.success(`Welcome back!`);
      navigate(user.role === 'buyer' ? '/buyer/dashboard' : '/dashboard', { replace: true });
    } catch (err: any) {
      toast.error(err.message || 'Login failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] px-4">
      <div className="w-full max-w-md card">
        <div className="card-body">
          <h1 className="text-h3 mb-1 text-center">Sign in to KrishiX</h1>
          <p className="text-sm text-[var(--text-secondary)] text-center mb-6">Market intelligence for smarter agricultural decisions</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">Email</label>
              <input type="email" className="input" value={email} onChange={e => setEmail(e.target.value)} placeholder="farmer@example.com" required disabled={loading} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Password</label>
              <input type="password" className="input" value={password} onChange={e => setPassword(e.target.value)} placeholder="Your password" required disabled={loading} />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Signing in...' : 'Sign in'}
            </button>
          </form>
          <p className="text-center text-sm text-[var(--text-secondary)] mt-6">
            Don't have an account? <Link to="/register" className="text-[var(--accent)] font-medium">Register</Link>
          </p>
          <div className="mt-4 rounded-md bg-[var(--surface-subtle)] p-3 text-xs text-[var(--text-muted)]">
            <strong>Demo:</strong> farmer1@krishix.com / password123
          </div>
        </div>
      </div>
    </div>
  );
}
