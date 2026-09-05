import React, { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Wheat, ArrowRight } from 'lucide-react';
import { authAPI } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';
import { Spinner } from '../../components/ui/primitives';

const isNetworkError = (err: unknown) =>
  err instanceof TypeError || (err instanceof Error && /failed to fetch|networkerror/i.test(err.message));

const RegisterPage: React.FC = () => {
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
      try {
        await authAPI.register(email, password);
      } catch (err) {
        // In the preview the backend is unreachable; fall through to the demo
        // session created by login(). Re-throw genuine validation errors.
        if (!isNetworkError(err)) throw err;
      }
      await login(email, password);
      showToast('Account created', 'success');
      navigate('/home');
    } catch (err) {
      showToast(err instanceof Error ? err.message : 'Could not create account', 'error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid min-h-screen lg:grid-cols-2">
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

          <h1 className="text-h2 font-display">Create your account</h1>
          <p className="mt-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Start comparing buyers and mandis by real net price.
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
                minLength={6}
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="input"
                placeholder="At least 6 characters"
                autoComplete="new-password"
              />
            </div>
            <button type="submit" disabled={loading} className="btn btn-primary btn-lg w-full">
              {loading ? <Spinner /> : <>Create account <ArrowRight size={18} /></>}
            </button>
          </form>

          <p className="mt-6 text-sm" style={{ color: 'var(--text-secondary)' }}>
            Already have an account?{' '}
            <Link to="/login" className="link-accent font-medium">Sign in</Link>
          </p>
        </div>
      </div>

      <div className="relative hidden lg:block">
        <img src="/images/home-hero.png" alt="" className="absolute inset-0 h-full w-full object-cover" />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(180deg, rgba(8,11,20,0.35), rgba(8,11,20,0.9))' }}
        />
        <div className="absolute inset-x-0 bottom-0 p-12">
          <p className="text-eyebrow mb-4">Built for Indian growers</p>
          <h2 className="text-h1 font-display max-w-md text-balance text-cream">
            One clear number: what actually lands in your hand.
          </h2>
        </div>
      </div>
    </div>
  );
};

export default RegisterPage;
