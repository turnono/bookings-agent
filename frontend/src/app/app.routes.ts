import { Routes } from '@angular/router';
import { ChatComponent } from './chat/chat.component';
import { PaymentCompleteComponent } from './payment-complete/payment-complete.component';

export const routes: Routes = [
  { path: '', component: ChatComponent },
  { path: 'payment-complete', component: PaymentCompleteComponent },
  { path: '**', redirectTo: '' },
];
