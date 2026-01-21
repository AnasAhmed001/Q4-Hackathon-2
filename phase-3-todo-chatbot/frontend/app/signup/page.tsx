import { SignupForm } from '@/components/auth/SignupForm';
import { Metadata } from 'next';
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { GalleryVerticalEnd } from 'lucide-react';

export const metadata: Metadata = {
  title: 'Sign Up | Task Manager',
  description: 'Create a new Task Manager account',
};

export default function SignupPage() {
  return (
    <div className="bg-background flex min-h-screen flex-col items-center justify-center gap-6 p-6 md:p-10">
      <div className="flex w-full max-w-sm flex-col gap-6 items-center">
        <a href="#" className="flex items-center gap-2 self-center font-medium text-foreground">
          <div className="bg-primary text-primary-foreground flex size-6 items-center justify-center rounded-md">
            <GalleryVerticalEnd className="size-4" />
          </div>
          Task Manager
        </a>
        <Card className='w-110'>
          <CardHeader className="text-center">
            <CardTitle className="text-xl">Create your account</CardTitle>
            <CardDescription>
              Enter your details below to create your account
            </CardDescription>
          </CardHeader>
          <CardContent>
            <SignupForm />
          </CardContent>
        </Card>
      </div>
    </div>
  );
}