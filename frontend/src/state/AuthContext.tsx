import React, { useEffect, useMemo, useRef, useState } from 'react';

import { TokenPair, login as apiLogin, refreshToken as apiRefreshToken } from '../api/client';
import { AuthContext, AuthContextValue } from './auth-context';

const ACCESS_KEY = 'ai-code-mentor.access';
const REFRESH_KEY = 'ai-code-mentor.refresh';

function persistTokens(tokens: TokenPair) {
  localStorage.setItem(ACCESS_KEY, tokens.access_token);
  localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [accessToken, setAccessToken] = useState<string | null>(() => localStorage.getItem(ACCESS_KEY));
  const [refreshToken, setRefreshToken] = useState<string | null>(() => localStorage.getItem(REFRESH_KEY));
  const [isAuthReady, setIsAuthReady] = useState(false);
  const bootstrapped = useRef(false);

  function clearTokens() {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    setAccessToken(null);
    setRefreshToken(null);
  }

  useEffect(() => {
    if (bootstrapped.current) return;
    bootstrapped.current = true;

    async function bootstrapSession() {
      const storedRefreshToken = localStorage.getItem(REFRESH_KEY);
      if (!storedRefreshToken) {
        clearTokens();
        setIsAuthReady(true);
        return;
      }

      try {
        const tokens = await apiRefreshToken(storedRefreshToken);
        persistTokens(tokens);
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);
      } catch {
        clearTokens();
      } finally {
        setIsAuthReady(true);
      }
    }

    bootstrapSession();
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      accessToken,
      refreshToken,
      isAuthReady,
      async login(email, password) {
        const tokens = await apiLogin({ email, password });
        persistTokens(tokens);
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);
        setIsAuthReady(true);
      },
      async refresh() {
        if (!refreshToken) {
          return null;
        }
        const tokens = await apiRefreshToken(refreshToken);
        persistTokens(tokens);
        setAccessToken(tokens.access_token);
        setRefreshToken(tokens.refresh_token);
        return tokens.access_token;
      },
      logout() {
        clearTokens();
        setIsAuthReady(true);
      },
    }),
    [accessToken, isAuthReady, refreshToken],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
