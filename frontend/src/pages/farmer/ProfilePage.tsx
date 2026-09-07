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

  return <div className="page-container min-h-screen"><div className="mb-8 border-b border-white/10 pb-6"><p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">Account</p><h1 className="mt-2 text-4xl font-semibold">Profile</h1><p className="mt-2 text-sm text-[#a9a8b3]">Keep your farmer context accurate so opportunities remain relevant.</p></div>{loading ? <div className="flex items-center gap-2 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading profile...</div> : !profile ? <div className="border border-dashed border-white/15 bg-[#15182a] p-8 text-sm text-[#a9a8b3]">No farmer profile has been created yet. Add your location before analyzing a lot.</div> : <div className="grid gap-5 lg:grid-cols-[1.2fr_0.8fr]"><section className="border border-white/10 bg-[#15182a] p-6"><div className="flex items-center gap-4"><div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-[#24152f] text-[#d6a84f]"><UserCircle2 className="h-8 w-8" /></div><div><p className="text-2xl font-semibold">{profile.full_name}</p><p className="mt-1 text-sm text-[#a9a8b3]">{user?.email}</p></div></div><div className="mt-8 grid gap-5 sm:grid-cols-2"><Info icon={<MapPin className="h-4 w-4" />} label="Location" value={[profile.village, profile.district, profile.state].filter(Boolean).join(', ')} /><Info icon={<Phone className="h-4 w-4" />} label="Phone" value={profile.phone || 'Not provided'} /><Info label="Coordinates" value={profile.latitude != null && profile.longitude != null ? `${profile.latitude}, ${profile.longitude}` : 'Not provided'} /><Info label="About" value={profile.bio || 'Not provided'} /></div></section><aside className="border border-white/10 bg-[#15182a] p-6"><div className="flex items-center gap-2 text-sm font-medium"><ShieldCheck className="h-4 w-4 text-emerald-300" /> Data used by decisions</div><p className="mt-4 text-sm leading-6 text-[#a9a8b3]">Your location and selling preferences help the backend evaluate distance, transport, timing, and payment fit. Keep them current.</p></aside></div>}</div>;
}

function Info({ icon, label, value }: { icon?: React.ReactNode; label: string; value: string }) { return <div><p className="flex items-center gap-2 text-xs uppercase tracking-[0.12em] text-[#a9a8b3]">{icon}{label}</p><p className="mt-2 text-sm">{value}</p></div>; }
