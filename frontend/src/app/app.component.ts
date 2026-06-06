import { Component } from '@angular/core';
import { RouterLink, RouterLinkActive, RouterOutlet } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from './services/auth.service';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [RouterOutlet, RouterLink, RouterLinkActive, LucideAngularModule],
  template: `
    <header class="toolbar">
      <a class="brand" routerLink="/">
        <lucide-icon name="newspaper" [size]="22"></lucide-icon>
        <span>Агрегатор новостей</span>
      </a>
      <nav class="nav">
        <a routerLink="/" routerLinkActive="active" [routerLinkActiveOptions]="{ exact: true }">Лента</a>
        @if (auth.isAuthenticated()) {
          <a routerLink="/profile" routerLinkActive="active">Кабинет</a>
          @if (auth.role === 'admin') {
            <a routerLink="/admin" routerLinkActive="active">Администрирование</a>
          }
          <button type="button" (click)="auth.logout()">Выйти</button>
        } @else {
          <a routerLink="/login" routerLinkActive="active">Вход</a>
          <a routerLink="/register" routerLinkActive="active">Регистрация</a>
        }
      </nav>
    </header>
    <router-outlet></router-outlet>
  `
})
export class AppComponent {
  constructor(readonly auth: AuthService) {}
}
