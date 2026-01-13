'use client';

import React, { createContext, useContext, ReactNode } from 'react';
import { AuthProvider } from 'better-auth/react';
import { auth } from '@/lib/auth';

interface AuthContextType {}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

interface AuthWrapperProps {
  children: ReactNode;
}

export const AuthWrapper: React.FC<AuthWrapperProps> = ({ children }) => {
  return (
    <AuthProvider client={auth}>
      {children}
    </AuthProvider>
  );
};