/**
 * User Login Page
 */

"use client";

import { useState, useEffect, Suspense } from "react";
import Link from "next/link";
import { useRouter, useSearchParams } from "next/navigation";
import { AlertCircle, CheckCircle, Loader2 } from "lucide-react";

// Inner component — uses useSearchParams, must be inside <Suspense>
function LoginForm() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const searchParams = useSearchParams();

  useEffect(() => {
    if (searchParams.get("registered")) {
      setSuccess("Account created successfully! Please log in.");
    }
  }, [searchParams]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setSuccess("");
    setLoading(true);

    if (!email || !password) {
      setError("Email and password are required");
      setLoading(false);
      return;
    }

    try {
      const { authAPI } = await import("@/lib/api");
      const data = await authAPI.login(email, password);
      localStorage.setItem("access_token", data.access_token);
      localStorage.setItem("token_type", data.token_type);
      router.push("/dashboard");
    } catch {
      setError("Invalid email or password");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center px-6 py-12 bg-neutral-50">
      <div className="w-full max-w-md">
        <div className="card">
          <div className="card-body">
            <h1 className="text-h3 text-center mb-2">Log In</h1>
            <p className="text-center text-neutral-600 text-sm mb-6">
              Access your KrishiX account
            </p>

            {error && (
              <div className="bg-danger/10 border border-danger/30 text-danger px-4 py-3 rounded-lg flex gap-3 mb-6">
                <AlertCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{error}</p>
              </div>
            )}

            {success && (
              <div className="bg-success/10 border border-success/30 text-success px-4 py-3 rounded-lg flex gap-3 mb-6">
                <CheckCircle className="w-5 h-5 flex-shrink-0 mt-0.5" />
                <p className="text-sm">{success}</p>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4">
              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Email Address
                </label>
                <input
                  type="email"
                  className="input"
                  placeholder="you@example.com"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  disabled={loading}
                  autoComplete="email"
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-neutral-700 mb-2">
                  Password
                </label>
                <input
                  type="password"
                  className="input"
                  placeholder="Your password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  disabled={loading}
                  autoComplete="current-password"
                />
              </div>

              <button
                type="submit"
                className="btn-primary w-full"
                disabled={loading}
              >
                {loading ? (
                  <><Loader2 className="w-4 h-4 animate-spin" /> Logging in...</>
                ) : (
                  "Log In"
                )}
              </button>
            </form>

            <p className="text-center text-neutral-600 text-sm mt-6">
              Don&apos;t have an account?{" "}
              <Link href="/auth/register" className="text-primary font-medium hover:text-primary-dark">
                Sign Up
              </Link>
            </p>
          </div>
        </div>

        <div className="mt-6 p-4 bg-neutral-100 rounded-lg border border-neutral-200">
          <p className="text-xs text-neutral-600 mb-2">
            <strong>Demo Account:</strong>
          </p>
          <p className="text-xs text-neutral-600">
            Email: farmer1@krishix.com
            <br />
            Password: password123
          </p>
        </div>
      </div>
    </div>
  );
}

// Suspense boundary required by Next.js 14 when using useSearchParams
export default function LoginPage() {
  return (
    <Suspense fallback={
      <div className="min-h-screen flex items-center justify-center">
        <Loader2 className="w-6 h-6 animate-spin text-primary" />
      </div>
    }>
      <LoginForm />
    </Suspense>
  );
}
