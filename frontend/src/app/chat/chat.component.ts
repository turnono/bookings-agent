import {
  Component,
  OnInit,
  ViewChild,
  ElementRef,
  AfterViewInit,
  OnDestroy,
} from '@angular/core';
import { AgentService } from '../agent.service';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatChipsModule } from '@angular/material/chips';
import { MatIconModule } from '@angular/material/icon';
import { MatCardModule } from '@angular/material/card';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatDividerModule } from '@angular/material/divider';
import { Timestamp } from '@angular/fire/firestore';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Subject } from 'rxjs';
import { takeUntil } from 'rxjs/operators';
import { MatDialog } from '@angular/material/dialog';
import { GenericFunctionDialogComponent } from '../dialogs/generic-function-dialog.component';
import { QualifierDialogComponent } from '../dialogs/qualifier-dialog.component';
import { ServiceSelectionDialogComponent } from '../dialogs/service-selection-dialog.component';
import { DatePickerDialogComponent } from '../dialogs/date-picker-dialog.component';
import { SlotPickerDialogComponent } from '../dialogs/slot-picker-dialog.component';
import { EmailDialogComponent } from '../dialogs/email-dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';
import { switchMap } from 'rxjs/operators';
import { Auth } from '@angular/fire/auth';

import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';
import { environment } from '../../environments/environment';

interface FunctionCall {
  name: string;
  arguments: any;
}

interface ChatMessage {
  role: 'user' | 'agent' | 'system';
  text: string;
  event?: string;
  functionCall?: FunctionCall;
  functionResponse?: any;
  timestamp?: Timestamp;
}

// Map function names to user-friendly one-liners
const FUNCTION_FRIENDLY_MESSAGES: Record<string, string> = {
  transfer_to_agent: 'Connecting you to an agent…',
  availability_agent: 'Checking available slots…',
  'availability_agent.getSlots': 'Checking available slots…',
  select_time_slot: 'Preparing available time slots…',
  screening_question: 'Just a quick question…',
  validate_email: 'Validating your email…',
  create_booking: 'Creating your booking…',
  send_invite: 'Sending your calendar invitation…',
  // Add more mappings as needed
};

const FUNCTION_DIALOG_MAP: Record<string, any> = {
  qualifyUser: QualifierDialogComponent,
  selectService: ServiceSelectionDialogComponent,
  getAvailableDates: DatePickerDialogComponent,
  getAvailableSlots: SlotPickerDialogComponent,
  transfer_to_agent: QualifierDialogComponent,
  get_available_time_slots: SlotPickerDialogComponent,
  validate_email: EmailDialogComponent,
};

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  standalone: true,
  imports: [
    ReactiveFormsModule,
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatChipsModule,
    MatProgressSpinnerModule,
    MatCardModule,
    MatIconModule,
    MatDividerModule,
    MatToolbarModule,
  ],
  styleUrls: ['./chat.component.scss'],
  animations: [
    trigger('fadeIn', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(16px)' }),
        animate(
          '400ms cubic-bezier(.35,0,.25,1)',
          style({ opacity: 1, transform: 'none' })
        ),
      ]),
    ]),
  ],
})
export class ChatComponent implements OnInit, AfterViewInit, OnDestroy {
  messages: ChatMessage[] = [];
  userInput: string = '';
  loading = false;
  errorMessage: string = '';

  // Interactive controls state
  activeFunctionCall: FunctionCall | null = null;
  detectedFunctionCalls: FunctionCall[] = [];
  screeningAnswer: string = '';
  selectedDate: Date | null = null;
  availableDates: string[] = [];
  availableSlots: string[] = [];
  selectedSlot: string = '';
  userEmail: string = '';
  bookingTopic: string = '';
  bookingId: string = '';
  // Track session creation status
  private sessionCreated: boolean = false;
  // Flag to prevent multiple booking submissions
  private bookingInProgress: boolean = false;

  @ViewChild('messageList') messageListRef!: ElementRef;
  @ViewChild('chatInput') chatInputRef!: ElementRef;

  currentYear = new Date().getFullYear();

  // Date filter for mat-datepicker
  dateFilter = (date: Date | null): boolean => {
    if (!date) return false;
    const dateStr = date.toISOString().split('T')[0];
    return this.availableDates.includes(dateStr);
  };

  private destroy$ = new Subject<void>();
  private mutationObserver: MutationObserver | null = null;
  private firebaseUserId: string | null = null;

  constructor(
    private agentService: AgentService,
    private dialog: MatDialog,
    private snackBar: MatSnackBar,
    private auth: Auth
  ) {}

  ngOnInit() {
    // Monitor auth state changes to keep firebaseUserId in sync
    this.auth.onAuthStateChanged((user) => {
      if (user) {
        console.log(
          `Auth state changed - current user: ${user.uid}, isAnonymous: ${user.isAnonymous}`
        );
        this.firebaseUserId = user.uid;
      } else {
        console.log('Auth state changed - user signed out');
        this.firebaseUserId = null;
      }
    });

    this.agentService.getUserId$().subscribe({
      next: (uid) => {
        this.firebaseUserId = uid;
        console.log(`Initial Firebase UID set to: ${uid}`);
        this.newChat(); // Only start chat after UID is ready
      },
      error: (err) => {
        console.error('Error getting Firebase UID:', err);
        this.handleError('Could not sign in anonymously.');
      },
    });
  }

  ngAfterViewInit() {
    this.scrollToBottom();
    this.setupScrollObserver();
  }

  setupScrollObserver() {
    if (this.messageListRef && !this.mutationObserver) {
      // Create a new observer
      this.mutationObserver = new MutationObserver(() => {
        this.scrollToBottom();
      });

      // Start observing
      this.mutationObserver.observe(this.messageListRef.nativeElement, {
        childList: true,
        subtree: true,
      });
    }
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.messageListRef) {
        const element = this.messageListRef.nativeElement;
        element.scrollTop = element.scrollHeight;
      }
    }, 100);
  }

  focusInput() {
    setTimeout(() => {
      if (this.chatInputRef) {
        this.chatInputRef.nativeElement.focus();
      }
    }, 0);
  }

  handleError(message: string) {
    this.errorMessage = message;
    this.snackBar.open(message, 'Dismiss', {
      duration: 5000,
      horizontalPosition: 'center',
      verticalPosition: 'bottom',
      panelClass: ['error-snackbar'],
    });
  }

  dismissError() {
    this.errorMessage = '';
  }

  sendMessage() {
    if (!this.userInput.trim()) return;

    // Save the input before clearing it
    const input = this.userInput;
    this.userInput = '';

    this.messages.push({
      role: 'user',
      text: input,
      timestamp: Timestamp.now(),
    });

    this.loading = true;
    this.scrollToBottom();

    // Extract potential topic for booking
    if (!this.bookingTopic && input.length > 10) {
      this.bookingTopic = input;
    }

    // Only ensure session if not already created
    if (this.sessionCreated) {
      // Session already exists, just send the message
      this.agentService
        .sendMessage(
          input,
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    } else {
      // First ensure a session exists
      this.agentService
        .ensureSessionExists(
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(
          // Then send the message
          switchMap(() => {
            // Mark session as created
            this.sessionCreated = true;
            return this.agentService.sendMessage(
              input,
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            );
          }),
          takeUntil(this.destroy$)
        )
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    }
  }

  handleAgentEvents(events: any) {
    let messageAdded = false;

    // Check if we received an API rate limit error
    const hasRateLimitError = events.some((event: any) =>
      event.content?.parts?.some(
        (part: any) =>
          part.text?.includes('rate limit') ||
          part.text?.includes('quota exceeded')
      )
    );

    if (hasRateLimitError) {
      this.handleError(
        'The service is experiencing high demand. Please try again in a moment.'
      );
      this.loading = false;
      this.bookingInProgress = false; // Reset booking flag if rate limited
      return;
    }

    for (const event of events) {
      if (event.content && event.content.parts) {
        for (const part of event.content.parts) {
          // Extract and process function calls
          if (part.functionCall) {
            const functionCall: FunctionCall = {
              name: part.functionCall.name,
              arguments: this.parseFunctionArguments(part.functionCall.args),
            };
            // Use friendly message if available
            const friendlyText =
              FUNCTION_FRIENDLY_MESSAGES[functionCall.name] || 'Processing…';
            this.messages.push({
              role: 'agent',
              text: friendlyText,
              functionCall: functionCall,
              timestamp: Timestamp.now(),
            });
            this.activeFunctionCall = functionCall;
            this.detectedFunctionCalls.push(functionCall);
            console.log('Function call detected:', functionCall);
            this.handleFunctionCall(functionCall);
            messageAdded = true;
          } else if (part.functionResponse) {
            this.activeFunctionCall = null;
            this.handleFunctionResponse(part.functionResponse);
          }

          // Display regular text messages
          if (part.text) {
            this.messages.push({
              role: 'agent',
              text: part.text,
              timestamp: Timestamp.now(),
            });
            messageAdded = true;
          }
        }
      }
    }

    this.loading = false;

    // Ensure scroll happens after DOM update
    if (messageAdded) {
      this.scrollToBottom();
      // Apply a second scroll after a slight delay to handle any rendering delays
      setTimeout(() => this.scrollToBottom(), 300);
    }

    this.focusInput();
  }

  // Helper method to parse function arguments
  parseFunctionArguments(args: any): any {
    // If args is a string (JSON string), parse it
    if (typeof args === 'string') {
      try {
        return JSON.parse(args);
      } catch (e) {
        console.error('Error parsing function arguments:', e);
        return args; // Return as is if parsing fails
      }
    }

    // If it's already an object, return it
    return args;
  }

  // Updated to use FunctionCall interface
  handleFunctionCall(func: FunctionCall) {
    // Reset all controls
    this.screeningAnswer = '';
    this.selectedDate = null;
    this.availableDates = [];
    this.availableSlots = [];
    this.selectedSlot = '';

    // Handle validate_email function call
    if (func.name === 'validate_email') {
      // Directly open the registration dialog when email validation is requested
      // Skip the email entry step as it will be handled in the registration dialog
    }
    // Screening question
    else if (func.name === 'screening_question') {
      // args: { question: string }
      // Show input for answer
    } else if (func.name === 'availability_agent.getSlots') {
      // Extract validDates from arguments
      this.availableDates = func.arguments?.validDates || [];
    } else if (func.name === 'select_time_slot') {
      // Extract slots from arguments
      this.availableSlots = func.arguments?.slots || [];
    } else if (func.name === 'create_booking') {
      // Before creating booking, check if user is anonymous
      if (this.auth.currentUser?.isAnonymous) {
        // Prompt for registration before proceeding
      } else {
        // User already registered, proceed with booking
        this.handleBookingCreation(func);
      }
    }
  }

  // Helper method to reset booking state
  private resetBookingState() {
    this.bookingInProgress = false;
    this.activeFunctionCall = null;
    this.selectedSlot = '';
    this.bookingId = '';
  }

  // Helper method to handle booking creation
  private handleBookingCreation(func: FunctionCall) {
    // Prevent multiple submissions
    if (this.bookingInProgress) {
      console.log('Booking already in progress, ignoring duplicate request');
      return;
    }

    // Set flag to prevent duplicate submissions
    this.bookingInProgress = true;

    // Capture booking details for later reference
    if (func.arguments?.slot) {
      this.selectedSlot = func.arguments.slot;
    }
    if (func.arguments?.topic) {
      this.bookingTopic = func.arguments.topic;
    }
    if (func.arguments?.email) {
      this.userEmail = func.arguments.email;
    }

    // Continue with booking flow
    this.messages.push({
      role: 'user',
      text: `I confirm booking for slot: ${this.selectedSlot}`,
      timestamp: Timestamp.now(),
    });

    this.loading = true;
    this.agentService
      .sendMessage(
        `I confirm booking for slot: ${this.selectedSlot}`,
        this.agentService.appName,
        this.firebaseUserId!,
        this.agentService.sessionId
      )
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: (events) => {
          this.handleAgentEvents(events);
          // Reset the flag when booking is complete
          this.bookingInProgress = false;
        },
        error: (err) => {
          this.handleError('Failed to create booking. Please try again.');
          // Reset the booking state on error
          this.resetBookingState();
        },
      });
  }

  handleFunctionResponse(funcResp: any) {
    if (!funcResp || !funcResp.name) {
      console.error('Invalid function response:', funcResp);
      return;
    }
    console.log('Function response received:', funcResp);

    // Use friendly message if available
    const friendlyText = FUNCTION_FRIENDLY_MESSAGES[funcResp.name] || 'Done.';
    this.messages.push({
      role: 'agent',
      text: friendlyText,
      functionResponse: funcResp,
      timestamp: Timestamp.now(),
    });

    // Handle function-specific responses
    if (funcResp.name === 'availability_agent.getSlots') {
      if (funcResp.response?.slots) {
        this.availableSlots = funcResp.response.slots;
      }
    } else if (funcResp.name === 'create_booking') {
      // Store booking ID if available
      if (funcResp.response?.booking_id) {
        this.bookingId = funcResp.response.booking_id;
      }

      // Show snackbar for booking success
      if (funcResp.response?.success) {
        this.snackBar.open(
          funcResp.response.status === 'created'
            ? 'Booking created successfully!'
            : 'This slot is already booked.',
          'Dismiss',
          {
            duration: 5000,
            horizontalPosition: 'center',
            verticalPosition: 'bottom',
            panelClass: ['success-snackbar'],
          }
        );
      }
    } else if (funcResp.name === 'send_invite') {
      // Show snackbar based on invitation status
      if (funcResp.response?.status === 'confirmed') {
        this.snackBar.open(
          'Calendar invitation sent successfully!',
          'Dismiss',
          {
            duration: 5000,
            horizontalPosition: 'center',
            verticalPosition: 'bottom',
            panelClass: ['success-snackbar'],
          }
        );
      } else if (funcResp.response?.status === 'pending_invite_error') {
        this.snackBar.open(
          "Booking confirmed, but there was an issue sending the calendar invitation. We'll fix this manually.",
          'Dismiss',
          {
            duration: 7000,
            horizontalPosition: 'center',
            verticalPosition: 'bottom',
            panelClass: ['warning-snackbar'],
          }
        );
      }
    }
  }

  submitScreeningAnswer() {
    if (!this.screeningAnswer.trim()) return;
    this.messages.push({
      role: 'user',
      text: this.screeningAnswer,
      timestamp: Timestamp.now(),
    });
    this.loading = true;
    this.scrollToBottom();

    // Only ensure session if not already created
    if (this.sessionCreated) {
      this.agentService
        .sendMessage(
          this.screeningAnswer,
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    } else {
      // First ensure a session exists
      this.agentService
        .ensureSessionExists(
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(
          switchMap(() => {
            // Mark session as created
            this.sessionCreated = true;
            return this.agentService.sendMessage(
              this.screeningAnswer,
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            );
          }),
          takeUntil(this.destroy$)
        )
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    }
    this.activeFunctionCall = null;
    this.screeningAnswer = '';
  }

  submitDateSelection() {
    if (!this.selectedDate) return;
    const dateStr = this.selectedDate.toISOString().split('T')[0];
    this.messages.push({
      role: 'user',
      text: dateStr,
      timestamp: Timestamp.now(),
    });
    this.loading = true;
    this.scrollToBottom();

    // Only ensure session if not already created
    if (this.sessionCreated) {
      this.agentService
        .sendMessage(
          dateStr,
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    } else {
      // First ensure a session exists
      this.agentService
        .ensureSessionExists(
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(
          switchMap(() => {
            // Mark session as created
            this.sessionCreated = true;
            return this.agentService.sendMessage(
              dateStr,
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            );
          }),
          takeUntil(this.destroy$)
        )
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    }
    this.activeFunctionCall = null;
    this.selectedDate = null;
  }

  submitSlotSelection(slot: string) {
    this.selectedSlot = slot;
    this.messages.push({
      role: 'user',
      text: slot,
      timestamp: Timestamp.now(),
    });
    this.loading = true;
    this.scrollToBottom();

    // Only ensure session if not already created
    if (this.sessionCreated) {
      this.agentService
        .sendMessage(
          slot,
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(takeUntil(this.destroy$))
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    } else {
      // First ensure a session exists
      this.agentService
        .ensureSessionExists(
          this.agentService.appName,
          this.firebaseUserId!,
          this.agentService.sessionId
        )
        .pipe(
          switchMap(() => {
            // Mark session as created
            this.sessionCreated = true;
            return this.agentService.sendMessage(
              slot,
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            );
          }),
          takeUntil(this.destroy$)
        )
        .subscribe({
          next: (events) => {
            this.handleAgentEvents(events);
            this.loading = false;
            this.focusInput();
          },
          error: (err) => {
            console.error('AgentService error:', err);
            let errorMsg = 'Error contacting agent.';
            if (err?.error?.message) {
              errorMsg += ` Details: ${err.error.message}`;
            } else if (err?.message) {
              errorMsg += ` Details: ${err.message}`;
            } else if (typeof err === 'string') {
              errorMsg += ` Details: ${err}`;
            }
            this.handleError(errorMsg);
            this.loading = false;
            this.scrollToBottom();
          },
        });
    }
    this.activeFunctionCall = null;
    this.selectedSlot = '';
  }

  newChat() {
    if (!this.firebaseUserId) {
      this.handleError('Firebase UID not ready yet.');
      return;
    }

    // Create a new session ID
    this.agentService.startNewSession();
    // Reset session created flag
    this.sessionCreated = false;

    // Ensure the session exists on the backend before continuing
    this.agentService
      .ensureSessionExists(
        this.agentService.appName,
        this.firebaseUserId,
        this.agentService.sessionId
      )
      .subscribe({
        next: () => {
          console.log('Session created successfully');
          // Mark session as created
          this.sessionCreated = true;
          // Initialize chat UI after session is created
          this.initializeChatUI();
        },
        error: (err) => {
          console.error('Failed to create session:', err);
          this.handleError(
            'Failed to initialize chat session. Please try again.'
          );

          // Still show the UI but warn the user
          this.initializeChatUI();
        },
      });
  }

  // Separate method to initialize the chat UI
  private initializeChatUI() {
    this.messages = [
      {
        role: 'agent',
        text: `Hi there! I'm the booking assistant for ${environment.ownerFullName}. How can I help you today?`,
        timestamp: Timestamp.now(),
      },
    ];
    this.activeFunctionCall = null;
    this.detectedFunctionCalls = [];
    this.screeningAnswer = '';
    this.selectedDate = null;
    this.availableDates = [];
    this.availableSlots = [];
    this.selectedSlot = '';
    this.userEmail = '';
    this.bookingTopic = '';
    this.bookingId = '';
    this.bookingInProgress = false;
    // Don't reset sessionCreated here, as it should persist for the duration of the chat
    this.focusInput();
  }

  ngOnDestroy() {
    this.destroy$.next();
    this.destroy$.complete();
    if (this.mutationObserver) {
      this.mutationObserver.disconnect();
      this.mutationObserver = null;
    }
  }
}
