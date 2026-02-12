import type { Metadata } from 'next';
import './globals.css';

export const metadata: Metadata = {
    title: 'Rehmat-e-Shereen Voice Agent',
    description: 'AI-powered voice assistant for Rehmat-e-Shereen',
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
