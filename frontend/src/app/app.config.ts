import { ApplicationConfig, provideZoneChangeDetection } from '@angular/core';
import { provideRouter } from '@angular/router';
import { provideHttpClient } from '@angular/common/http';
import { provideFirebaseApp, initializeApp } from '@angular/fire/app';
import { provideAuth, getAuth } from '@angular/fire/auth';
import { provideFirestore, getFirestore } from '@angular/fire/firestore';
import { provideFunctions, getFunctions } from '@angular/fire/functions';
import { provideStorage, getStorage } from '@angular/fire/storage';

import { routes } from './app.routes';
import { provideAnimationsAsync } from '@angular/platform-browser/animations/async';

export const appConfig: ApplicationConfig = {
  providers: [
    provideZoneChangeDetection({ eventCoalescing: true }),
    provideRouter(routes),
    provideHttpClient(),
    provideAnimationsAsync(),
    provideFirebaseApp(() =>
      initializeApp({
        projectId: 'taajirah',
        appId: '1:855515190257:web:2c01b97a96acc83556ea50',
        databaseURL:
          'https://taajirah-default-rtdb.europe-west1.firebasedatabase.app',
        storageBucket: 'taajirah.appspot.com',
        apiKey: 'AIzaSyDGaH72jq3Ev-Jue-5qm72OzpRCWzQMh9U',
        authDomain: 'taajirah.firebaseapp.com',
        messagingSenderId: '855515190257',
        measurementId: 'G-SP3FWBJNT3',
      })
    ),
    provideAuth(() => getAuth()),
    provideFirestore(() => getFirestore()),
    provideFunctions(() => getFunctions()),
    provideStorage(() => getStorage()),
  ],
};
