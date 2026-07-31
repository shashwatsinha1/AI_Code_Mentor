import { createContext } from 'react';

export type AuthContextValue = {
  accessToken: string | null;
  refreshToken: string | null;
  isAuthReady: boolean;
  login: (email: string, password: string) => Promise<void>;
  refresh: () => Promise<string | null>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
