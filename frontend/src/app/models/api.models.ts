export interface Role {
  id: number;
  name: 'user' | 'admin';
  permissions: string[];
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
  role: Role;
}

export interface TokenPair {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface Source {
  id: number;
  name: string;
  url: string;
  type: 'rss' | 'api';
  is_active: boolean;
  created_at: string;
}

export interface Article {
  id: number;
  title: string;
  content: string;
  url: string;
  published_at: string | null;
  fetched_at: string;
  category: string | null;
  source: Source;
}

export interface LogEntry {
  id: number;
  user_id: number | null;
  action: string;
  entity: string;
  level: 'info' | 'warning' | 'error';
  message: string;
  ip_address: string | null;
  created_at: string;
}

export interface Backup {
  id: number;
  filename: string;
  created_at: string;
  size: number;
  status: string;
}
