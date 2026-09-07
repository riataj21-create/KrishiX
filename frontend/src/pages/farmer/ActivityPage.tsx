import React, { useEffect, useState } from 'react';
import { Activity, CheckCircle2, Clock3, Loader2 } from 'lucide-react';
import { transactionAPI, type Transaction } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const labels: Record<string, string> = {
  OFFER_ACCEPTED: 'Offer accepted',
  PICKUP_SCHEDULED: 'Pickup scheduled',
  DELIVERED: 'Produce delivered',
  PAYMENT_PENDING: 'Payment pending',
  BUYER_REPORTED_PAID: 'Payment reported',
  FARMER_CONFIRMED: 'Payment confirmed',
  PAYMENT_CONFIRMED: 'Payment confirmed',
};

export default function ActivityPage() {
  const toast = useToast();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [busyId, setBusyId] = useState<string | null>(null);

  useEffect(() => {
    transactionAPI.listTransactions()
      .then((result) => setTransactions(result.items))
      .catch((error: Error) => toast.error(error.message || 'Unable to load activity'))
      .finally(() => setLoading(false));
  }, [toast]);

  const updateTransaction = async (id: string, action: 'advance' | 'confirm' | 'dispute') => {
    setBusyId(id);
    try {
      const transaction = action === 'advance'
        ? await transactionAPI.advance(id)
        : await transactionAPI.confirmPayment(id, action === 'confirm', action === 'dispute' ? 'Farmer reported a payment issue.' : undefined);
      setTransactions((current) => current.map((item) => item.id === id ? transaction : item));
      toast.success(action === 'advance' ? 'Transaction advanced.' : action === 'confirm' ? 'Payment confirmation recorded.' : 'Payment issue recorded.');
    } catch (error) {
      toast.error(error instanceof Error ? error.message : 'Unable to update transaction');
    } finally {
      setBusyId(null);
    }
  };

  return <div className="page-container min-h-screen"><div className="mb-8 border-b border-white/10 pb-6"><p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">History</p><h1 className="mt-2 text-4xl font-semibold">Activity</h1><p className="mt-2 text-sm text-[#a9a8b3]">Follow actual offers, sales, delivery, and payment events.</p></div>{loading ? <div className="flex items-center gap-2 text-sm text-[#a9a8b3]"><Loader2 className="h-4 w-4 animate-spin" /> Loading activity...</div> : transactions.length === 0 ? <div className="border border-dashed border-white/15 bg-[#15182a] p-10 text-center"><Activity className="mx-auto h-7 w-7 text-[#8b5cf6]" /><p className="mt-3 text-lg font-medium">No activity yet</p><p className="mt-2 text-sm text-[#a9a8b3]">Your activity will appear here as you analyze opportunities and transact through KrishiX.</p></div> : <div className="space-y-5">{transactions.map((transaction) => <article key={transaction.id} className="border border-white/10 bg-[#15182a] p-5"><div className="flex flex-wrap items-center justify-between gap-3"><div><p className="text-lg font-semibold">Transaction</p><p className="mt-1 text-sm text-[#a9a8b3]">₹{transaction.agreed_price_per_quintal.toLocaleString('en-IN')}/q · {transaction.agreed_quantity} quintal</p></div><span className="rounded-full border border-white/10 px-2.5 py-1 text-xs text-[#a9a8b3]">{transaction.status}</span></div><div className="mt-5 space-y-3 border-l border-white/10 pl-4">{transaction.events.map((event) => <div key={event.id} className="relative"><span className="absolute -left-[1.35rem] top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-[#15182a] text-emerald-300">{labels[event.event_type] ? <CheckCircle2 className="h-4 w-4" /> : <Clock3 className="h-4 w-4" />}</span><p className="text-sm font-medium">{labels[event.event_type] || event.event_type}</p><p className="mt-1 text-xs text-[#a9a8b3]">{new Date(event.created_at).toLocaleString()}</p></div>)}</div><div className="mt-5 flex flex-wrap gap-2">{['accepted', 'pickup_scheduled', 'delivered'].includes(transaction.status) && <button onClick={() => updateTransaction(transaction.id, 'advance')} disabled={busyId === transaction.id} className="rounded-xl border border-violet-400/30 px-3 py-2 text-sm text-violet-200 disabled:opacity-50">{busyId === transaction.id ? 'Updating...' : 'Advance status'}</button>}{transaction.payment_status === 'buyer_reported_paid' && <><button onClick={() => updateTransaction(transaction.id, 'confirm')} disabled={busyId === transaction.id} className="rounded-xl border border-emerald-400/30 px-3 py-2 text-sm text-emerald-200 disabled:opacity-50">Confirm payment received</button><button onClick={() => updateTransaction(transaction.id, 'dispute')} disabled={busyId === transaction.id} className="rounded-xl border border-rose-400/30 px-3 py-2 text-sm text-rose-200 disabled:opacity-50">Report payment issue</button></>}</div>{transaction.disclaimer && <p className="mt-4 text-xs text-[#a9a8b3]">{transaction.disclaimer}</p>}</article>)}</div>}</div>;
}
