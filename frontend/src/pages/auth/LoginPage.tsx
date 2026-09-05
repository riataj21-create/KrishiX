import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wheat, ArrowRight } from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Spinner } from '../../components/ui/primitives';

const LoginPage: React.FC = () => {
  const { login } = useAuth();
  const { showToast } = useToast();
  const navigate = useNavigate();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);

  const submit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    try {
      await login(email, password);
      showToast('Welcome back', 'success');
      navigate('/home');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Could not sign in', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
      {/* Visual side */}
      <div className="relative hidden lg:block">
        <img src="/images/profile.png" alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(180deg, rgba(8,11,20,0.35), rgba(8,11,20,0.9))' }}
        />
        <div className="absolute inset-x-0 bottom-0 p-12">
          <p className="text-eyebrow mb-4">KrishiX · Market Intelligence</p>
          <h2 className="text-h1 font-display max-w-md text-balance text-cream">
            Know where your crop earns more — before you load the truck.
          </h2>
        </div>
      </div>

      {/* Form side */}
      <div className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm animate-in">
          <div className="mb-8 flex items-center gap-3">
            <div
              className="flex h-11 w-11 items-center justify-center rounded-xl"
              style={{ background: 'linear-gradient(135deg, var(--indigo), var(--violet))' }}
            >
              <Wheat size={22} className="text-white" />
            </div>
            <span className="font-display text-xl">KrishiX</span>
          </div>

          <h1 className="text-h2 font-display">Sign in</h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Compare recent prices, distance and selling costs in one place.
          </p>

          <form onSubmit={submit} className="mt-8 space-y-4">
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="email">Email</label>
              <input
                id="email"
                type="email"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                className="input"
                placeholder="you@farm.in"
                autoComplete="email"
              />
            </div>
            <div>
              <label className="mb-1.5 block text-sm font-medium" htmlFor="password">Password</label>
              <input
                id="password"
                type="password"
                required
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="••••••••"
                autoComplete="current-password"
              />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-full">
              {loading ? <Spinner /> : <>Sign in <ArrowRight size={18} /></>}
            </button>
          </form>

          <p className="mt-6 text-sm" style={{ color: 'var(--text-secondary)' }}>
            New to KrishiX?{' '}
            <Link to="/register" className="link-accent font-medium">Create an account</Link>
          </p>
        </div>
      </div>
    </div>
  );
};

export default LoginPage;
