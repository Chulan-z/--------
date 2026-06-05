import { bootstrapApplication } from '@angular/platform-browser';
import { provideHttpClient, withInterceptors } from '@angular/common/http';
import { importProvidersFrom } from '@angular/core';
import { provideRouter } from '@angular/router';
import { DatabaseBackup, ExternalLink, LogIn, LucideAngularModule, Newspaper, Play, RefreshCcw, RotateCcw, Save, Search, ShieldCheck, UserCircle, UserPlus } from 'lucide-angular';
import { AppComponent } from './app/app.component';
import { routes } from './app/app.routes';
import { authInterceptor } from './app/services/auth.interceptor';

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(routes),
    provideHttpClient(withInterceptors([authInterceptor])),
    importProvidersFrom(LucideAngularModule.pick({
      DatabaseBackup,
      ExternalLink,
      LogIn,
      Newspaper,
      Play,
      RefreshCcw,
      RotateCcw,
      Save,
      Search,
      ShieldCheck,
      UserCircle,
      UserPlus
    }))
  ]
}).catch((err) => console.error(err));
