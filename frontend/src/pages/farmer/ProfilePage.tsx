import React from 'react';
import { MapPin, Phone, ShieldCheck, UserCircle2 } from 'lucide-react';

export default function ProfilePage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-5xl rounded-3xl border border-white/10 bg-[#101827] p-6">
        <div className="mb-6 flex items-center gap-4">
          <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300">
            <UserCircle2 className="h-8 w-8" />
          </div>
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Farmer profile</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Ravi Kumar</h1>
          </div>
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="flex items-center gap-2 text-slate-300"><Phone className="h-4 w-4 text-cyan-300" /> Contact</div>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>Phone: +91 98765 43210</li>
              <li>Email: ravi@krishix.in</li>
              <li>Village: Madanapalle</li>
            </ul>
          </div>

          <div className="rounded-3xl border border-white/10 bg-[#0d1020] p-5">
            <div className="flex items-center gap-2 text-slate-300"><MapPin className="h-4 w-4 text-emerald-300" /> Location</div>
            <ul className="mt-4 space-y-3 text-sm text-slate-300">
              <li>District: Chittoor</li>
              <li>State: Andhra Pradesh</li>
              <li>Coordinates: 13.55°N, 78.49°E</li>
            </ul>
          </div>
        </div>

        <div className="mt-6 rounded-3xl border border-white/10 bg-[#0d1020] p-5">
          <div className="flex items-center gap-2 text-slate-300"><ShieldCheck className="h-4 w-4 text-emerald-300" /> Trust & verification</div>
          <div className="mt-4 grid gap-4 md:grid-cols-3">
            <div className="rounded-2xl bg-white/5 p-4"><p className="text-sm text-slate-400">KYC</p><p className="mt-2 text-lg font-semibold text-white">Verified</p></div>
            <div className="rounded-2xl bg-white/5 p-4"><p className="text-sm text-slate-400">Lot history</p><p className="mt-2 text-lg font-semibold text-white">12 seasons</p></div>
            <div className="rounded-2xl bg-white/5 p-4"><p className="text-sm text-slate-400">Ratings</p><p className="mt-2 text-lg font-semibold text-white">4.8/5</p></div>
          </div>
        </div>
      </div>
    </div>
  );
}
