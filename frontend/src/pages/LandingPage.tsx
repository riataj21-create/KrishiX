import React from 'react';
import { Link } from 'react-router-dom';
import { ArrowRight, BarChart3, MapPin, TrendingUp } from 'lucide-react';

const features = [
  { icon: MapPin, title: 'Location-aware', text: 'Move from state to district to market without losing context.' },
  { icon: BarChart3, title: 'Net realization', text: 'See actual ₹ in hand after transport and mandi charges — not just listed price.' },
  { icon: TrendingUp, title: 'Timing intelligence', text: 'Evidence-based signals on whether to sell now or wait.' },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--background)]">
      {/* Nav */}
      <header className="border-b border-[var(--border)] bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
          <div className="flex items-center gap-2.5">
            <span className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--accent)] text-sm font-bold text-white">K</span>
            <span className="text-[15px] font-semibold tracking-tight">KrishiX</span>
          </div>
          <div className="flex items-center gap-4">
            <Link to="/login" className="text-sm text-[var(--text-secondary)] hover:text-[var(--text-primary)]">Sign in</Link>
            <Link to="/register" className="btn-primary btn-sm">Get started</Link>
          </div>
        </div>
      </header>

      {/* Hero */}
      <section className="border-b border-[var(--border)] bg-[var(--surface-subtle)] px-5 py-16 sm:px-8 md:py-24">
        <div className="mx-auto max-w-6xl">
          <p className="mb-4 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
            KrishiX — Market Intelligence
          </p>
          <h1 className="text-h1 mb-6 max-w-3xl leading-tight">
            Know exactly where, when, and who to sell to.
          </h1>
          <p className="mb-8 max-w-xl text-lg leading-8 text-[var(--text-secondary)]">
            Fragmented market data converted into a single ranked selling recommendation —
            with the actual rupees you'll receive after all costs.
          </p>
          <div className="flex flex-wrap gap-3">
            <Link to="/register" className="btn-primary">
              Create a free account <ArrowRight size={16} />
            </Link>
            <Link to="/login" className="btn-outline">Sign in</Link>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="px-5 py-16 sm:px-8 md:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12">
            <h2 className="text-h2 mb-4">Three questions. One platform.</h2>
            <p className="text-lg text-[var(--text-secondary)]">
              WHERE should I sell? &nbsp;·&nbsp; WHEN should I sell? &nbsp;·&nbsp; WHO should I sell to?
            </p>
          </div>
          <div className="grid gap-px overflow-hidden border border-[var(--border)] bg-[var(--border)] md:grid-cols-3">
            {features.map(({ icon: Icon, title, text }) => (
              <div key={title} className="bg-white p-6">
                <Icon className="mb-4 h-5 w-5 text-[var(--accent)]" />
                <h3 className="text-h5 mb-2">{title}</h3>
                <p className="text-sm text-[var(--text-secondary)]">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA */}
      <section className="border-t border-[var(--border)] bg-[var(--accent)] px-5 py-14 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-col justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-h4 text-white">Built for confident decisions.</h2>
            <p className="mt-2 text-sm text-white/70">
              Every cost assumption labelled. Every price dated. No magic numbers.
            </p>
          </div>
          <Link to="/register" className="btn bg-white text-[var(--accent)] hover:bg-[var(--primary-light)] self-start sm:self-auto">
            Start for free <ArrowRight size={16} />
          </Link>
        </div>
      </section>
    </div>
  );
}
