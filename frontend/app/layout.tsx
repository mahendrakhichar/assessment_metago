import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
  title: 'Metago AI Marketing Platform',
  description:
    'AI-powered marketing automation and content distribution platform for Metago — India\'s leading medical GLP-1 weight-loss program.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body>{children}</body>
    </html>
  );
}
