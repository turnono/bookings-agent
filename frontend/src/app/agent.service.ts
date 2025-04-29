import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from, of } from 'rxjs';
import { switchMap, tap } from 'rxjs/operators';
import { Auth, signInAnonymously, User } from '@angular/fire/auth';

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private backendUrl = '/run';
  private appName = 'bookings_agent';
  private _firebaseUid: string | null = null;
  private _authReady: Promise<string>;

  constructor(private http: HttpClient, private auth: Auth) {
    this._authReady = this.ensureSignedIn();
  }

  // Ensures the user is signed in anonymously and UID is available
  private async ensureSignedIn(): Promise<string> {
    if (this.auth.currentUser) {
      this._firebaseUid = this.auth.currentUser.uid;
      return this._firebaseUid;
    }
    // Otherwise, sign in anonymously
    const cred = await signInAnonymously(this.auth);
    this._firebaseUid = cred.user.uid;
    return this._firebaseUid;
  }

  // Returns a promise that resolves to the Firebase UID
  get userId(): string {
    if (this.auth.currentUser) {
      return this.auth.currentUser.uid;
    }
    throw new Error('Firebase UID not ready yet.');
  }

  // Returns an observable that emits when UID is ready
  getUserId$(): Observable<string> {
    if (this.auth.currentUser) return of(this.auth.currentUser.uid);
    return from(this.ensureSignedIn());
  }

  get sessionId(): string {
    let id = localStorage.getItem('session_id');
    if (!id) {
      id = crypto.randomUUID();
      localStorage.setItem('session_id', id);
    }
    return id;
  }

  startNewSession() {
    const newSessionId = crypto.randomUUID();
    localStorage.setItem('session_id', newSessionId);
  }

  sendMessage(message: string): Observable<any> {
    // Wait for UID to be ready before sending
    return this.getUserId$().pipe(
      switchMap((uid) => {
        const payload = {
          app_name: this.appName,
          user_id: uid,
          session_id: this.sessionId,
          new_message: {
            role: 'user',
            parts: [{ text: message }],
          },
        };
        return this.http.post<any>(this.backendUrl, payload);
      })
    );
  }

  createSession(): Observable<any> {
    return this.getUserId$().pipe(
      switchMap((uid) => {
        const url = `/apps/${this.appName}/users/${uid}/sessions/${this.sessionId}`;
        return this.http.post<any>(url, { state: {} });
      })
    );
  }
}
