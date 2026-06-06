import { HttpClient } from '@angular/common/http';
import { Injectable, signal } from '@angular/core';
import { jwtDecode } from 'jwt-decode';
import { tap } from 'rxjs';
import { TokenPair, User } from '../models/api.models';

interface TokenPayload {
  sub: string;
  role: 'user' | 'admin';
  exp: number;
}

@Injectable({ providedIn: 'root' })
export class AuthService {
  private readonly baseUrl = 'http://localhost:8000/api/auth';
  readonly currentUser = signal<User | null>(null);

  constructor(private readonly http: HttpClient) {
    if (this.accessToken) {
      this.loadMe().subscribe({ error: () => this.clear() });
    }
  }

  get accessToken(): string | null {
    return localStorage.getItem('access_token');
  }

  get refreshToken(): string | null {
    return localStorage.getItem('refresh_token');
  }

  get role(): 'user' | 'admin' | null {
    if (!this.accessToken) return null;
    try {
      return jwtDecode<TokenPayload>(this.accessToken).role;
    } catch {
      return null;
    }
  }

  login(email: string, password: string) {
    return this.http.post<TokenPair>(`${this.baseUrl}/login`, { email, password }).pipe(tap((tokens) => this.store(tokens)));
  }

  register(username: string, email: string, password: string) {
    return this.http.post<TokenPair>(`${this.baseUrl}/register`, { username, email, password }).pipe(tap((tokens) => this.store(tokens)));
  }

  loadMe() {
    return this.http.get<User>(`${this.baseUrl}/me`).pipe(tap((user) => this.currentUser.set(user)));
  }

  logout() {
    const refresh_token = this.refreshToken;
    this.clear();
    if (refresh_token) {
      this.http.post(`${this.baseUrl}/logout`, { refresh_token }).subscribe();
    }
  }

  store(tokens: TokenPair) {
    localStorage.setItem('access_token', tokens.access_token);
    localStorage.setItem('refresh_token', tokens.refresh_token);
    this.loadMe().subscribe();
  }

  clear() {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUser.set(null);
  }

  isAuthenticated(): boolean {
    return Boolean(this.accessToken);
  }
}
