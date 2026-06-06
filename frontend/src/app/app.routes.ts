import { Routes } from '@angular/router';
import { adminGuard, authGuard } from './guards/auth.guard';
import { AdminPageComponent } from './pages/admin-page.component';
import { FeedPageComponent } from './pages/feed-page.component';
import { LoginPageComponent } from './pages/login-page.component';
import { ProfilePageComponent } from './pages/profile-page.component';
import { RegisterPageComponent } from './pages/register-page.component';

export const routes: Routes = [
  { path: '', component: FeedPageComponent },
  { path: 'login', component: LoginPageComponent },
  { path: 'register', component: RegisterPageComponent },
  { path: 'profile', component: ProfilePageComponent, canActivate: [authGuard] },
  { path: 'admin', component: AdminPageComponent, canActivate: [authGuard, adminGuard] },
  { path: '**', redirectTo: '' }
];
