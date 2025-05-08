import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable, from, of, throwError, firstValueFrom } from 'rxjs';
import { switchMap, tap, map, catchError } from 'rxjs/operators';
import {
  Auth,
  signInAnonymously,
  User,
  UserCredential,
  createUserWithEmailAndPassword,
  EmailAuthProvider,
  linkWithCredential,
} from '@angular/fire/auth';
import { environment } from '../environments/environment';
import {
  Firestore,
  doc,
  setDoc,
  getDoc,
  serverTimestamp,
  collection,
  getDocs,
  writeBatch,
  runTransaction,
  CollectionReference,
  DocumentReference,
} from '@angular/fire/firestore';

@Injectable({
  providedIn: 'root',
})
export class AgentService {
  private backendUrl = '/run';
  public appName = 'bookings_agent';
  private _firebaseUid: string | null = null;
  private _authReady: Promise<string>;

  // Use the environment configuration
  private baseUrl = environment.apiUrl.agentService;

  constructor(
    private http: HttpClient,
    private auth: Auth,
    private firestore: Firestore
  ) {
    this._authReady = this.ensureSignedIn();
  }

  // Ensures the user is signed in anonymously and UID is available
  private async ensureSignedIn(): Promise<string> {
    console.log('ensureSignedIn', this.auth.currentUser);

    if (this.auth.currentUser) {
      this._firebaseUid = this.auth.currentUser.uid;

      // Create or update user document in Firestore
      await this.createUserDocument(this._firebaseUid);

      return this._firebaseUid;
    }
    // Otherwise, sign in anonymously
    const cred = await signInAnonymously(this.auth);
    console.log('signInAnonymously', cred);
    this._firebaseUid = cred.user.uid;

    // Create user document for the new anonymous user
    await this.createUserDocument(this._firebaseUid);

    return this._firebaseUid;
  }

  // Create a user document in Firestore
  private async createUserDocument(userId: string): Promise<void> {
    // Top-level try-catch for the entire method
    try {
      // Check if user document exists first
      const userDocRef = doc(this.firestore, 'users', userId);
      let userDoc;

      try {
        userDoc = await getDoc(userDocRef);
      } catch (error) {
        console.warn('Error checking if user document exists:', error);
        // Continue execution even if we can't read the user doc
        userDoc = { exists: () => false };
      }

      // 2. Create/ensure sessions subcollection exists
      try {
        const sessionsCollectionRef = collection(
          this.firestore,
          'users',
          userId,
          'sessions'
        );
        await setDoc(doc(sessionsCollectionRef, '_placeholder'), {
          placeholder: true,
          createdAt: serverTimestamp(),
          userId: userId, // Ensure userId is consistent
        });
        console.log('Ensured sessions subcollection for user:', userId);
      } catch (error) {
        console.warn('Error ensuring sessions subcollection:', error);
        // Continue with other operations
      }

      // Only attempt to create/update the user document if we know its state
      if (userDoc.exists !== undefined) {
        try {
          if (!userDoc.exists()) {
            // Create a new user document if it doesn't exist with minimal fields
            await setDoc(userDocRef, {
              userId: userId,
              displayName: '',
              email: '',
              createdAt: serverTimestamp(),
              updatedAt: serverTimestamp(),
              isAnonymous: true,
              lastSeen: serverTimestamp(),
            });
            console.log('Created new user document:', userId);
          } else {
            // Update last seen time
            await setDoc(
              userDocRef,
              {
                updatedAt: serverTimestamp(),
                lastSeen: serverTimestamp(),
              },
              { merge: true }
            );
          }
        } catch (error) {
          console.warn('Error updating user document:', error);
          // We've already created the subcollections, so this is not fatal
        }
      }
    } catch (error) {
      // Top-level error handler
      console.error('Error in createUserDocument:', error);
      // Don't throw the error to prevent breaking the authentication flow
    }
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
    userId: string | null,
    sessionId: string,
    streaming: boolean = true
  ) {
    const effectiveUserId =
      userId || this.auth.currentUser?.uid || 'anonymous-user';

    if (streaming) {
      // Return an Observable that handles Server-Sent Events (SSE) with streaming
      return new Observable((observer) => {
        const url = `${this.baseUrl}/run_sse`;

        // Prepare request data
        const requestData = {
          app_name: appName,
          user_id: effectiveUserId,
          session_id: sessionId,
          new_message: this.formatMessage(message),
          streaming: true, // Enable token-by-token streaming
        };

        console.log('Starting streaming request to:', url);

        // Make the POST request to initiate streaming
        fetch(url, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(requestData),
        })
          .then((response) => {
            if (!response.ok) {
              throw new Error(
                `Server error: ${response.status} ${response.statusText}`
              );
            }

            // Set up stream processing using the ReadableStream API
            const reader = response.body!.getReader();
            const textDecoder = new TextDecoder();

            // Process the stream chunks as they arrive
            const processStream = async () => {
              try {
                while (true) {
                  const { done, value } = await reader.read();

                  if (done) {
                    console.log('Stream complete');
                    observer.complete();
                    break;
                  }

                  // Decode binary chunk to text
                  const text = textDecoder.decode(value, { stream: true });

                  // Process each line (SSE format sends one event per line)
                  const lines = text.split('\n');

                  for (const line of lines) {
                    // SSE format prefixes data with "data: "
                    if (line.startsWith('data: ')) {
                      try {
                        // Parse the JSON payload
                        const eventData = JSON.parse(line.substring(6));

                        // Send the parsed event to subscribers
                        observer.next(eventData);
                      } catch (error) {
                        console.warn('Error parsing SSE event:', error);
                      }
                    }
                  }
                }
              } catch (error) {
                console.error('Stream processing error:', error);
                observer.error(error);
              }
            };

            // Start processing the stream
            processStream();
          })
          .catch((error) => {
            console.error('Fetch error:', error);
            observer.error(error);
          });

        // Return a cleanup function (called when the observable is unsubscribed)
        return () => {
          console.log('Cleaning up streaming connection');
          // The fetch API will automatically abort the connection when it goes out of scope
        };
      });
    } else {
      // Use the existing implementation for non-streaming requests
      return this.http
        .post<any>(
          `${this.baseUrl}/run_sse`,
          {
            app_name: appName,
            user_id: effectiveUserId,
            session_id: sessionId,
            new_message: this.formatMessage(message),
            streaming: false,
          },
          { responseType: 'text' as any }
        )
        .pipe(
          map((response: string) => {
            if (!response) return [];

            const eventStrings = response
              .split('\n')
              .filter((line) => line.trim().startsWith('data: '));

            return eventStrings
              .map((eventStr) => {
                try {
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
  }

  createOrUpdateSession(
    appName: string,
    userId: string | null,
    sessionId: string,
    state: any = {}
  ) {
    // Ensure userId is never null in the request
    const effectiveUserId =
      userId || this.auth.currentUser?.uid || 'anonymous-user';

    const url = `${this.baseUrl}/apps/${appName}/users/${effectiveUserId}/sessions/${sessionId}`;

    return this.http.post<any>(url, { state });
  }

  // New method to ensure a session exists before sending messages
  ensureSessionExists(
    appName: string,
    userId: string | null,
    sessionId: string
  ): Observable<any> {
    // Ensure userId is available
    if (!userId) {
      return throwError(
        () => new Error('User ID is required to create a session')
      );
    }

    // First, make sure we have a sessions subcollection
    const checkSessionsCollection = async () => {
      try {
        const sessionsCollectionRef = collection(
          this.firestore,
          'users',
          userId,
          'sessions'
        );

        try {
          // Check if placeholder exists and create if needed
          const placeholderDoc = await getDoc(
            doc(sessionsCollectionRef, '_placeholder')
          );
          if (!placeholderDoc.exists()) {
            await setDoc(doc(sessionsCollectionRef, '_placeholder'), {
              placeholder: true,
              createdAt: serverTimestamp(),
              userId: userId, // Ensure userId is consistent
            });
            console.log('Created sessions subcollection for user:', userId);
          }
        } catch (error) {
          console.warn('Error with sessions placeholder document:', error);
          // Continue to session creation
        }

        try {
          // Now check if this specific session exists
          const sessionDoc = await getDoc(
            doc(sessionsCollectionRef, sessionId)
          );
          if (!sessionDoc.exists()) {
            // Create a new session document
            await setDoc(doc(sessionsCollectionRef, sessionId), {
              id: sessionId,
              appName: appName,
              userId: userId, // Ensure userId is consistent
              createdAt: serverTimestamp(),
              updatedAt: serverTimestamp(),
              lastMessage: null,
              status: 'active',
            });
            console.log(
              'Created new session document:',
              sessionId,
              'for user:',
              userId
            );
            return { created: true, sessionId };
          } else {
            // Session already exists
            console.log(
              'Session already exists:',
              sessionId,
              'for user:',
              userId
            );
            return { created: false, sessionId };
          }
        } catch (error) {
          console.warn('Error checking/creating session document:', error);
          // Return as if created so the flow continues
          return { created: true, sessionId, error: true };
        }
      } catch (err) {
        console.error('Error ensuring session exists:', err);
        // Don't throw to prevent breaking the message flow
        return { created: false, sessionId, error: true };
      }
    };

    // Wrap Firestore operations in Observable
    return from(checkSessionsCollection()).pipe(
      // Then call the backend API to ensure session
      switchMap((result) => {
        return this.createOrUpdateSession(appName, userId, sessionId).pipe(
          // Map success response
          map(() => ({
            success: true,
            created: result.created,
            message: result.created ? 'Session created' : 'Session exists',
            sessionId,
          })),
          // Handle API errors
          catchError((error) => {
            // If the error is that the session already exists, treat it as a success
            if (
              error?.error?.detail &&
              typeof error.error.detail === 'string' &&
              error.error.detail.includes('Session already exists')
            ) {
              console.log(
                'Backend session already exists, using existing session'
              );
              return of({
                success: true,
                created: false,
                message: 'Using existing session',
                sessionId,
              });
            }
            // For other errors, log but don't fail since we've already created the Firestore doc
            console.warn(
              'Error from backend ensureSessionExists, continuing anyway:',
              error
            );
            return of({
              success: true,
              created: result.created,
              message: 'Created Firestore session but backend API failed',
              sessionId,
            });
          })
        );
      }),
      // Handle any errors from the Firestore operations
      catchError((err) => {
        console.error('Failed to ensure session exists:', err);
        // Return a valid object instead of throwing to prevent breaking the message flow
        return of({
          success: false,
          created: false,
          message: 'Error creating session but continuing with message flow',
          sessionId,
          error: err,
        });
      })
    );
  }
}
