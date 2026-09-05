import React, { useState } from 'react';
import { LogOut, MapPin, Phone, ShieldCheck } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { useToast } from '../context/ToastContext';
import { Eyebrow } from '../components/ui/primitives';

const ProfilePage: React.FC = () => {
  const { user, logout } = useAuth();
  const { showToast } = useToast();
  const [name, setName] = useState(user?.name || '');
  const [phone, setPhone] = useState('');
  const [location, setLocation] = useState('Sinnar, Nashik');
  const [language, setLanguage] = useState('English');

  const initials = (user?.name || user?.email || 'K')
    .split(' ')
    .map((s) => s[0])
    .slice(0, 2)
    .join('')
    .toUpperCase();

  const save = (e: React.FormEvent) => {
    e.preventDefault();
    showToast('Profile updated', 'success');
  };

  return (
    <div className="mx-auto max-w-2xl space-y-8">
      <header>
        <Eyebrow>Account</Eyebrow>
        <h1 className="text-h1 font-display mt-2">Profile</h1>
      </header>

      {/* Identity card */}
      <div className="card flex items-center gap-5 p-6">
        <div
          className="flex h-16 w-16 flex-none items-center justify-center rounded-2xl text-xl font-semibold"
          style={{ background: 'linear-gradient(135deg, var(--indigo), var(--violet))', color: '#fff' }}
        >
          {initials}
        </div>
        <div className="min-w-0">
          <p className="text-h4">{user?.name || 'Farmer'}</p>
          <p className="truncate text-sm" style={{ color: 'var(--text-secondary)' }}>{user?.email}</p>
          <span className="badge badge-emerald mt-2"><ShieldCheck size={13} /> Verified grower</span>
        </div>
      </div>

      {/* Editable details */}
      <form onSubmit={save} className="card space-y-5 p-6 md:p-8">
        <h2 className="text-h4">Details</h2>
        <div className="grid gap-5 sm:grid-cols-2">
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="name">Full name</label>
            <input id="name" className="input" value={name} onChange={(e) => setName(e.target.value)} placeholder="Your name" />
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="phone">Phone</label>
            <div className="relative">
              <Phone size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
              <input id="phone" className="input pl-9" value={phone} onChange={(e) => setPhone(e.target.value)} placeholder="+91" />
            </div>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="loc">Location</label>
            <div className="relative">
              <MapPin size={15} className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2" style={{ color: 'var(--text-muted)' }} />
              <input id="loc" className="input pl-9" value={location} onChange={(e) => setLocation(e.target.value)} />
            </div>
          </div>
          <div>
            <label className="mb-1.5 block text-sm font-medium" htmlFor="lang">Language</label>
            <select id="lang" className="select" value={language} onChange={(e) => setLanguage(e.target.value)}>
              <option>English</option>
              <option>हिन्दी</option>
              <option>मराठी</option>
              <option>ਪੰਜਾਬੀ</option>
            </select>
          </div>
        </div>
        <div className="flex justify-end border-t pt-5" style={{ borderColor: 'var(--border)' }}>
          <button type="submit" className="btn btn-primary">Save changes</button>
        </div>
      </form>

      <button onClick={logout} className="btn btn-outline w-full" style={{ color: 'var(--burgundy)', borderColor: 'rgba(177,68,91,0.4)' }}>
        <LogOut size={16} /> Sign out
      </button>
    </div>
  );
};

export default ProfilePage;
