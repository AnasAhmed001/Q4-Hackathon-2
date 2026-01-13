'use client';

import { useSession } from '@/lib/auth';
import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

const DashboardPage = () => {
  const { data: session, isPending, error } = useSession();
  const router = useRouter();

  useEffect(() => {
    if (!isPending && (!session || error)) {
      router.push('/login');
    }
  }, [session, error, isPending, router]);

  if (isPending) {
    return (
      <div className="flex min-h-screen items-center justify-center">
        <div className="text-lg">Loading...</div>
      </div>
    );
  }

  if (!session || error) {
    return null; // Redirect effect will handle navigation
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
        <div className="bg-white shadow sm:rounded-lg">
          <div className="px-4 py-5 sm:p-6">
            <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
            <div className="mt-4">
              <p className="text-gray-600">Welcome, {session.user.name || session.user.email}!</p>
              <p className="mt-2 text-sm text-gray-500">You are successfully logged in.</p>
            </div>

            {/* Example of making an authenticated API call */}
            <div className="mt-6">
              <h2 className="text-lg font-medium text-gray-900">User Information</h2>
              <div className="mt-2 grid grid-cols-1 gap-4 sm:grid-cols-2">
                <div className="rounded-md bg-gray-50 p-4">
                  <p className="text-sm font-medium text-gray-500">Email</p>
                  <p className="mt-1 text-sm text-gray-900">{session.user.email}</p>
                </div>
                <div className="rounded-md bg-gray-50 p-4">
                  <p className="text-sm font-medium text-gray-500">User ID</p>
                  <p className="mt-1 text-sm text-gray-900">{session.user.id}</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default DashboardPage;