import Link from "next/link";
import { ArrowRight, BarChart3, Check, MapPin, TrendingUp } from "lucide-react";
import CTASection from "@/components/CTASection";

const features = [
  { icon: MapPin,    title: "Location-aware", text: "Move from state to district to market without losing context." },
  { icon: BarChart3, title: "Comparable",      text: "See modal, minimum and maximum prices side by side." },
  { icon: TrendingUp,title: "Understandable",  text: "Follow recent price movement with clear historical views." },
];

export default function Home() {
  return (
    <div>
      {/* Hero */}
      <section className="border-b border-[var(--border)] bg-[var(--surface-subtle)] px-5 py-16 sm:px-8 md:py-24">
        <div className="mx-auto grid max-w-6xl items-center gap-12 md:grid-cols-[1.1fr_0.9fr]">
          <div className="space-y-6">
            <p className="text-sm font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
              KrishiX market intelligence
            </p>
            <h1 className="text-h1 max-w-2xl leading-tight">
              Know the market before you make the move.
            </h1>
            <p className="max-w-xl text-lg leading-8 text-[var(--text-secondary)]">
              Reliable, location-specific market reports that help farmers compare
              opportunities and make clearer selling decisions.
            </p>
            <div className="flex flex-wrap gap-3 pt-2">
              <Link href="/auth/register" className="btn-primary">
                Create a free account <ArrowRight size={16} />
              </Link>
              <Link href="#features" className="btn-outline">
                Explore the product
              </Link>
            </div>
            <p className="flex items-center gap-2 text-sm text-[var(--text-secondary)]">
              <Check size={15} className="text-[var(--accent)]" />
              Latest available data, with source and timestamp
            </p>
          </div>

          {/* Mockup price card */}
          <div className="rounded-md border border-[var(--border)] bg-white p-6">
            <div className="flex items-start justify-between border-b border-[var(--border)] pb-5">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.12em] text-[var(--text-muted)]">
                  Market view
                </p>
                <p className="mt-1 text-sm font-medium">Ludhiana, Punjab</p>
              </div>
              <span className="badge-warning">Latest available</span>
            </div>
            <div className="py-7">
              <p className="text-sm text-[var(--text-secondary)]">Tomato · Ludhiana Central Market</p>
              <p className="mt-2 text-4xl font-semibold tracking-tight">
                ₹2,850{" "}
                <span className="text-base font-normal text-[var(--text-secondary)]">/ quintal</span>
              </p>
              <p className="mt-3 text-sm font-medium text-[var(--success)]">
                +4.8%{" "}
                <span className="font-normal text-[var(--text-secondary)]">
                  vs previous available report
                </span>
              </p>
            </div>
            <div className="border-t border-[var(--border)] pt-4 text-xs text-[var(--text-muted)]">
              Source: APMC report · Indicative only
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section id="features" className="px-5 py-16 sm:px-8 md:py-24">
        <div className="mx-auto max-w-6xl">
          <div className="mb-12 max-w-2xl">
            <p className="mb-3 text-sm font-semibold uppercase tracking-[0.14em] text-[var(--accent)]">
              One clear view
            </p>
            <h2 className="text-h2 mb-4">The information you need, in one place.</h2>
            <p className="text-lg text-[var(--text-secondary)]">
              A focused workspace for finding, comparing and following agricultural market data.
            </p>
          </div>
          <div className="grid gap-px overflow-hidden border border-[var(--border)] bg-[var(--border)] md:grid-cols-3">
            {features.map(({ icon: Icon, title, text }) => (
              <div key={title} className="bg-white p-6">
                <Icon className="mb-6 h-5 w-5 text-[var(--accent)]" />
                <h3 className="text-h5 mb-2">{title}</h3>
                <p className="text-[var(--text-secondary)]">{text}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Mid-page CTA strip */}
      <section className="border-y border-[var(--border)] bg-white px-5 py-14 sm:px-8">
        <div className="mx-auto flex max-w-6xl flex-col justify-between gap-6 sm:flex-row sm:items-center">
          <div>
            <h2 className="text-h4">Built for confident decisions.</h2>
            <p className="mt-2 max-w-xl text-sm leading-6 text-[var(--text-secondary)]">
              Every price includes context. Compare the numbers, check the freshness,
              then decide what works for you.
            </p>
          </div>
          <Link href="/auth/register" className="btn-primary self-start sm:self-auto">
            Start exploring <ArrowRight size={16} />
          </Link>
        </div>
      </section>

      {/* Full-width CTA footer banner */}
      <CTASection />
    </div>
  );
}
