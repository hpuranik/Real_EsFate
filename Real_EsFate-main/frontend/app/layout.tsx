import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Urban Intelligence Platform',
  description: 'Displacement Risk Forecasting System',
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
