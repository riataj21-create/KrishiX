"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { BarChart3, Bookmark, LayoutDashboard, Leaf, LogOut, Menu, Search, UserRound, X } from "lucide-react";
import { useState, useEffect } from "react";
import { farmerProfileAPI } from "@/lib/api";

const navigation = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/search", label: "Markets", icon: Search },
  { href: "/comparison", label: "Price comparison", icon: BarChart3 },
  { href: "/trends", label: "Commodities", icon: Leaf },
  { href: "/saved", label: "Saved", icon: Bookmark },
  { href: "/profile", label: "Profile", icon: UserRound },
];

export default function Navbar({ isAppRoute = false }: { isAppRoute?: boolean }) {
  const pathname = usePathname();
  const router = useRouter();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [userName, setUserName] = useState("");
  const [userLocation, setUserLocation] = useState("");

  useEffect(() => {
    if (!isAppRoute) return;
    farmerProfileAPI.getProfile().then((profile: any) => {
      if (profile?.full_name) setUserName(profile.full_name);
      if (profile?.state) {
        setUserLocation(profile.district ? `${profile.district}, ${profile.state}` : profile.state);
      }
    }).catch(() => {/* profile not set yet — show nothing */});
  }, [isAppRoute]);

  function handleLogout() {
    localStorage.removeItem("access_token");
    localStorage.removeItem("token_type");
    router.push("/auth/login");
  }

  const initials = userName
    ? userName.split(" ").map((n: string) => n[0]).slice(0, 2).join("").toUpperCase()
    : "–";

  if (!isAppRoute) {
    return (
      <header className="border-b border-[var(--border)] bg-white">
        <div className="mx-auto flex h-16 max-w-7xl items-center justify-between px-5 sm:px-8">
          <Brand />
          <nav className="hidden items-center gap-7 text-sm text-[var(--text-secondary)] md:flex">
            <Link href="/#features" className="transition-colors hover:text-[var(--text-primary)]">Product</Link>
            <Link href="/auth/login" className="transition-colors hover:text-[var(--text-primary)]">Sign in</Link>
            <Link href="/auth/register" className="btn-primary btn-sm">Create account</Link>
          </nav>
          <button className="btn-ghost min-h-10 px-2 md:hidden" aria-label="Open navigation" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {mobileOpen && (
          <div className="border-t border-[var(--border)] px-5 py-3 md:hidden">
            <Link href="/#features" className="block py-2 text-sm text-[var(--text-secondary)]">Product</Link>
            <Link href="/auth/login" className="block py-2 text-sm text-[var(--text-secondary)]">Sign in</Link>
            <Link href="/auth/register" className="btn-primary mt-2 w-full">Create account</Link>
          </div>
        )}
      </header>
    );
  }

  return (
    <>
      {/* Desktop sidebar */}
      <aside className="fixed inset-y-0 left-0 z-40 hidden w-[248px] border-r border-[var(--border)] bg-white lg:flex lg:flex-col">
        <div className="flex h-16 items-center border-b border-[var(--border)] px-6"><Brand /></div>
        <div className="px-4 pt-7 flex-1 overflow-y-auto">
          <p className="px-3 pb-3 text-[10px] font-semibold uppercase tracking-[0.14em] text-[var(--text-muted)]">Workspace</p>
          <nav className="space-y-1" aria-label="Main navigation">
            {navigation.map((item) => <NavItem key={item.href} item={item} pathname={pathname} />)}
          </nav>
        </div>
        <div className="border-t border-[var(--border)] p-4">
          <div className="flex items-center gap-3 rounded-md bg-[var(--surface-subtle)] px-3 py-3">
            <div className="flex h-8 w-8 flex-shrink-0 items-center justify-center rounded-full bg-[var(--accent-soft)] text-xs font-semibold text-[var(--accent-dark)]">
              {initials}
            </div>
            <div className="min-w-0 flex-1">
              <p className="truncate text-sm font-medium">{userName || "Your profile"}</p>
              <p className="truncate text-xs text-[var(--text-muted)]">{userLocation || "Set location in profile"}</p>
            </div>
            <button
              onClick={handleLogout}
              className="ml-auto flex h-7 w-7 flex-shrink-0 items-center justify-center rounded text-[var(--text-muted)] transition-colors hover:bg-[var(--border)] hover:text-[var(--error)]"
              aria-label="Log out"
              title="Log out"
            >
              <LogOut size={15} />
            </button>
          </div>
        </div>
      </aside>

      {/* Mobile top bar */}
      <header className="sticky top-0 z-30 border-b border-[var(--border)] bg-white/95 backdrop-blur lg:hidden">
        <div className="flex h-16 items-center justify-between px-5">
          <Brand />
          <button className="btn-ghost min-h-10 px-2" aria-label="Open navigation" onClick={() => setMobileOpen(!mobileOpen)}>
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
        {mobileOpen && (
          <div className="border-t border-[var(--border)] bg-white px-4 py-3">
            <nav className="space-y-1">
              {navigation.map((item) => (
                <NavItem key={item.href} item={item} pathname={pathname} onClick={() => setMobileOpen(false)} />
              ))}
            </nav>
            <div className="mt-3 border-t border-[var(--border)] pt-3">
              <button
                onClick={handleLogout}
                className="flex w-full items-center gap-3 rounded-md px-3 py-2.5 text-sm text-[var(--error)] hover:bg-[#fbefef]"
              >
                <LogOut size={16} />
                Log out
              </button>
            </div>
          </div>
        )}
      </header>
    </>
  );
}

function Brand() {
  return (
    <Link href="/" className="flex items-center gap-2.5">
      <span className="flex h-8 w-8 items-center justify-center rounded-md bg-[var(--accent)] text-sm font-bold text-white">K</span>
      <span className="text-[15px] font-semibold tracking-tight text-[var(--text-primary)]">KrishiX</span>
    </Link>
  );
}

function NavItem({
  item,
  pathname,
  onClick,
}: {
  item: (typeof navigation)[number];
  pathname: string;
  onClick?: () => void;
}) {
  const Icon = item.icon;
  const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
  return (
    <Link
      href={item.href}
      onClick={onClick}
      className={`flex min-h-10 items-center gap-3 rounded-md px-3 text-sm transition-colors ${
        active
          ? "bg-[var(--accent-soft)] font-medium text-[var(--accent-dark)]"
          : "text-[var(--text-secondary)] hover:bg-[var(--surface-subtle)] hover:text-[var(--text-primary)]"
      }`}
    >
      <Icon size={17} strokeWidth={active ? 2.2 : 1.8} />
      <span>{item.label}</span>
    </Link>
  );
}
