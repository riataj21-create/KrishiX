import React from 'react';
import { ArrowDownUp, Check } from 'lucide-react';

const comparison = [
  { metric: 'Price / quintal', mandi: '₹2,700', fpo: '₹2,880', direct: '₹2,950' },
  { metric: 'Transport cost', mandi: '₹980', fpo: '₹620', direct: '₹1,120' },
  { metric: 'Payment window', mandi: '2 days', fpo: '5 days', direct: '7 days' },
  { metric: 'Feasibility risk', mandi: 'Low', fpo: 'Low', direct: 'Medium' },
];

export default function ComparisonPage() {
  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-6xl">
        <div className="mb-6 flex items-center justify-between rounded-3xl border border-white/10 bg-[#101827] p-5">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Compare</p>
            <h1 className="mt-2 text-3xl font-semibold text-white">Channel comparison</h1>
          </div>
          <div className="rounded-full border border-white/10 bg-black/10 p-2 text-slate-300"><ArrowDownUp className="h-4 w-4" /></div>
        </div>

        <div className="overflow-hidden rounded-3xl border border-white/10 bg-[#0d1020]">
          <table className="w-full border-collapse text-left text-sm text-slate-300">
            <thead className="bg-[#121a2c] text-slate-300">
              <tr>
                <th className="px-5 py-4 font-medium">Metric</th>
                <th className="px-5 py-4 font-medium">Mandi</th>
                <th className="px-5 py-4 font-medium">FPO</th>
                <th className="px-5 py-4 font-medium">Direct buyer</th>
              </tr>
            </thead>
            <tbody>
              {comparison.map((row) => (
                <tr key={row.metric} className="border-t border-white/10">
                  <td className="px-5 py-4 text-white">{row.metric}</td>
                  <td className="px-5 py-4">{row.mandi}</td>
                  <td className="px-5 py-4">{row.fpo}</td>
                  <td className="px-5 py-4">{row.direct}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="mt-6 rounded-3xl border border-emerald-500/20 bg-emerald-500/10 p-5 text-sm text-emerald-100">
          <div className="flex items-center gap-2 font-medium"><Check className="h-4 w-4" /> Best executable option</div>
          <p className="mt-2">Direct buyer still gives the strongest net price, but the FPO offers the cleanest risk balanced with faster pickup.</p>
        </div>
      </div>
    </div>
  );
}
