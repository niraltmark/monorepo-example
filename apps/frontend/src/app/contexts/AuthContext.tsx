import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from 'react';
import { usersApi, type UserRead } from '../api/usersApi';

interface AuthContextValue {
  token: string | null;
  user: UserRead | null;
  login: (token: string) => Promise<void>;
  logout: () => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [token, setToken] = useState<string | null>(() =>
    localStorage.getItem('access_token')
  );
  const [user, setUser] = useState<UserRead | null>(null);

  useEffect(() => {
    if (!token) {
      setUser(null);
      return;
    }
    usersApi.getMe(token).then(setUser).catch(() => {
      setToken(null);
      localStorage.removeItem('access_token');
    });
  }, [token]);

  const login = useCallback(async (newToken: string) => {
    localStorage.setItem('access_token', newToken);
    setToken(newToken);
    const me = await usersApi.getMe(newToken);
    setUser(me);
  }, []);

  const logout = useCallback(() => {
    localStorage.removeItem('access_token');
    setToken(null);
    setUser(null);
  }, []);

  const value = useMemo(() => ({ token, user, login, logout }), [token, user, login, logout]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within <AuthProvider>');
  return ctx;
}
