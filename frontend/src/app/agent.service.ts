import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

function uuidv4() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function (c) {
    const r = (Math.random() * 16) | 0,
      v = c === 'x' ? r : (r & 0x3) | 0x8;
    return v.toString(16);
  });
}

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private backendUrl = '/run';
  private appName = 'bookings_agent';

  get userId(): string {
    let id = localStorage.getItem('user_id');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('user_id', id);
    }
    return id;
  }

  get sessionId(): string {
    let id = localStorage.getItem('session_id');
    if (!id) {
      id = uuidv4();
      localStorage.setItem('session_id', id);
    }
    return id;
  }

  startNewSession() {
    const newSessionId = uuidv4();
    localStorage.setItem('session_id', newSessionId);
  }

  constructor(private http: HttpClient) {}

  sendMessage(message: string): Observable<any> {
    const payload = {
      app_name: this.appName,
      user_id: this.userId,
      session_id: this.sessionId,
      new_message: {
        role: 'user',
        parts: [{ text: message }],
      },
    };
    return this.http.post<any>(this.backendUrl, payload);
  }

  createSession(): Observable<any> {
    const url = `/apps/${this.appName}/users/${this.userId}/sessions/${this.sessionId}`;
    return this.http.post<any>(url, { state: {} });
  }
}
