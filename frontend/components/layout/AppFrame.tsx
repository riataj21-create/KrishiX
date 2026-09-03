"use client";

import { usePathname } from "next/navigation";
import Navbar from "@/components/Navigation/Navbar";
import Footer from "@/components/Footer";

export default function AppFrame({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isAppRoute = pathname !== "/" && !pathname.startsWith("/auth");

  return (
    <div className={isAppRoute ? "min-h-screen lg:pl-[248px]" : "min-h-screen"}>
      <Navbar isAppRoute={isAppRoute} />
      <main className="min-h-screen">{children}</main>
      {!isAppRoute && <Footer />}
    </div>
  );
}