import { bootstrapApplication } from '@angular/platform-browser';
import { AppComponent } from './app/app.component';
import { provideRouter, withComponentInputBinding } from '@angular/router';
import { ChatComponent } from './app/chat/chat.component';
import { PaymentCompleteComponent } from './app/payment-complete/payment-complete.component';
import { LandingPageComponent } from './app/landing-page/landing-page.component';
import { initializeApp, provideFirebaseApp } from '@angular/fire/app';
import { getAuth, provideAuth } from '@angular/fire/auth';
import { getFirestore, provideFirestore } from '@angular/fire/firestore';
import { getFunctions, provideFunctions } from '@angular/fire/functions';
import { getStorage, provideStorage } from '@angular/fire/storage';

bootstrapApplication(AppComponent, {
  providers: [
    provideRouter(
      [
        { path: '', component: LandingPageComponent },
        { path: 'bookings-agent', component: ChatComponent },
        { path: 'payment-complete', component: PaymentCompleteComponent },
        { path: '**', redirectTo: '' },
      ],
      withComponentInputBinding()
    ), provideFirebaseApp(() => initializeApp({ projectId: "taajirah", appId: "1:855515190257:web:2c01b97a96acc83556ea50", databaseURL: "https://taajirah-default-rtdb.europe-west1.firebasedatabase.app", storageBucket: "taajirah.appspot.com", apiKey: "AIzaSyDGaH72jq3Ev-Jue-5qm72OzpRCWzQMh9U", authDomain: "taajirah.firebaseapp.com", messagingSenderId: "855515190257", measurementId: "G-SP3FWBJNT3" })), provideAuth(() => getAuth()), provideFirestore(() => getFirestore()), provideFunctions(() => getFunctions()), provideStorage(() => getStorage()),
  ],
});
