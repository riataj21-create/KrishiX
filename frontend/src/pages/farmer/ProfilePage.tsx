import React, { useEffect, useState } from 'react';
import { Loader2, MapPin, Phone, ShieldCheck, UserCircle2 } from 'lucide-react';
import { farmerProfileAPI, type FarmerProfile } from '../../lib/api';
import { useAuth } from '../../context/AuthContext';
import { useToast } from '../../context/ToastContext';

export default function ProfilePage() {
  const { user } = useAuth();
  const toast = useToast();
  const [profile, setProfile] = useState<FarmerProfile | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    farmerProfileAPI.getProfile().then(setProfile).catch((error: Error) => toast.error(error.message || 'Unable to load profile')).finally(() => setLoading(false));
  }, [toast]);

  return <div className="page-container min-h-screen"><div className="mb-8 border-b border-white/10 pb-6"><p className="eyebrow">Account / identity</p><h1 className="editorial-title mt-2">Your field profile</h1><p className="mt-2 text-sm text-[#a9a8b3]">Keep your farmer context accurate so opportunities remain relevant.</p></div>{loading ? <div className="glass-panel flex items-center gap-2 p-8 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading profile...</div> : !profile ? <div className="glass-panel p-8 text-sm text-[#a9a8b3]">No farmer profile has been created yet. Add your location before analyzing a lot.</div> : <div className="photo-hero min-h-[620px] bg-[url('https://images.unsplash.com/photo-1500382017468-9049fed747ef?auto=format&fit=crop&w=1800&q=85')] p-6 sm:p-10"><div className="photo-content flex min-h-[540px] flex-col justify-between"><div><p className="eyebrow">Farmer identity</p><p className="mt-3 font-serif text-5xl font-semibold text-[#f5f1e8]">{profile.full_name}</p><p className="mt-2 text-sm text-[#f5f1e8]">{[profile.village, profile.district, profile.state].filter(Boolean).join(', ')}</p><p className="mt-1 text-xs text-[#c8c4d7]">{user?.email}</p></div><div className="glass-panel max-w-xl p-6"><div className="flex items-center gap-2 text-sm font-medium text-[#f5f1e8]"><ShieldCheck className="h-4 w-4 text-[#d6a84f]" /> Data used by decisions</div><div className="mt-5 grid gap-5 sm:grid-cols-2"><Info icon={<MapPin className="h-4 w-4" />} label="Location" value={[profile.village, profile.district, profile.state].filter(Boolean).join(', ')} /><Info icon={<Phone className="h-4 w-4" />} label="Phone" value={profile.phone || 'Not provided'} /><Info label="Coordinates" value={profile.latitude != null && profile.longitude != null ? `${profile.latitude}, ${profile.longitude}` : 'Not provided'} /><Info label="About" value={profile.bio || 'Not provided'} /></div></div></div></div>}</div>;
}

function Info({ icon, label, value }: { icon?: React.ReactNode; label: string; value: string }) { return <div><p className="flex items-center gap-2 text-xs uppercase tracking-[0.12em] text-[#a9a8b3]">{icon}{label}</p><p className="mt-2 text-sm">{value}</p></div>; }
