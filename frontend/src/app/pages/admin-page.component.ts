import { DatePipe } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Article, Backup, LogEntry, Source, User } from '../models/api.models';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [DatePipe, FormsModule, LucideAngularModule],
  template: `
    <main class="page admin-page">
      <h1>Панель администрирования</h1>
      <section class="admin-layout">
        <div class="card admin-card manual-card">
          <h2>Своя новость</h2>
          <form class="form admin-form" (ngSubmit)="addArticle()">
            <input name="articleTitle" [(ngModel)]="articleTitle" placeholder="Заголовок" required minlength="5">
            <input name="articleCategory" [(ngModel)]="articleCategory" placeholder="Категория">
            <input name="articleImageUrl" [(ngModel)]="articleImageUrl" placeholder="URL фото, например https://site.ru/photo.jpg">
            <input name="articleUrl" [(ngModel)]="articleUrl" placeholder="Ссылка на источник, можно оставить пустой">
            <textarea name="articleContent" [(ngModel)]="articleContent" rows="6" placeholder="Текст новости" required minlength="10"></textarea>
            <label class="check-row">
              <input class="table-checkbox" type="checkbox" name="articleFeatured" [(ngModel)]="articleFeatured">
              <span>Сделать основной в ленте</span>
            </label>
            <button class="primary" type="submit"><lucide-icon name="save" [size]="17"></lucide-icon> Добавить новость</button>
          </form>
          @if (articleStatus()) { <p class="success admin-status">{{ articleStatus() }}</p> }
        </div>

        <div class="card admin-card sources-card">
          <h2>Источники новостей</h2>
          <form class="form admin-form" (ngSubmit)="addSource()">
            <input name="sourceName" [(ngModel)]="sourceName" placeholder="Название RSS-источника" required>
            <input name="sourceUrl" [(ngModel)]="sourceUrl" placeholder="https://example.com/rss.xml" required>
            <button class="primary" type="submit"><lucide-icon name="save" [size]="17"></lucide-icon> Добавить</button>
          </form>
          <div class="admin-list">
            @for (source of sources(); track source.id) {
              <div class="admin-list-row">
                <div class="stacked-text">
                  <strong>{{ source.name }}</strong>
                  <span class="badge">{{ source.type }}</span>
                </div>
                <button type="button" (click)="toggleSource(source)">{{ source.is_active ? 'Выключить' : 'Включить' }}</button>
              </div>
            }
          </div>
          <button type="button" class="admin-action" (click)="aggregate()"><lucide-icon name="play" [size]="17"></lucide-icon> Запустить агрегацию</button>
          @if (status()) { <p class="success admin-status">{{ status() }}</p> }
        </div>

        <div class="card admin-card users-card">
          <h2>Пользователи</h2>
          <div class="table-wrap">
            <table class="table admin-table">
              <thead><tr><th>ID</th><th>Email</th><th>Роль</th><th>Активен</th></tr></thead>
              <tbody>
                @for (user of users(); track user.id) {
                  <tr>
                    <td>{{ user.id }}</td>
                    <td class="cell-break">{{ user.email }}</td>
                    <td><span class="badge">{{ user.role.name }}</span></td>
                    <td><input class="table-checkbox" type="checkbox" [ngModel]="user.is_active" (ngModelChange)="setUserActive(user, $event)"></td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>

        <div class="card admin-card backups-card">
          <h2>Резервные копии</h2>
          <div class="row">
            <button type="button" (click)="createBackup()"><lucide-icon name="database-backup" [size]="17"></lucide-icon> Создать</button>
            <button type="button" (click)="applyMigrations()"><lucide-icon name="rotate-ccw" [size]="17"></lucide-icon> Миграции</button>
          </div>
          <div class="admin-list">
            @for (backup of backups(); track backup.id) {
              <div class="admin-list-row">
                <div class="stacked-text">
                  <strong>{{ backup.filename }}</strong>
                  <span class="badge">{{ backup.status }}</span>
                </div>
                <button type="button" (click)="restore(backup.filename)">Восстановить</button>
              </div>
            } @empty {
              <p class="muted">Резервных копий пока нет.</p>
            }
          </div>
        </div>

        <div class="card admin-card articles-card">
          <h2>Новости в ленте</h2>
          <div class="table-wrap">
            <table class="table admin-table articles-table">
              <thead><tr><th>ID</th><th>Заголовок</th><th>Тип</th><th></th></tr></thead>
              <tbody>
                @for (article of articles(); track article.id) {
                  <tr>
                    <td>{{ article.id }}</td>
                    <td class="cell-break">{{ article.title }}</td>
                    <td><span class="badge">{{ article.is_featured ? 'Основная' : article.source.name }}</span></td>
                    <td><button class="danger" type="button" (click)="deleteArticle(article.id)">Удалить</button></td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>

        <div class="card admin-card logs-card">
          <h2>Журнал действий</h2>
          <div class="table-wrap">
            <table class="table admin-table logs-table">
              <thead><tr><th>Время</th><th>Уровень</th><th>Действие</th><th>Сообщение</th></tr></thead>
              <tbody>
                @for (log of logs(); track log.id) {
                  <tr>
                    <td class="nowrap">{{ log.created_at | date:'dd.MM HH:mm' }}</td>
                    <td><span class="badge">{{ log.level }}</span></td>
                    <td class="nowrap">{{ log.action }}</td>
                    <td class="cell-break">{{ log.message }}</td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
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
  articles = signal<Article[]>([]);
  status = signal('');
  articleStatus = signal('');
  sourceName = '';
  sourceUrl = '';
  articleTitle = '';
  articleContent = '';
  articleCategory = 'Важная';
  articleImageUrl = '';
  articleUrl = '';
  articleFeatured = true;

  constructor(private readonly api: ApiService) {}

  ngOnInit() {
    this.reload();
  }

  reload() {
    this.api.sources().subscribe((items) => this.sources.set(items));
    this.api.users().subscribe((items) => this.users.set(items));
    this.api.logs().subscribe((items) => this.logs.set(items));
    this.api.backups().subscribe((items) => this.backups.set(items));
    this.api.articles().subscribe((items) => this.articles.set(items));
  }

  addArticle() {
    this.api.createArticle({
      title: this.articleTitle,
      content: this.articleContent,
      category: this.articleCategory || 'Редакция',
      image_url: this.articleImageUrl || null,
      url: this.articleUrl || null,
      is_featured: this.articleFeatured
    }).subscribe({
      next: () => {
        this.articleTitle = '';
        this.articleContent = '';
        this.articleImageUrl = '';
        this.articleUrl = '';
        this.articleCategory = 'Важная';
        this.articleFeatured = true;
        this.articleStatus.set('Новость добавлена и будет показана в ленте.');
        this.reload();
      },
      error: () => this.articleStatus.set('Не удалось добавить новость. Проверьте поля формы.')
    });
  }

  deleteArticle(id: number) {
    this.api.deleteArticle(id).subscribe(() => this.reload());
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
