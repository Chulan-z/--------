import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-login-page',
  standalone: true,
  imports: [FormsModule, RouterLink, LucideAngularModule],
  template: `
    <main class="page">
      <h1>Авторизация</h1>
      <form class="form card" (ngSubmit)="submit()">
        <label>Email<input type="email" name="email" [(ngModel)]="email" required></label>
        <label>Пароль<input type="password" name="password" [(ngModel)]="password" required minlength="8"></label>
        @if (error) { <p class="error">{{ error }}</p> }
        <button class="primary" type="submit"><lucide-icon name="log-in" [size]="17"></lucide-icon> Войти</button>
        <a routerLink="/register">Создать аккаунт</a>
      </form>
    </main>
  `
})
export class LoginPageComponent {
  email = 'admin@example.com';
  password = 'admin12345';
  error = '';

  constructor(private readonly auth: AuthService, private readonly router: Router) {}

  submit() {
    this.auth.login(this.email, this.password).subscribe({
      next: () => this.router.navigateByUrl('/profile'),
      error: (err) => this.error = err.error?.detail ?? 'Не удалось войти'
    });
  }
}
