import Header from '@/components/header';
import { ChatWidget } from '@/components/chat/ChatWidget';

export default function ProtectedLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="min-h-screen bg-background">
      <Header />
      <main className="container mx-auto py-6">
        {children}
      </main>
      <ChatWidget />
    </div>
  );
}