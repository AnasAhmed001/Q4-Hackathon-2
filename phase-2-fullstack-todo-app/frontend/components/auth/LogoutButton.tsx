'use client';

import { useRouter } from 'next/navigation';
import { signOut } from '@/lib/auth';
import { Button } from '@/components/ui/button';
import { LogOut } from 'lucide-react';

export const LogoutButton = () => {
  const router = useRouter();

  const handleLogout = async () => {
    try {
      await signOut();
      // Redirect to login page after logout
      router.push('/login');
      router.refresh(); // Refresh to update the UI
    } catch (error) {
      console.error('Logout failed:', error);
    }
  };

  return (
    <Button onClick={handleLogout} variant="outline" className="flex items-center gap-2">
      <LogOut className="h-4 w-4" />
      Logout
    </Button>
  );
};