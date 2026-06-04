import { DatePipe } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Article, Backup, Category, LogEntry, Source, User } from '../models/api.models';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-admin-page',
  standalone: true,
  imports: [DatePipe, FormsModule, LucideAngularModule],
  template: `
    <main class="page admin-page">
      <h1>{{ labels.adminTitle }}</h1>
      <section class="admin-layout">
        <div class="card admin-card manual-card">
          <h2>{{ labels.manualNews }}</h2>
          <form class="form admin-form" #articleForm="ngForm" (ngSubmit)="addArticle()">
            <input name="articleTitle" [(ngModel)]="articleTitle" [placeholder]="labels.title" required minlength="5">
            <select name="articleCategory" [(ngModel)]="articleCategory" required>
              @for (category of categories(); track category.id) {
                <option [value]="category.name">{{ category.name }}</option>
              }
            </select>
            <input name="articleImageUrl" [(ngModel)]="articleImageUrl" [placeholder]="labels.imageUrl">
            <input name="articleUrl" [(ngModel)]="articleUrl" [placeholder]="labels.sourceUrlOptional">
            <textarea name="articleContent" [(ngModel)]="articleContent" rows="6" [placeholder]="labels.newsText" required minlength="10"></textarea>
            <button class="primary" type="submit" [disabled]="articleForm.invalid"><lucide-icon name="save" [size]="17"></lucide-icon> {{ labels.addNews }}</button>
          </form>
          @if (articleStatus()) { <p class="success admin-status">{{ articleStatus() }}</p> }
        </div>

        <div class="card admin-card sources-card">
          <h2>{{ labels.sources }}</h2>
          <form class="form admin-form" (ngSubmit)="addSource()">
            <input name="sourceName" [(ngModel)]="sourceName" [placeholder]="labels.sourceName" required>
            <input name="sourceUrl" [(ngModel)]="sourceUrl" placeholder="https://example.com/rss.xml" required>
            <button class="primary" type="submit"><lucide-icon name="save" [size]="17"></lucide-icon> {{ labels.add }}</button>
          </form>
          <div class="admin-list">
            @for (source of sources(); track source.id) {
              <div class="admin-list-row">
                <div class="stacked-text">
                  <strong>{{ source.name }}</strong>
                  <span class="badge">{{ source.type }}</span>
                </div>
                <button type="button" (click)="toggleSource(source)">{{ source.is_active ? labels.disable : labels.enable }}</button>
              </div>
            }
          </div>
          <button type="button" class="admin-action" (click)="aggregate()"><lucide-icon name="play" [size]="17"></lucide-icon> {{ labels.aggregate }}</button>
          @if (status()) { <p class="success admin-status">{{ status() }}</p> }
        </div>

        <div class="card admin-card users-card">
          <h2>{{ labels.users }}</h2>
          <div class="table-wrap">
            <table class="table admin-table">
              <thead><tr><th>ID</th><th>Email</th><th>{{ labels.role }}</th><th>{{ labels.active }}</th></tr></thead>
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
          <h2>{{ labels.backups }}</h2>
          <div class="row">
            <button type="button" (click)="createBackup()"><lucide-icon name="database-backup" [size]="17"></lucide-icon> {{ labels.create }}</button>
            <button type="button" (click)="applyMigrations()"><lucide-icon name="rotate-ccw" [size]="17"></lucide-icon> {{ labels.migrations }}</button>
          </div>
          <div class="admin-list">
            @for (backup of backups(); track backup.id) {
              <div class="admin-list-row">
                <div class="stacked-text">
                  <strong>{{ backup.filename }}</strong>
                  <span class="badge">{{ backup.status }}</span>
                </div>
                <button type="button" (click)="restore(backup.filename)">{{ labels.restore }}</button>
              </div>
            } @empty {
              <p class="muted">{{ labels.noBackups }}</p>
            }
          </div>
        </div>

        <div class="card admin-card articles-card">
          <h2>{{ labels.feedNews }}</h2>
          <div class="table-wrap">
            <table class="table admin-table articles-table">
              <thead><tr><th>ID</th><th>{{ labels.title }}</th><th>{{ labels.category }}</th><th></th></tr></thead>
              <tbody>
                @for (article of articles(); track article.id) {
                  <tr>
                    <td>{{ article.id }}</td>
                    <td class="cell-break">{{ article.title }}</td>
                    <td><span class="badge">{{ article.category || article.source.name }}</span></td>
                    <td><button class="danger" type="button" (click)="deleteArticle(article.id)">{{ labels.delete }}</button></td>
                  </tr>
                }
              </tbody>
            </table>
          </div>
        </div>

        <div class="card admin-card logs-card">
          <h2>{{ labels.logs }}</h2>
          <div class="table-wrap">
            <table class="table admin-table logs-table">
              <thead><tr><th>{{ labels.time }}</th><th>{{ labels.level }}</th><th>{{ labels.action }}</th><th>{{ labels.message }}</th></tr></thead>
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
  categories = signal<Category[]>([]);
  users = signal<User[]>([]);
  logs = signal<LogEntry[]>([]);
  backups = signal<Backup[]>([]);
  articles = signal<Article[]>([]);
  status = signal('');
  articleStatus = signal('');
  allowedCategories = [
    '\u0412\u0430\u0436\u043d\u0430\u044f',
    '\u041c\u0438\u0440',
    '\u041f\u0440\u043e\u0438\u0441\u0448\u0435\u0441\u0442\u0432\u0438\u044f',
    '\u0413\u043e\u0440\u043e\u0434',
    '\u041e\u0431\u0440\u0430\u0437\u043e\u0432\u0430\u043d\u0438\u0435',
    '\u0422\u0435\u0445\u043d\u043e\u043b\u043e\u0433\u0438\u0438',
    '\u0421\u043f\u043e\u0440\u0442',
    '\u041a\u0443\u043b\u044c\u0442\u0443\u0440\u0430'
  ];
  labels = {
    adminTitle: '\u041f\u0430\u043d\u0435\u043b\u044c \u0430\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0438\u0440\u043e\u0432\u0430\u043d\u0438\u044f',
    manualNews: '\u0421\u0432\u043e\u044f \u043d\u043e\u0432\u043e\u0441\u0442\u044c',
    title: '\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a',
    category: '\u041a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f',
    imageUrl: 'URL \u0444\u043e\u0442\u043e \u0438\u043b\u0438 /assets/news/photo.png',
    sourceUrlOptional: '\u0421\u0441\u044b\u043b\u043a\u0430 \u043d\u0430 \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a, \u043c\u043e\u0436\u043d\u043e \u043e\u0441\u0442\u0430\u0432\u0438\u0442\u044c \u043f\u0443\u0441\u0442\u043e\u0439',
    newsText: '\u0422\u0435\u043a\u0441\u0442 \u043d\u043e\u0432\u043e\u0441\u0442\u0438',
    addNews: '\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043d\u043e\u0432\u043e\u0441\u0442\u044c',
    sources: '\u0418\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0438 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439',
    sourceName: '\u041d\u0430\u0437\u0432\u0430\u043d\u0438\u0435 RSS-\u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a\u0430',
    add: '\u0414\u043e\u0431\u0430\u0432\u0438\u0442\u044c',
    disable: '\u0412\u044b\u043a\u043b\u044e\u0447\u0438\u0442\u044c',
    enable: '\u0412\u043a\u043b\u044e\u0447\u0438\u0442\u044c',
    aggregate: '\u0417\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u0430\u0433\u0440\u0435\u0433\u0430\u0446\u0438\u044e',
    users: '\u041f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0438',
    role: '\u0420\u043e\u043b\u044c',
    active: '\u0410\u043a\u0442\u0438\u0432\u0435\u043d',
    backups: '\u0420\u0435\u0437\u0435\u0440\u0432\u043d\u044b\u0435 \u043a\u043e\u043f\u0438\u0438',
    create: '\u0421\u043e\u0437\u0434\u0430\u0442\u044c',
    migrations: '\u041c\u0438\u0433\u0440\u0430\u0446\u0438\u0438',
    restore: '\u0412\u043e\u0441\u0441\u0442\u0430\u043d\u043e\u0432\u0438\u0442\u044c',
    noBackups: '\u0420\u0435\u0437\u0435\u0440\u0432\u043d\u044b\u0445 \u043a\u043e\u043f\u0438\u0439 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442.',
    feedNews: '\u041d\u043e\u0432\u043e\u0441\u0442\u0438 \u0432 \u043b\u0435\u043d\u0442\u0435',
    delete: '\u0423\u0434\u0430\u043b\u0438\u0442\u044c',
    logs: '\u0416\u0443\u0440\u043d\u0430\u043b \u0434\u0435\u0439\u0441\u0442\u0432\u0438\u0439',
    time: '\u0412\u0440\u0435\u043c\u044f',
    level: '\u0423\u0440\u043e\u0432\u0435\u043d\u044c',
    action: '\u0414\u0435\u0439\u0441\u0442\u0432\u0438\u0435',
    message: '\u0421\u043e\u043e\u0431\u0449\u0435\u043d\u0438\u0435',
    added: '\u041d\u043e\u0432\u043e\u0441\u0442\u044c \u0434\u043e\u0431\u0430\u0432\u043b\u0435\u043d\u0430 \u0438 \u0431\u0443\u0434\u0435\u0442 \u043f\u043e\u043a\u0430\u0437\u0430\u043d\u0430 \u0432 \u043b\u0435\u043d\u0442\u0435.',
    addError: '\u041d\u0435 \u0443\u0434\u0430\u043b\u043e\u0441\u044c \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043d\u043e\u0432\u043e\u0441\u0442\u044c. \u041f\u0440\u043e\u0432\u0435\u0440\u044c\u0442\u0435 \u043f\u043e\u043b\u044f \u0444\u043e\u0440\u043c\u044b.',
    requiredFields: '\u0417\u0430\u0433\u043e\u043b\u043e\u0432\u043e\u043a \u0438 \u0442\u0435\u043a\u0441\u0442 \u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u043e\u0431\u044f\u0437\u0430\u0442\u0435\u043b\u044c\u043d\u044b \u0434\u043b\u044f \u0437\u0430\u043f\u043e\u043b\u043d\u0435\u043d\u0438\u044f.'
  };
  sourceName = '';
  sourceUrl = '';
  articleTitle = '';
  articleContent = '';
  articleCategory = '\u0412\u0430\u0436\u043d\u0430\u044f';
  articleImageUrl = '';
  articleUrl = '';
  articleFeatured = true;

  constructor(private readonly api: ApiService) {}

  ngOnInit() {
    this.reload();
  }

  reload() {
    this.api.sources().subscribe((items) => this.sources.set(items));
    this.api.categories().subscribe((items) => {
      const filtered = items.filter((category) => this.allowedCategories.includes(category.name));
      this.categories.set(filtered);
      if (!this.allowedCategories.includes(this.articleCategory) && filtered.length > 0) {
        this.articleCategory = filtered[0].name;
      }
    });
    this.api.users().subscribe((items) => this.users.set(items));
    this.api.logs().subscribe((items) => this.logs.set(items));
    this.api.backups().subscribe((items) => this.backups.set(items));
    this.api.articles().subscribe((items) => this.articles.set(items));
  }

  addArticle() {
    if (!this.articleTitle.trim() || !this.articleContent.trim()) {
      this.articleStatus.set(this.labels.requiredFields);
      return;
    }
    this.api.createArticle({
      title: this.articleTitle.trim(),
      content: this.articleContent.trim(),
      category: this.articleCategory,
      image_url: this.articleImageUrl || null,
      url: this.articleUrl || null,
      is_featured: this.articleCategory === '\u0412\u0430\u0436\u043d\u0430\u044f'
    }).subscribe({
      next: () => {
        this.articleTitle = '';
        this.articleContent = '';
        this.articleImageUrl = '';
        this.articleUrl = '';
        this.articleCategory = '\u0412\u0430\u0436\u043d\u0430\u044f';
        this.articleStatus.set(this.labels.added);
        this.reload();
      },
      error: () => this.articleStatus.set(this.labels.addError)
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
