import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Concert Buddy",
  description: "Your AI-powered concert assistant",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
