/**
 * KrishiX Frontend - Root Layout
 * Professional agricultural market intelligence platform
 */

import type { Metadata } from "next";
import "./globals.css";
import AppFrame from "@/components/layout/AppFrame";

export const metadata: Metadata = {
  title: "KrishiX - Market Intelligence for Smarter Agricultural Decisions",
  description: "Reliable location-specific commodity prices and market intelligence for Indian farmers",
  keywords: "agriculture, commodity prices, market intelligence, farmers, APMC",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="antialiased">
        <AppFrame>{children}</AppFrame>
      </body>
    </html>
  );
}
