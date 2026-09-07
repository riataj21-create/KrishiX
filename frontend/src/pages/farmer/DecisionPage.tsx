import React, { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { ArrowLeft, CheckCircle2, Loader2, MapPinned, ShieldAlert, Sparkles } from 'lucide-react';
import { commodityAPI, lotAPI, type Commodity, type Opportunity } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const today = new Date().toISOString().slice(0, 10);

function money(value?: number | null) {
  return value == null ? 'Not available' : `₹${Math.round(value).toLocaleString('en-IN')}`;
}

export default function DecisionPage() {
  const toast = useToast();
  const [commodities, setCommodities] = useState<Commodity[]>([]);
  const [loadingCommodities, setLoadingCommodities] = useState(true);
  const [submitting, setSubmitting] = useState(false);
  const [opportunities, setOpportunities] = useState<Opportunity[]>([]);
  const [recommendation, setRecommendation] = useState('');
  const [dataCaveat, setDataCaveat] = useState('');
  const [form, setForm] = useState({
    commodity_id: '',
    quantity: '0.8',
    state: 'Andhra Pradesh',
    district: 'Madanapalle',
    village: '',
    quality_grade: 'Grade B',
    available_from: today,
    sell_by: today,
    minimum_price: '2800',
    max_payment_days: '2',
    latitude: '13.5504',
    longitude: '78.5024',
    preferred_payment_method: 'bank_transfer',
  });

  useEffect(() => {
    commodityAPI.listCommodities(undefined, 100)
      .then((result) => {
        setCommodities(result.items);
        if (result.items[0]) setForm((current) => ({ ...current, commodity_id: result.items[0].id }));
      })
      .catch((error: Error) => toast.error(error.message || 'Unable to load commodities'))
      .finally(() => setLoadingCommodities(false));
  }, [toast]);

  const update = (key: keyof typeof form, value: string) => setForm((current) => ({ ...current, [key]: value }));

  const submit = async (event: React.FormEvent) => {
    event.preventDefault();
    setSubmitting(true);
    setOpportunities([]);
    try {
      const lot = await lotAPI.createLot({
        commodity_id: form.commodity_id,
        quantity: Number(form.quantity),
        unit: 'quintal',
        state: form.state,
        district: form.district,
        village: form.village || null,
        latitude: form.latitude ? Number(form.latitude) : null,
        longitude: form.longitude ? Number(form.longitude) : null,
        quality_grade: form.quality_grade || null,
        quality_status: null,
        quality_notes: null,
        available_from: form.available_from,
        sell_by: form.sell_by,
        minimum_price: form.minimum_price ? Number(form.minimum_price) : null,
        max_payment_days: Number(form.max_payment_days),
        preferred_payment_method: form.preferred_payment_method,
        transport_preference: null,
        max_transport_budget: null,
      });
      const result = await lotAPI.analyzeOpportunities(lot.id);
      setOpportunities(result.items);
      setRecommendation(result.recommendation);
      setDataCaveat(result.data_caveat);
      toast.success('Lot analyzed against current opportunities');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to analyze this lot');
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#080b14] p-6 text-slate-100">
      <div className="mx-auto max-w-7xl">
        <div className="mb-6 flex items-center gap-3 text-sm text-slate-300">
          <Link to="/dashboard" className="inline-flex items-center gap-2 rounded-full border border-white/10 px-3 py-1.5 hover:bg-white/5">
            <ArrowLeft className="h-4 w-4" /> Back to dashboard
          </Link>
        </div>

        <div className="grid gap-6 xl:grid-cols-[0.85fr_1.15fr]">
          <section className="rounded-3xl border border-white/10 bg-[#101827] p-6">
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Farmer lot</p>
            <h1 className="mt-3 text-3xl font-semibold text-white">Find an executable sale</h1>
            <p className="mt-2 text-sm leading-6 text-slate-300">Enter the lot exactly as it exists. KrishiX will compare it with buyer requirements and market prices.</p>

            <form onSubmit={submit} className="mt-6 space-y-4">
              <label className="block text-sm text-slate-300">Commodity
                <select className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" value={form.commodity_id} onChange={(event) => update('commodity_id', event.target.value)} required disabled={loadingCommodities || submitting}>
                  {loadingCommodities && <option>Loading commodities...</option>}
                  {commodities.map((commodity) => <option key={commodity.id} value={commodity.id}>{commodity.name}</option>)}
                </select>
              </label>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm text-slate-300">Quantity (quintal)
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" type="number" min="0.01" step="0.01" value={form.quantity} onChange={(event) => update('quantity', event.target.value)} required />
                </label>
                <label className="block text-sm text-slate-300">Quality grade
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" value={form.quality_grade} onChange={(event) => update('quality_grade', event.target.value)} />
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm text-slate-300">State
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" value={form.state} onChange={(event) => update('state', event.target.value)} required />
                </label>
                <label className="block text-sm text-slate-300">District
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" value={form.district} onChange={(event) => update('district', event.target.value)} required />
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm text-slate-300">Available from
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" type="date" value={form.available_from} onChange={(event) => update('available_from', event.target.value)} required />
                </label>
                <label className="block text-sm text-slate-300">Sell by
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" type="date" value={form.sell_by} onChange={(event) => update('sell_by', event.target.value)} required />
                </label>
              </div>

              <div className="grid gap-4 sm:grid-cols-2">
                <label className="block text-sm text-slate-300">Minimum price (₹/quintal)
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" type="number" min="0" value={form.minimum_price} onChange={(event) => update('minimum_price', event.target.value)} />
                </label>
                <label className="block text-sm text-slate-300">Maximum payment days
                  <input className="mt-2 w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-white outline-none focus:border-violet-400" type="number" min="0" max="90" value={form.max_payment_days} onChange={(event) => update('max_payment_days', event.target.value)} required />
                </label>
              </div>

              <div className="rounded-2xl border border-white/10 bg-black/10 p-4">
                <p className="mb-3 flex items-center gap-2 text-sm font-medium text-white"><MapPinned className="h-4 w-4 text-cyan-300" /> Optional GPS location</p>
                <div className="grid gap-4 sm:grid-cols-2">
                  <input aria-label="Latitude" className="w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-sm text-white outline-none focus:border-violet-400" placeholder="Latitude" value={form.latitude} onChange={(event) => update('latitude', event.target.value)} />
                  <input aria-label="Longitude" className="w-full rounded-xl border border-white/10 bg-[#0d1020] px-3 py-3 text-sm text-white outline-none focus:border-violet-400" placeholder="Longitude" value={form.longitude} onChange={(event) => update('longitude', event.target.value)} />
                </div>
              </div>

              <button type="submit" className="inline-flex w-full items-center justify-center gap-2 rounded-xl bg-[#5b4bdb] px-4 py-3 font-medium text-white transition hover:bg-[#6b5ce7] disabled:cursor-not-allowed disabled:opacity-50" disabled={submitting || loadingCommodities || !form.commodity_id}>
                {submitting ? <><Loader2 className="h-4 w-4 animate-spin" /> Analyzing...</> : 'Analyze selling options'}
              </button>
            </form>
          </section>

          <section className="rounded-3xl border border-white/10 bg-[#101827] p-6">
            <p className="text-xs uppercase tracking-[0.18em] text-violet-300">Decision engine</p>
            <h2 className="mt-3 text-2xl font-semibold text-white">Feasibility results</h2>
            {!opportunities.length ? (
              <div className="mt-6 rounded-2xl border border-dashed border-white/15 bg-[#0d1020] p-8 text-center">
                <Sparkles className="mx-auto h-8 w-8 text-violet-300" />
                <p className="mt-3 font-medium text-white">Your result will appear here</p>
                <p className="mt-2 text-sm text-slate-400">The engine checks quantity, grade, timing, payment terms, price, and available recovery options.</p>
              </div>
            ) : (
              <>
                <div className="mt-5 rounded-2xl border border-emerald-500/20 bg-emerald-500/10 p-4 text-sm text-emerald-100">{recommendation}</div>
                <div className="mt-5 space-y-4">
                  {opportunities.map((opportunity) => (
                    <article key={opportunity.id} className="rounded-2xl border border-white/10 bg-[#0d1020] p-5">
                      <div className="flex flex-wrap items-start justify-between gap-3">
                        <div>
                          <p className="text-lg font-semibold text-white">{opportunity.title || opportunity.opportunity_type}</p>
                          <p className="mt-1 text-sm text-slate-400">{opportunity.source_type} · {opportunity.data_quality || 'Data quality not specified'}</p>
                        </div>
                        <span className={`rounded-full border px-2.5 py-1 text-xs font-medium ${opportunity.feasibility_decision === 'EXECUTABLE' ? 'border-emerald-400/30 bg-emerald-500/10 text-emerald-300' : opportunity.feasibility_decision === 'RECOVERABLE' ? 'border-amber-400/30 bg-amber-500/10 text-amber-300' : 'border-rose-400/30 bg-rose-500/10 text-rose-300'}`}>{opportunity.feasibility_decision}</span>
                      </div>
                      <div className="mt-4 grid gap-3 sm:grid-cols-2">
                        <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-slate-400">Offered price</p><p className="mt-1 font-semibold text-white">{money(opportunity.offered_price)}</p></div>
                        <div className="rounded-xl bg-white/5 p-3"><p className="text-xs text-slate-400">Estimated net</p><p className="mt-1 font-semibold text-white">{money(opportunity.estimated_net_realization)}</p></div>
                      </div>
                      {opportunity.explanation && <p className="mt-4 text-sm leading-6 text-slate-300">{opportunity.explanation}</p>}
                      {!!opportunity.blocking_constraints.length && <p className="mt-3 flex items-start gap-2 text-sm text-rose-200"><ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" /> Blocking: {opportunity.blocking_constraints.join(', ')}</p>}
                      {!!opportunity.minimum_viable_changes.length && <div className="mt-4 border-t border-white/10 pt-4"><p className="mb-2 text-sm font-medium text-white">Minimum viable changes</p>{opportunity.minimum_viable_changes.map((change, index) => <p key={index} className="flex items-start gap-2 text-sm text-slate-300"><CheckCircle2 className="mt-0.5 h-4 w-4 shrink-0 text-emerald-300" /> {change.description || 'Review the recommended recovery action'}</p>)}</div>}
                    </article>
                  ))}
                </div>
                <p className="mt-5 text-xs leading-5 text-slate-500">{dataCaveat}</p>
              </>
            )}
          </section>
        </div>
      </div>
    </div>
  );
}
