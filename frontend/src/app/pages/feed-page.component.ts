import { DatePipe } from '@angular/common';
import { Component, OnInit, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Article } from '../models/api.models';
import { ApiService } from '../services/api.service';

@Component({
  selector: 'app-feed-page',
  standalone: true,
  imports: [DatePipe, FormsModule, LucideAngularModule],
  template: `
    <main class="page">
      <div class="row" style="justify-content: space-between; margin-bottom: 18px;">
        <div>
          <h1>Лента агрегированных новостей</h1>
          <p class="muted">Основные новости редакции и материалы из RSS-источников хранятся в PostgreSQL.</p>
        </div>
        <button type="button" (click)="load()" title="Обновить ленту"><lucide-icon name="refresh-ccw" [size]="18"></lucide-icon></button>
      </div>
      <form class="row" (ngSubmit)="load()" style="margin-bottom: 18px;">
        <label style="flex: 1; min-width: 240px;">
          <input name="q" [(ngModel)]="q" placeholder="Поиск по заголовкам">
        </label>
        <button class="primary" type="submit"><lucide-icon name="search" [size]="17"></lucide-icon> Найти</button>
      </form>
      @if (loading()) {
        <p class="muted">Загрузка...</p>
      } @else {
        <section class="grid">
          @for (article of articles(); track article.id) {
            <article class="card news-card">
              @if (article.image_url) {
                <img class="news-image" [src]="article.image_url" [alt]="article.title" loading="lazy">
              }
              <div class="row" style="justify-content: space-between;">
                <span class="badge">{{ article.source.name }}</span>
                <span class="badge">{{ article.is_featured ? (article.category || 'Основная') : (article.category || 'Без категории') }}</span>
              </div>
              <h2>{{ article.title }}</h2>
              <p class="muted">{{ article.published_at || article.fetched_at | date:'dd.MM.yyyy HH:mm' }}</p>
              <p [innerHTML]="article.content"></p>
              <a class="row" [href]="article.url" target="_blank" rel="noopener">Открыть источник <lucide-icon name="external-link" [size]="16"></lucide-icon></a>
            </article>
          } @empty {
            <p class="muted">Новостей пока нет. Администратор может добавить свою новость или запустить агрегацию.</p>
          }
        </section>
      }
    </main>
  `
})
export class FeedPageComponent implements OnInit {
  q = '';
  articles = signal<Article[]>([]);
  loading = signal(false);

  constructor(private readonly api: ApiService) {}

  ngOnInit() {
    this.load();
  }

  load() {
    this.loading.set(true);
    this.api.articles({ q: this.q }).subscribe({
      next: (items) => this.articles.set(items),
      error: () => this.articles.set([]),
      complete: () => this.loading.set(false)
    });
  }
}
