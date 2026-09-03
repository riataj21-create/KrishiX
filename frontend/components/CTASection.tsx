/**
 * Call-to-Action Section Component
 */

import Link from "next/link";
import { ArrowRight } from "lucide-react";

export default function CTASection() {
  return (
    <section className="px-6 py-20 md:py-24 bg-primary text-white">
      <div className="mx-auto max-w-4xl text-center">
        <h2 className="text-h2 text-white mb-4">Ready to Access Market Intelligence?</h2>
        <p className="text-lg text-neutral-100 mb-8 max-w-2xl mx-auto">
          Join farmers across India who make smarter selling decisions with KrishiX. Sign up free today.
        </p>
        <div className="flex gap-4 justify-center flex-wrap">
          <Link href="/auth/register" className="btn bg-white text-primary hover:bg-neutral-100">
            Sign Up Free
            <ArrowRight className="ml-2 w-4 h-4" />
          </Link>
          <a
            href="#"
            className="btn border-2 border-white text-white hover:bg-white/10"
          >
            View Demo
          </a>
        </div>
      </div>
    </section>
  );
}
