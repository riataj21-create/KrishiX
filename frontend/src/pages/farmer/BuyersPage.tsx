import React from 'react';
import { BriefcaseBusiness, ArrowRight, Users } from 'lucide-react';

const buyers = [
  { name: 'Nellore Fresh Foods', crop: 'Tomato', price: '₹3,400 / q', payment: '7 days', fit: 'High fit' },
  { name: 'A.P. Agri Co-op', crop: 'Tomato', price: '₹3,220 / q', payment: '5 days', fit: 'Medium fit' },
  { name: 'Vijayawada Traders', crop: 'Tomato', price: '₹3,100 / q', payment: '3 days', fit: 'Strong fallback' },
];

export default function BuyersPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl rounded-3xl border border-white/10 bg-[#101827] p-6">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Buyers</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Buyer discovery</h1>
          </div>
          <div className="rounded-full border border-white/10 bg-black/10 p-2 text-slate-300"><Users className="h-4 w-4" /></div>
        </div>

        <div className="space-y-4">
          {buyers.map((buyer) => (
            <div key={buyer.name} className="flex flex-col gap-4 rounded-3xl border border-white/10 bg-[#0d1020] p-5 md:flex-row md:items-center md:justify-between">
              <div className="flex items-center gap-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-2xl bg-violet-500/10 text-violet-300"><BriefcaseBusiness className="h-5 w-5" /></div>
                <div>
                  <p className="text-lg font-semibold text-white">{buyer.name}</p>
                  <p className="text-sm text-slate-300">{buyer.crop} · {buyer.fit}</p>
                </div>
              </div>
              <div className="flex flex-wrap items-center gap-4 text-sm text-slate-300">
                <span>Offer: <span className="font-medium text-white">{buyer.price}</span></span>
                <span>Payment: <span className="font-medium text-white">{buyer.payment}</span></span>
                <button className="inline-flex items-center gap-2 rounded-full border border-violet-400/30 bg-violet-500/10 px-3 py-1.5 text-violet-200">
                  Contact <ArrowRight className="h-4 w-4" />
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
