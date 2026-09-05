import React from 'react';
import { Link } from 'react-router-dom';
import { Wheat, ArrowRight, Route, ReceiptText, ShieldCheck } from 'lucide-react';

const pillars = [
  {
    icon: Route,
    title: 'Distance is priced in',
    body: 'A higher headline price 200 km away often loses to a fair price down the road. We do that maths for you.',
  },
  {
    icon: ReceiptText,
    title: 'Real net, not headline',
    body: 'Transport, commission and labour are deducted so you see what actually reaches your hand — per quintal.',
  },
  {
    icon: ShieldCheck,
    title: 'Feasibility, plainly',
    body: 'Every buyer is graded Executable, Recoverable or Not viable — with the reason spelled out.',
  },
];

const LandingPage: React.FC = () => (
  <div style={{ backgroundColor: 'var(--midnight)' }}>
    {/* Nav */}
    <header className="mx-auto flex max-w-content items-center justify-between px-5 py-5 md:px-8">
      <div className="flex items-center gap-3">
        <div
          className="flex h-10 w-10 items-center justify-center rounded-xl"
          style={{ background: 'linear-gradient(135deg, var(--indigo), var(--violet))' }}
        >
          <Wheat size={20} className="text-white" />
        </div>
        <span className="font-display text-xl">KrishiX</span>
      </div>
      <div className="flex items-center gap-2">
        <Link to="/login" className="btn btn-ghost btn-sm">Sign in</Link>
        <Link to="/register" className="btn btn-primary btn-sm">Get started</Link>
      </div>
    </header>

    {/* Hero */}
    <section className="relative mx-auto max-w-content px-5 pb-16 pt-8 md:px-8">
      <div className="relative overflow-hidden rounded-3xl border" style={{ borderColor: 'var(--border)' }}>
        <img src="/images/home-hero.png" alt="Golden-hour Indian farmland" className="h-[520px] w-full object-cover" />
        <div
          className="absolute inset-0"
          style={{ background: 'linear-gradient(180deg, rgba(8,11,20,0.25) 0%, rgba(8,11,20,0.55) 45%, rgba(8,11,20,0.95) 100%)' }}
        />
        <div className="absolute inset-x-0 bottom-0 p-8 md:p-14">
          <p className="text-eyebrow mb-5">Market intelligence for Indian growers</p>
          <h1 className="text-display max-w-3xl text-balance text-cream">
            Know where your crop earns more.
          </h1>
          <p className="mt-5 max-w-xl text-base leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
            KrishiX compares recent market prices, distance and selling costs, then tells you the one
            thing that matters: what actually lands in your hand.
          </p>
          <div className="mt-8 flex flex-wrap gap-3">
            <Link to="/register" className="btn btn-primary btn-lg">
              Start free <ArrowRight size={18} />
            </Link>
            <Link to="/login" className="btn btn-outline btn-lg">I have an account</Link>
          </div>
        </div>
      </div>
    </section>

    {/* Pillars */}
    <section className="mx-auto max-w-content px-5 pb-20 md:px-8">
      <div className="grid gap-5 md:grid-cols-3">
        {pillars.map(({ icon: Icon, title, body }) => (
          <div key={title} className="card card-hover p-7">
            <div
              className="mb-5 flex h-11 w-11 items-center justify-center rounded-xl"
              style={{ background: 'var(--indigo-soft)', color: '#b3a5ff' }}
            >
              <Icon size={20} strokeWidth={1.8} />
            </div>
            <h3 className="text-h4">{title}</h3>
            <p className="mt-2 text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{body}</p>
          </div>
        ))}
      </div>
    </section>

    {/* CTA */}
    <section className="mx-auto max-w-content px-5 pb-24 md:px-8">
      <div
        className="rounded-3xl px-8 py-14 text-center"
        style={{ background: 'linear-gradient(135deg, var(--aubergine), var(--surface))', border: '1px solid var(--border)' }}
      >
        <h2 className="text-h1 font-display text-balance">Stop guessing the best mandi.</h2>
        <p className="mx-auto mt-3 max-w-md text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>
          List your produce once. See every buyer ranked by real net price.
        </p>
        <Link to="/register" className="btn btn-primary btn-lg mt-7 inline-flex">
          Create your account <ArrowRight size={18} />
        </Link>
      </div>
    </section>

    <footer className="border-t py-8 text-center text-xs" style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
      © 2026 KrishiX · Market intelligence, not investment advice.
    </footer>
  </div>
);

export default LandingPage;
