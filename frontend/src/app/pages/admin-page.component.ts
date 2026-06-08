import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Backup, LogEntry, Source, User } from '../models/api.models';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [FormsModule, LucideAngularModule],
  template: `
    <main class="page">
      <h1>Панель администрирования</h1>
      <section class="grid">
        <div class="card">
          <h2>Источники новостей</h2>
          <form class="form" (ngSubmit)="addSource()">
            <input name="sourceName" [(ngModel)]="sourceName" placeholder="Название RSS-источника" required>
            <input name="sourceUrl" [(ngModel)]="sourceUrl" placeholder="https://example.com/rss.xml" required>
            <button class="primary" type="submit"><lucide-icon name="save" [size]="17"></lucide-icon> Добавить</button>
          </form>
          <div style="margin-top: 14px;">
            @for (source of sources(); track source.id) {
              <div class="row" style="justify-content: space-between; border-top: 1px solid var(--line); padding: 10px 0;">
                <span>{{ source.name }} <span class="badge">{{ source.type }}</span></span>
                <button type="button" (click)="toggleSource(source)">{{ source.is_active ? 'Выключить' : 'Включить' }}</button>
              </div>
            }
          </div>
          <button type="button" style="margin-top: 12px;" (click)="aggregate()"><lucide-icon name="play" [size]="17"></lucide-icon> Запустить агрегацию</button>
          @if (status()) { <p class="success">{{ status() }}</p> }
        </div>

        <div class="card">
          <h2>Пользователи</h2>
          <table class="table">
            <thead><tr><th>ID</th><th>Email</th><th>Роль</th><th>Активен</th></tr></thead>
            <tbody>
              @for (user of users(); track user.id) {
                <tr>
                  <td>{{ user.id }}</td>
                  <td>{{ user.email }}</td>
                  <td>{{ user.role.name }}</td>
                  <td><input type="checkbox" [ngModel]="user.is_active" (ngModelChange)="setUserActive(user, $event)"></td>
                </tr>
              }
            </tbody>
          </table>
        </div>

        <div class="card">
          <h2>Резервные копии</h2>
          <div class="row">
            <button type="button" (click)="createBackup()"><lucide-icon name="database-backup" [size]="17"></lucide-icon> Создать</button>
            <button type="button" (click)="applyMigrations()"><lucide-icon name="rotate-ccw" [size]="17"></lucide-icon> Миграции</button>
          </div>
          @for (backup of backups(); track backup.id) {
            <div class="row" style="justify-content: space-between; border-top: 1px solid var(--line); padding: 10px 0;">
              <span>{{ backup.filename }} <span class="badge">{{ backup.status }}</span></span>
              <button type="button" (click)="restore(backup.filename)">Восстановить</button>
            </div>
          }
        </div>

        <div class="card">
          <h2>Журнал действий</h2>
          <table class="table">
            <thead><tr><th>Уровень</th><th>Действие</th><th>Сообщение</th></tr></thead>
            <tbody>
              @for (log of logs(); track log.id) {
                <tr>
                  <td><span class="badge">{{ log.level }}</span></td>
                  <td>{{ log.action }}</td>
                  <td>{{ log.message }}</td>
                </tr>
              }
            </tbody>
          </table>
        </div>
      </section>
    </main>
  `
})
export class AdminPageComponent implements OnInit {
  sources = signal<Source[]>([]);
  users = signal<User[]>([]);
  logs = signal<LogEntry[]>([]);
  backups = signal<Backup[]>([]);
  status = signal('');
  sourceName = '';
  sourceUrl = '';

  constructor(private readonly api: ApiService) {}

  ngOnInit() {
    this.reload();
  }

  reload() {
    this.api.sources().subscribe((items) => this.sources.set(items));
    this.api.users().subscribe((items) => this.users.set(items));
    this.api.logs().subscribe((items) => this.logs.set(items));
    this.api.backups().subscribe((items) => this.backups.set(items));
  }

  addSource() {
    this.api.createSource({ name: this.sourceName, url: this.sourceUrl, type: 'rss', is_active: true }).subscribe(() => {
      this.sourceName = '';
      this.sourceUrl = '';
      this.reload();
    });
  }

  toggleSource(source: Source) {
    this.api.updateSource(source.id, { is_active: !source.is_active }).subscribe(() => this.reload());
  }

  setUserActive(user: User, is_active: boolean) {
    this.api.updateUser(user.id, { is_active }).subscribe(() => this.reload());
  }

  aggregate() {
    this.api.aggregate().subscribe((result) => {
      this.status.set(Object.entries(result).map(([name, count]) => `${name}: ${count}`).join('; '));
      this.reload();
    });
  }

  createBackup() {
    this.api.createBackup().subscribe(() => this.reload());
  }

  restore(filename: string) {
    this.api.restoreBackup(filename).subscribe(() => this.reload());
  }

  applyMigrations() {
    this.api.applyMigrations().subscribe((result) => this.status.set(result.message));
  }
}
