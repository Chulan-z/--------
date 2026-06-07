import { Component } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { Router, RouterLink } from '@angular/router';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-register-page',
  standalone: true,
  imports: [FormsModule, RouterLink, LucideAngularModule],
  template: `
    <main class="page">
      <h1>Регистрация</h1>
      <form class="form card" (ngSubmit)="submit()">
        <label>Логин<input name="username" [(ngModel)]="username" required minlength="3"></label>
        <label>Email<input type="email" name="email" [(ngModel)]="email" required></label>
        <label>Пароль<input type="password" name="password" [(ngModel)]="password" required minlength="8"></label>
        @if (error) { <p class="error">{{ error }}</p> }
        <button class="primary" type="submit"><lucide-icon name="user-plus" [size]="17"></lucide-icon> Зарегистрироваться</button>
        <a routerLink="/login">Уже есть аккаунт</a>
      </form>
    </main>
  `
})
export class RegisterPageComponent {
  username = '';
  email = '';
  password = '';
  error = '';

  constructor(private readonly auth: AuthService, private readonly router: Router) {}

  submit() {
    this.auth.register(this.username, this.email, this.password).subscribe({
      next: () => this.router.navigateByUrl('/profile'),
      error: (err) => this.error = err.error?.detail ?? 'Не удалось зарегистрироваться'
    });
  }
}
