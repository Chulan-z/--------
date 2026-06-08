import { Component } from '@angular/core';
import { DatePipe } from '@angular/common';
import { LucideAngularModule } from 'lucide-angular';
import { AuthService } from '../services/auth.service';

@Component({
  selector: 'app-profile-page',
  standalone: true,
  imports: [DatePipe, LucideAngularModule],
  template: `
    <main class="page">
      <h1>Личный кабинет</h1>
      @if (auth.currentUser(); as user) {
        <section class="grid">
          <div class="card">
            <h2><lucide-icon name="user-circle" [size]="20"></lucide-icon> Профиль</h2>
            <p><b>Логин:</b> {{ user.username }}</p>
            <p><b>Email:</b> {{ user.email }}</p>
            <p><b>Активен:</b> {{ user.is_active ? 'да' : 'нет' }}</p>
            <p class="muted">Создан: {{ user.created_at | date:'dd.MM.yyyy HH:mm' }}</p>
          </div>
          <div class="card">
            <h2><lucide-icon name="shield-check" [size]="20"></lucide-icon> Роль и права</h2>
            <p><span class="badge">{{ user.role.name }}</span></p>
            <p class="muted">{{ user.role.permissions.join(', ') }}</p>
          </div>
        </section>
      }
    </main>
  `
})
export class ProfilePageComponent {
  constructor(readonly auth: AuthService) {}
}
