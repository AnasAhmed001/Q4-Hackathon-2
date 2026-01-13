'use client';

import { useSession } from '@/lib/auth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import Header from '@/components/header';
import { LogoutButton } from '@/components/auth/LogoutButton';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  const { data: session, isLoading } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isLoading && !session) {
      // Redirect to login if not authenticated
      router.push('/login');
    }
  }, [session, isLoading, router]);

  if (isLoading || !session) {
    // Show loading state while checking session
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-gray-900"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Header />
      <main className="container mx-auto py-6">
        {children}
      </main>
    </div>
  );
}