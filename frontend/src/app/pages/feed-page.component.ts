import { DatePipe } from '@angular/common';
import { Component, OnInit, computed, signal } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { LucideAngularModule } from 'lucide-angular';
import { Article } from '../models/api.models';
import { ApiService } from '../services/api.service';

interface CategorySection {
  name: string;
  articles: Article[];
}

@Component({
  selector: 'app-feed-page',
  standalone: true,
  imports: [DatePipe, FormsModule, LucideAngularModule],
  template: `
    <main class="page">
      <div class="feed-head">
        <div>
          <h1>{{ labels.feedTitle }}</h1>
          <p class="muted">{{ labels.feedDescription }}</p>
        </div>
        <button type="button" (click)="load()" [title]="labels.refresh">
          <lucide-icon name="refresh-ccw" [size]="18"></lucide-icon>
        </button>
      </div>

      <form class="feed-search" (ngSubmit)="load()">
        <input name="q" [(ngModel)]="q" [placeholder]="labels.search">
        <button class="primary" type="submit"><lucide-icon name="search" [size]="17"></lucide-icon> {{ labels.find }}</button>
      </form>

      @if (loading()) {
        <p class="muted">{{ labels.loading }}</p>
      } @else {
        @for (section of categorySections(); track section.name) {
          <section class="category-section">
            <div class="category-title">
              <h2>{{ section.name }}</h2>
              <span class="badge">{{ section.articles.length }}</span>
            </div>

            <div [class]="section.name === importantCategory ? 'featured-grid' : 'grid'">
              @for (article of section.articles; track article.id) {
                <article class="card news-card" [class.featured-card]="section.name === importantCategory">
                  @if (article.image_url) {
                    <img class="news-image" [class.featured-image]="section.name === importantCategory" [src]="article.image_url" [alt]="article.title" loading="lazy">
                  }
                  <div class="row" style="justify-content: space-between;">
                    <span class="badge">{{ article.source.name }}</span>
                    <span class="badge" [class.priority-badge]="section.name === importantCategory">{{ article.category || section.name }}</span>
                  </div>
                  <h2>{{ article.title }}</h2>
                  <p class="muted">{{ article.published_at || article.fetched_at | date:'dd.MM.yyyy HH:mm' }}</p>
                  <p [innerHTML]="article.content"></p>
                  <a class="row" [href]="article.url" target="_blank" rel="noopener">{{ labels.openSource }} <lucide-icon name="external-link" [size]="16"></lucide-icon></a>
                </article>
              }
            </div>
          </section>
        } @empty {
          <div class="empty-panel muted">{{ labels.empty }}</div>
        }
      }
    </main>
  `
})
export class FeedPageComponent implements OnInit {
  q = '';
  articles = signal<Article[]>([]);
  loading = signal(false);
  importantCategory = '\u0412\u0430\u0436\u043d\u0430\u044f';
  categoryOrder = [
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
    feedTitle: '\u041b\u0435\u043d\u0442\u0430 \u043d\u043e\u0432\u043e\u0441\u0442\u0435\u0439',
    feedDescription: '\u041d\u043e\u0432\u043e\u0441\u0442\u0438 \u0441\u0433\u0440\u0443\u043f\u043f\u0438\u0440\u043e\u0432\u0430\u043d\u044b \u043f\u043e \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u044f\u043c. \u0412\u0430\u0436\u043d\u044b\u0435 \u043d\u043e\u0432\u043e\u0441\u0442\u0438 \u043f\u043e\u043a\u0430\u0437\u044b\u0432\u0430\u044e\u0442\u0441\u044f \u043e\u0442\u0434\u0435\u043b\u044c\u043d\u043e \u043f\u0435\u0440\u0432\u044b\u043c\u0438.',
    refresh: '\u041e\u0431\u043d\u043e\u0432\u0438\u0442\u044c \u043b\u0435\u043d\u0442\u0443',
    search: '\u041f\u043e\u0438\u0441\u043a',
    find: '\u041d\u0430\u0439\u0442\u0438',
    loading: '\u0417\u0430\u0433\u0440\u0443\u0437\u043a\u0430...',
    openSource: '\u041e\u0442\u043a\u0440\u044b\u0442\u044c \u0438\u0441\u0442\u043e\u0447\u043d\u0438\u043a',
    empty: '\u041d\u043e\u0432\u043e\u0441\u0442\u0435\u0439 \u043f\u043e\u043a\u0430 \u043d\u0435\u0442. \u0410\u0434\u043c\u0438\u043d\u0438\u0441\u0442\u0440\u0430\u0442\u043e\u0440 \u043c\u043e\u0436\u0435\u0442 \u0434\u043e\u0431\u0430\u0432\u0438\u0442\u044c \u043d\u043e\u0432\u043e\u0441\u0442\u044c \u0438\u043b\u0438 \u0437\u0430\u043f\u0443\u0441\u0442\u0438\u0442\u044c \u0430\u0433\u0440\u0435\u0433\u0430\u0446\u0438\u044e.'
  };
  categorySections = computed(() => this.buildCategorySections(this.articles()));

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

  private buildCategorySections(articles: Article[]): CategorySection[] {
    const sections = new Map<string, CategorySection>();
    for (const article of articles) {
      const name = article.category || '\u0411\u0435\u0437 \u043a\u0430\u0442\u0435\u0433\u043e\u0440\u0438\u0438';
      if (!sections.has(name)) {
        sections.set(name, { name, articles: [] });
      }
      sections.get(name)!.articles.push(article);
    }
    return Array.from(sections.values()).sort((a, b) => this.sectionWeight(a.name) - this.sectionWeight(b.name));
  }

  private sectionWeight(name: string): number {
    const index = this.categoryOrder.indexOf(name);
    return index === -1 ? 100 : index;
  }
}
