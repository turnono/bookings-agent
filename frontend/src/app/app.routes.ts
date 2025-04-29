import { Routes } from '@angular/router';
import { LandingPageComponent } from './landing-page/landing-page.component';
import { ChatComponent } from './chat/chat.component';
import { PaymentCompleteComponent } from './payment-complete/payment-complete.component';

export const routes: Routes = [
  { path: '', component: LandingPageComponent },
  { path: 'bookings-agent', component: ChatComponent },
  { path: 'payment-complete', component: PaymentCompleteComponent },
  { path: '**', redirectTo: '' },
];
