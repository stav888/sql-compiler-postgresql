import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "PostgreSQL SQL Compiler",
  description: "Transform natural language into optimized PostgreSQL queries using AI",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased">
        {children}
      </body>
    </html>
  );
}
