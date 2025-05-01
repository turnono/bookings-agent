import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from, of } from 'rxjs';
import { switchMap, tap, map } from 'rxjs/operators';
import { Auth, signInAnonymously, User } from '@angular/fire/auth';
import { environment } from '../environments/environment';

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private backendUrl = '/run';
  public appName = 'bookings_agent';
  private _firebaseUid: string | null = null;
  private _authReady: Promise<string>;

  private deploymentCloudUrl = environment.apiUrl.agentService;

  constructor(private http: HttpClient, private auth: Auth) {
    this._authReady = this.ensureSignedIn();
  }

  // Ensures the user is signed in anonymously and UID is available
  private async ensureSignedIn(): Promise<string> {
    console.log('ensureSignedIn', this.auth.currentUser);
    if (this.auth.currentUser) {
      this._firebaseUid = this.auth.currentUser.uid;
      return this._firebaseUid;
    }
    // Otherwise, sign in anonymously
    const cred = await signInAnonymously(this.auth);
    console.log('signInAnonymously', cred);
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
    return from(this._authReady);
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

  // Helper to ensure new_message is always in the correct format
  private formatMessage(message: any): any {
    if (typeof message === 'string') {
      return { role: 'user', parts: [{ text: message }] };
    }
    // If already in correct format, return as is
    if (message && message.role && message.parts) {
      return message;
    }
    // Fallback: wrap in parts
    return { role: 'user', parts: [{ text: String(message) }] };
  }

  sendMessage(
    message: any,
    appName: string,
    userId: string,
    sessionId: string,
    streaming: boolean = false
  ) {
    return this.http
      .post<any>(
        this.deploymentCloudUrl + '/run_sse', // Use the built-in ADK endpoint
        {
          app_name: appName,
          user_id: userId,
          session_id: sessionId,
          new_message: this.formatMessage(message),
          streaming,
        },
        { responseType: 'text' as any } // Response is text with "data: {...}" format
      )
      .pipe(
        // Transform SSE format into proper JSON objects
        map((response: string) => {
          if (!response) return [];

          // Split by newline and filter out empty lines
          const eventStrings = response
            .split('\n')
            .filter((line) => line.trim().startsWith('data: '));

          // Parse each event string into a JSON object
          return eventStrings
            .map((eventStr) => {
              try {
                // Remove the 'data: ' prefix and parse JSON
                return JSON.parse(eventStr.substring(6));
              } catch (e) {
                console.error('Error parsing event:', eventStr, e);
                return null;
              }
            })
            .filter((event) => event !== null);
        })
      );
  }

  createOrUpdateSession(
    appName: string,
    userId: string,
    sessionId: string,
    state: any
  ) {
    const url = `${this.deploymentCloudUrl}/apps/${appName}/users/${userId}/sessions/${sessionId}`;

    return this.http.post<any>(url, { state });
  }
}
