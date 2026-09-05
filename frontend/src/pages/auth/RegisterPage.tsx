import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { authAPI } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

export default function RegisterPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<'farmer' | 'buyer'>('farmer');
  const [loading, setLoading] = useState(false);
  const toast = useToast();
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (password.length < 8) { toast.error('Password must be at least 8 characters'); return; }
    setLoading(true);
    try {
      await authAPI.register(email, password, role);
      toast.success('Account created! Please sign in.');
      navigate('/login');
    } catch (err: any) {
      toast.error(err.message || 'Registration failed');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-[var(--background)] px-4">
      <div className="w-full max-w-md card">
        <div className="card-body">
          <h1 className="text-h3 mb-1 text-center">Create your account</h1>
          <p className="text-sm text-[var(--text-secondary)] text-center mb-6">Join KrishiX to access market intelligence</p>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div>
              <label className="block text-sm font-medium mb-1.5">I am a</label>
              <div className="grid grid-cols-2 gap-2">
                {(['farmer', 'buyer'] as const).map(r => (
                  <button key={r} type="button"
                    onClick={() => setRole(r)}
                    className={`rounded-md border px-4 py-2.5 text-sm font-medium transition-colors capitalize ${role === r ? 'border-[var(--accent)] bg-[var(--accent-soft)] text-[var(--accent-dark)]' : 'border-[var(--border)] text-[var(--text-secondary)]'}`}>
                    {r}
                  </button>
                ))}
              </div>
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Email</label>
              <input type="email" className="input" value={email} onChange={e => setEmail(e.target.value)} placeholder="you@example.com" required disabled={loading} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1.5">Password</label>
              <input type="password" className="input" value={password} onChange={e => setPassword(e.target.value)} placeholder="Min 8 characters" required disabled={loading} />
            </div>
            <button type="submit" className="btn-primary w-full" disabled={loading}>
              {loading ? 'Creating account...' : 'Create account'}
            </button>
          </form>
          <p className="text-center text-sm text-[var(--text-secondary)] mt-6">
            Already have an account? <Link to="/login" className="text-[var(--accent)] font-medium">Sign in</Link>
          </p>
        </div>
      </div>
    </div>
  );
}
