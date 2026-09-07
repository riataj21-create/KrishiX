import React, { useEffect, useState } from 'react';
import {
  Activity, CheckCircle2, Clock3, Loader2,
  Package, Truck, Wallet, XCircle,
} from 'lucide-react';
import { transactionAPI, type Transaction } from '../../lib/api';
import { useToast } from '../../context/ToastContext';

const EVENT_LABELS: Record<string, string> = {
  OFFER_ACCEPTED:      'Offer accepted',
  PICKUP_SCHEDULED:    'Pickup scheduled',
  DELIVERED:           'Produce delivered',
  PAYMENT_PENDING:     'Payment pending',
  BUYER_REPORTED_PAID: 'Buyer reported payment',
  FARMER_CONFIRMED:    'Payment confirmed by farmer',
  PAYMENT_CONFIRMED:   'Payment confirmed',
  PAYMENT_DISPUTED:    'Payment disputed',
};

const STATUS_NEXT: Record<string, { label: string; icon: React.ReactNode }> = {
  accepted:         { label: 'Confirm pickup scheduled', icon: <Truck className="h-4 w-4" /> },
  pickup_scheduled: { label: 'Confirm delivered',        icon: <Package className="h-4 w-4" /> },
};

export default function ActivityPage() {
  const toast = useToast();
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loading, setLoading] = useState(true);
  const [acting, setActing] = useState<string | null>(null);

  const refresh = () => {
    transactionAPI.listTransactions()
      .then(r => setTransactions(r.items))
      .catch((err: Error) => toast.error(err.message))
      .finally(() => setLoading(false));
  };

  useEffect(() => { refresh(); }, []);

  const advance = async (txnId: string) => {
    setActing(txnId + ':advance');
    try {
      const updated = await transactionAPI.advance(txnId);
      setTransactions(prev => prev.map(t => t.id === txnId ? updated : t));
      toast.success('Status updated.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to advance');
    } finally { setActing(null); }
  };

  const reportPayment = async (txnId: string) => {
    setActing(txnId + ':report');
    try {
      const updated = await transactionAPI.reportPayment(txnId, undefined, true);
      setTransactions(prev => prev.map(t => t.id === txnId ? updated : t));
      toast.success('Payment reported. Ask the farmer to confirm.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed to report payment');
    } finally { setActing(null); }
  };

  const confirmPayment = async (txnId: string, confirmed: boolean) => {
    setActing(txnId + ':confirm');
    try {
      const updated = await transactionAPI.confirmPayment(txnId, confirmed);
      setTransactions(prev => prev.map(t => t.id === txnId ? updated : t));
      toast.success(confirmed ? 'Payment confirmed — transaction complete!' : 'Payment disputed.');
    } catch (err) {
      toast.error(err instanceof Error ? err.message : 'Failed');
    } finally { setActing(null); }
  };

  return (
    <div className="page-container min-h-screen">
      <div className="mb-8 border-b border-white/10 pb-6">
        <p className="text-xs uppercase tracking-[0.18em] text-[#8b5cf6]">History</p>
        <h1 className="mt-2 text-4xl font-semibold">Activity</h1>
        <p className="mt-2 text-sm text-[#a9a8b3]">Track offers, delivery, and payment for every transaction.</p>
      </div>

      {loading ? (
        <div className="flex items-center gap-2 text-sm text-[#a9a8b3]">
          <Loader2 className="h-4 w-4 animate-spin" /> Loading activity...
        </div>
      ) : transactions.length === 0 ? (
        <div className="border border-dashed border-white/15 bg-[#15182a] p-10 text-center">
          <Activity className="mx-auto h-7 w-7 text-[#8b5cf6]" />
          <p className="mt-3 text-lg font-medium">No activity yet</p>
          <p className="mt-2 text-sm text-[#a9a8b3]">Your activity will appear here once you accept an offer.</p>
        </div>
      ) : (
        <div className="space-y-6">
          {transactions.map(txn => (
            <TransactionCard
              key={txn.id}
              txn={txn}
              acting={acting}
              onAdvance={() => advance(txn.id)}
              onReportPayment={() => reportPayment(txn.id)}
              onConfirmPayment={(confirmed) => confirmPayment(txn.id, confirmed)}
            />
          ))}
        </div>
      )}
    </div>
  );
}

function TransactionCard({
  txn, acting, onAdvance, onReportPayment, onConfirmPayment,
}: {
  txn: Transaction;
  acting: string | null;
  onAdvance: () => void;
  onReportPayment: () => void;
  onConfirmPayment: (confirmed: boolean) => void;
}) {
  const nextAction = STATUS_NEXT[txn.status];
  const isPaymentPending = txn.status === 'payment_pending' || txn.payment_status === 'payment_pending';
  const buyerReported = txn.payment_status === 'buyer_reported_paid';
  const isComplete = txn.status === 'completed';
  const isDisputed = txn.is_disputed || txn.status === 'disputed';
  const actingKey = acting?.startsWith(txn.id) ? acting.split(':')[1] : null;

  return (
    <article className={`border bg-[#15182a] p-5 ${isComplete ? 'border-emerald-400/30' : isDisputed ? 'border-rose-400/30' : 'border-white/10'}`}>
      {/* Header */}
      <div className="flex flex-wrap items-center justify-between gap-3">
        <div>
          <p className="text-lg font-semibold">
            ₹{txn.agreed_price_per_quintal.toLocaleString('en-IN')}/q · {txn.agreed_quantity} quintal
          </p>
          <p className="mt-1 text-sm text-[#a9a8b3]">
            Payment within {txn.agreed_payment_days === 0 ? 'same day' : `${txn.agreed_payment_days} days`}
          </p>
        </div>
        <StatusBadge status={txn.status} paymentStatus={txn.payment_status} />
      </div>

      {/* Payment info */}
      {txn.payment && (
        <div className="mt-4 border border-white/10 bg-[#0d1020] p-3 text-xs text-[#a9a8b3]">
          <p>Amount: <strong className="text-white">₹{txn.payment.payment_amount.toLocaleString('en-IN')}</strong></p>
          <p className="mt-1">Due: <strong className="text-white">{txn.payment.payment_due_date}</strong></p>
          {txn.payment.disclaimer && (
            <p className="mt-2 italic">{txn.payment.disclaimer}</p>
          )}
        </div>
      )}

      {/* Action buttons */}
      <div className="mt-5 flex flex-wrap gap-3">
        {/* Advance lifecycle */}
        {nextAction && !isComplete && !isDisputed && (
          <button
            onClick={onAdvance}
            disabled={actingKey === 'advance'}
            className="btn-primary flex items-center gap-2 text-sm"
          >
            {actingKey === 'advance' ? <Loader2 className="h-4 w-4 animate-spin" /> : nextAction.icon}
            {nextAction.label}
          </button>
        )}

        {/* Report payment (demo: farmer acts as buyer) */}
        {isPaymentPending && !buyerReported && !isComplete && !isDisputed && (
          <button
            onClick={onReportPayment}
            disabled={actingKey === 'report'}
            className="flex items-center gap-2 rounded border border-[#d6a84f]/30 bg-[#d6a84f]/10 px-4 py-2 text-sm text-[#d6a84f] hover:bg-[#d6a84f]/20 disabled:opacity-50"
          >
            {actingKey === 'report' ? <Loader2 className="h-4 w-4 animate-spin" /> : <Wallet className="h-4 w-4" />}
            Report payment (demo)
          </button>
        )}

        {/* Confirm or dispute payment */}
        {buyerReported && !isComplete && !isDisputed && (
          <>
            <button
              onClick={() => onConfirmPayment(true)}
              disabled={actingKey === 'confirm'}
              className="flex items-center gap-2 rounded border border-emerald-400/30 bg-emerald-500/10 px-4 py-2 text-sm text-emerald-300 hover:bg-emerald-500/20 disabled:opacity-50"
            >
              {actingKey === 'confirm' ? <Loader2 className="h-4 w-4 animate-spin" /> : <CheckCircle2 className="h-4 w-4" />}
              Confirm payment received
            </button>
            <button
              onClick={() => onConfirmPayment(false)}
              disabled={actingKey === 'confirm'}
              className="flex items-center gap-2 rounded border border-rose-400/30 bg-rose-500/10 px-4 py-2 text-sm text-rose-300 hover:bg-rose-500/20 disabled:opacity-50"
            >
              <XCircle className="h-4 w-4" /> Dispute
            </button>
          </>
        )}
      </div>

      {/* Event log */}
      {txn.events?.length > 0 && (
        <div className="mt-5 space-y-2 border-l border-white/10 pl-4">
          {txn.events.map(event => (
            <div key={event.id} className="relative">
              <span className="absolute -left-[1.35rem] top-0.5 flex h-5 w-5 items-center justify-center rounded-full bg-[#15182a]">
                {event.event_type.includes('CONFIRMED') || event.event_type.includes('ACCEPTED')
                  ? <CheckCircle2 className="h-4 w-4 text-emerald-300" />
                  : <Clock3 className="h-4 w-4 text-[#a9a8b3]" />}
              </span>
              <p className="text-sm font-medium">{EVENT_LABELS[event.event_type] ?? event.event_type}</p>
              <p className="mt-0.5 text-xs text-[#a9a8b3]">{new Date(event.created_at).toLocaleString('en-IN')}</p>
            </div>
          ))}
        </div>
      )}
    </article>
  );
}

function StatusBadge({ status, paymentStatus }: { status: string; paymentStatus: string }) {
  const map: Record<string, string> = {
    accepted: 'border-blue-400/30 text-blue-300',
    pickup_scheduled: 'border-amber-400/30 text-amber-300',
    payment_pending: 'border-amber-400/30 text-amber-300',
    buyer_reported_paid: 'border-[#d6a84f]/30 text-[#d6a84f]',
    completed: 'border-emerald-400/30 text-emerald-300',
    disputed: 'border-rose-400/30 text-rose-300',
  };
  const key = status === 'payment_pending' ? paymentStatus || status : status;
  const cls = map[key] ?? 'border-white/20 text-[#a9a8b3]';
  return (
    <span className={`rounded-full border px-2.5 py-1 text-xs capitalize ${cls}`}>
      {key.replace(/_/g, ' ')}
    </span>
  );
}
