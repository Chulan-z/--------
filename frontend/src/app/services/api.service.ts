import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { Article, Backup, Category, LogEntry, Source, User } from '../models/api.models';

@Injectable({ providedIn: 'root' })
export class ApiService {
  private readonly baseUrl = 'http://localhost:8000/api';

  constructor(private readonly http: HttpClient) {}

  articles(filters: { q?: string; category?: string } = {}) {
    let params = new HttpParams();
    if (filters.q) params = params.set('q', filters.q);
    if (filters.category) params = params.set('category', filters.category);
    return this.http.get<Article[]>(`${this.baseUrl}/articles`, { params });
  }

  createArticle(payload: {
    title: string;
    content: string;
    url?: string | null;
    image_url?: string | null;
    category: string;
    is_featured: boolean;
  }) {
    return this.http.post<Article>(`${this.baseUrl}/admin/articles`, payload);
  }

  deleteArticle(id: number) {
    return this.http.delete(`${this.baseUrl}/admin/articles/${id}`);
  }

  sources() {
    return this.http.get<Source[]>(`${this.baseUrl}/sources`);
  }

  categories() {
    return this.http.get<Category[]>(`${this.baseUrl}/categories`);
  }

  createSource(payload: Partial<Source>) {
    return this.http.post<Source>(`${this.baseUrl}/admin/sources`, payload);
  }

  updateSource(id: number, payload: Partial<Source>) {
    return this.http.patch<Source>(`${this.baseUrl}/admin/sources/${id}`, payload);
  }

  deleteSource(id: number) {
    return this.http.delete(`${this.baseUrl}/admin/sources/${id}`);
  }

  aggregate() {
    return this.http.post<Record<string, number>>(`${this.baseUrl}/admin/aggregate`, {});
  }

  users() {
    return this.http.get<User[]>(`${this.baseUrl}/admin/users`);
  }

  updateUser(id: number, payload: Partial<User> & { role_id?: number }) {
    return this.http.patch<User>(`${this.baseUrl}/admin/users/${id}`, payload);
  }

  logs() {
    return this.http.get<LogEntry[]>(`${this.baseUrl}/admin/logs`);
  }

  backups() {
    return this.http.get<Backup[]>(`${this.baseUrl}/admin/backups`);
  }

  createBackup() {
    return this.http.post<Backup>(`${this.baseUrl}/admin/backups`, {});
  }

  restoreBackup(filename: string) {
    return this.http.post<Backup>(`${this.baseUrl}/admin/backups/restore`, { filename });
  }

  applyMigrations() {
    return this.http.post<{ message: string }>(`${this.baseUrl}/admin/migrations`, {});
  }
}
