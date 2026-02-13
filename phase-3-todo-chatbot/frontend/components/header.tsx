'use client';

import { useSession, signOut } from '@/lib/auth';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Button } from '@/components/ui/button';
import { ModeToggle } from './ModeToggle';

const Header = () => {
  const { data: session, isPending } = useSession();
  const router = useRouter();

  return (
    <header className="sticky top-0 z-40 border-b bg-background backdrop-blur-md">
      <div className="mx-auto flex max-w-6xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
        <Link href="/" className="flex items-center gap-3">
          <div className="flex h-10 w-10 items-center justify-center rounded-full bg-gradient-to-br from-gray-900 to-gray-700 text-white font-semibold">
            TA
          </div>
          <div className="flex flex-col leading-tight">
            <span className="text-sm uppercase tracking-[0.12em] text-foreground">Task Manager</span>
          </div>
        </Link>

        <nav className="flex items-center gap-2">
          {!isPending && session ? (
            <>
              <span className="hidden text-sm text-muted-foreground sm:inline">
                {session.user.email}
              </span>
              <Button
                variant="outline"
                onClick={async () => {
                  await signOut();
                  router.push('/login');
                  router.refresh();
                }}
              >
                Sign Out
              </Button>
              <ModeToggle />
            </>
          ) : (
            <div className="flex items-center gap-2">
              <Link href="/login" className="hidden sm:inline-flex">
                <Button variant="ghost">Log In</Button>
              </Link>
              <Link href="/signup">
                <Button>Sign Up</Button>
              </Link>
            </div>
          )}
        </nav>
      </div>
    </header>
  );
};

export default Header;