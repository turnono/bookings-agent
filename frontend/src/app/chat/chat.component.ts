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
import { FormatMessagePipe } from './format-message.pipe';

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
  completed?: boolean;
  isStreaming?: boolean;
}

// Map function names to user-friendly one-liners
const FUNCTION_FRIENDLY_MESSAGES: Record<string, string> = {
  transfer_to_agent: 'Connecting to agent…',
  availability_agent: 'Checking availability…',
  'availability_agent.getSlots': 'Finding slots…',
  select_time_slot: 'Available time slots…',
  screening_question: 'Qualification…',
  validate_email: 'Validating email…',
  create_booking: 'Creating booking…',
  send_invite: 'Sending invitation…',
  current_year: 'Getting date info…',
  current_time: 'Getting time info…',
  get_all_available_slots: 'Checking calendar…',
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

// Add new interfaces for time slot grouping
interface SlotInfo {
  time: string; // Just the time part (e.g., "18:00-18:30")
  fullSlot: string; // The full date+time string as received from the API
}

interface DateGroup {
  date: string; // Full date (e.g., "May 13, 2025")
  dayOfWeek: string; // Day of week (e.g., "Tuesday")
  dateObj: Date; // Date object for sorting
  slots: SlotInfo[]; // Time slots for this date
}

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
    FormatMessagePipe,
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
    trigger('fadeInOut', [
      transition(':enter', [
        style({ opacity: 0, transform: 'translateY(10px)' }),
        animate('400ms ease-out', style({ opacity: 1, transform: 'none' })),
      ]),
      transition(':leave', [
        animate(
          '300ms ease-in',
          style({ opacity: 0, transform: 'translateY(-10px)' })
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

  // Add new property for grouped time slots
  groupedTimeSlots: DateGroup[] = [];

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
          this.agentService.sessionId,
          true
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
              this.agentService.sessionId,
              true
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
    try {
      // If events is not an array in streaming mode, wrap it in an array
      if (!Array.isArray(events)) {
        events = [events];
      }

      // Check if we received an API rate limit error
      const hasRateLimitError = events.some((event: any) =>
        this.isRateLimitError(event)
      );

      if (hasRateLimitError) {
        this.handleError(
          'The service is experiencing high demand. Please try again in a moment.'
        );
        this.loading = false;
        this.bookingInProgress = false; // Reset booking flag if rate limited
        return;
      }

      // Process each event
      let hasCompletedEvent = false;

      for (const event of events) {
        // Skip invalid events
        if (!event || !event.content || !event.content.parts) {
          continue;
        }

        // Process each part in the event
        for (const part of event.content.parts) {
          // Handle function calls
          if (part.functionCall) {
            this.handleFunctionCallPart(part);
          }
          // Handle function responses
          else if (part.functionResponse) {
            this.activeFunctionCall = null;
            this.handleFunctionResponse(part.functionResponse);
          }
          // Handle text messages
          else if (part.text) {
            this.handleTextPart(part, event.partial === true);
          }
        }

        // Track if we have a completed event (non-partial)
        if (!event.partial) {
          hasCompletedEvent = true;
        }
      }

      // Only scroll to bottom once after processing all events
      setTimeout(() => this.scrollToBottom(), 0);

      // Only remove loading indicator when we receive a completed event
      if (hasCompletedEvent) {
        this.loading = false;
        this.focusInput();

        // Mark any streaming messages as complete
        this.messages.forEach((msg) => {
          if (msg.isStreaming) {
            msg.isStreaming = false;
            msg.completed = true;
          }
        });
      }
    } catch (error) {
      console.error('Error handling agent events:', error);
      this.handleError(
        'An error occurred while processing the agent response.'
      );
      this.loading = false;
    }
  }

  // Helper method to handle function call parts
  private handleFunctionCallPart(part: any) {
    const functionCall: FunctionCall = {
      name: part.functionCall.name,
      arguments: this.parseFunctionArguments(part.functionCall.args),
    };

    // Use friendly message if available
    const friendlyText =
      FUNCTION_FRIENDLY_MESSAGES[functionCall.name] || 'Processing…';

    // Find existing "processing" message to update instead of adding new one
    const existingFunctionCallMsg = this.messages.find(
      (msg) =>
        msg.role === 'agent' &&
        msg.functionCall?.name === functionCall.name &&
        !msg.completed
    );

    if (existingFunctionCallMsg) {
      // Update existing message
      existingFunctionCallMsg.text = friendlyText;
      existingFunctionCallMsg.functionCall = functionCall;
    } else {
      // Add new message
      this.messages.push({
        role: 'agent',
        text: friendlyText,
        functionCall: functionCall,
        timestamp: Timestamp.now(),
        completed: false,
        isStreaming: false,
      });
    }

    this.activeFunctionCall = functionCall;
    this.detectedFunctionCalls.push(functionCall);
    console.log('Function call detected:', functionCall);
    this.handleFunctionCall(functionCall);
  }

  // Simple helper method to handle text parts
  private handleTextPart(part: any, isPartial: boolean) {
    // Skip empty text messages
    if (!part.text || !part.text.trim()) {
      return;
    }

    // Process the text for formatting (if it's from the agent)
    const processedText = part.text;

    const lastMessage =
      this.messages.length > 0 ? this.messages[this.messages.length - 1] : null;

    // Only append to the last message if it's a streaming agent message without a function call
    const shouldAppendToLastMessage =
      lastMessage &&
      lastMessage.role === 'agent' &&
      !lastMessage.functionCall &&
      lastMessage.isStreaming;

    if (shouldAppendToLastMessage) {
      // For streaming messages, replace the entire text as the server sends the full accumulated text
      lastMessage.text = processedText;
      lastMessage.isStreaming = isPartial;

      if (!isPartial) {
        lastMessage.completed = true;
      }
    } else {
      // Create a new message
      this.messages.push({
        role: 'agent',
        text: processedText,
        timestamp: Timestamp.now(),
        completed: !isPartial,
        isStreaming: isPartial,
      });
    }

    // Always scroll when we get new text
    this.scrollToBottom();
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
    this.groupedTimeSlots = []; // Reset grouped slots

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
      // Group slots by date
      this.groupTimeSlotsByDate();
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
        this.agentService.sessionId,
        true
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
          this.agentService.sessionId,
          true
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
              this.agentService.sessionId,
              true
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
          this.agentService.sessionId,
          true
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
              this.agentService.sessionId,
              true
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

    // Format slot for a nicer display
    const formattedSlot = this.formatSlotForDisplay(slot);

    this.messages.push({
      role: 'user',
      text: `I'd like to book the slot on ${formattedSlot}`,
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
          this.agentService.sessionId,
          true
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
              this.agentService.sessionId,
              true
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

  // Helper method to format slot for display
  private formatSlotForDisplay(slot: string): string {
    // Slot format: "Tuesday, May 13, 2025 at 18:00-18:30"
    const parts = slot.split(' at ');
    if (parts.length !== 2) return slot;

    const dateString = parts[0].trim();
    const timeString = parts[1].trim();

    // Convert 24h time to 12h format with AM/PM
    const timeFormatted = timeString.replace(
      /(\d{2}):(\d{2})-(\d{2}):(\d{2})/g,
      (match, startHour, startMin, endHour, endMin) => {
        const startH = parseInt(startHour);
        const endH = parseInt(endHour);

        const startAmPm = startH >= 12 ? 'PM' : 'AM';
        const endAmPm = endH >= 12 ? 'PM' : 'AM';

        const startH12 = startH % 12 || 12;
        const endH12 = endH % 12 || 12;

        return `${startH12}:${startMin} ${startAmPm} - ${endH12}:${endMin} ${endAmPm}`;
      }
    );

    return `${dateString} at ${timeFormatted}`;
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
        text: `Hi there! I'm an AI Agent for ${environment.ownerFullName}. What can I do for you today?`,
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

  // Helper method to check if there are any streaming messages
  hasStreamingMessages(): boolean {
    return this.messages.some((msg) => msg.isStreaming === true);
  }

  // Helper method to check for rate limit errors
  private isRateLimitError(event: any): boolean {
    return event.content?.parts?.some(
      (part: any) =>
        part.text?.includes('rate limit') ||
        part.text?.includes('quota exceeded')
    );
  }

  // Helper to get a user-friendly function name
  getFunctionDisplayName(name: string): string {
    // For transfer_to_agent, show which agent is being connected to
    if (
      name === 'transfer_to_agent' &&
      this.activeFunctionCall?.arguments?.agent_name
    ) {
      const agentName = this.getAgentDisplayName(
        this.activeFunctionCall.arguments.agent_name
      );
      return `Connecting to ${agentName}`;
    }

    // Use predefined friendly names if available
    if (FUNCTION_FRIENDLY_MESSAGES[name]) {
      // Extract just the action part without the ellipsis
      return FUNCTION_FRIENDLY_MESSAGES[name].replace('…', '');
    }

    // Handle sub-agent calls (format: agent.method)
    if (name.includes('.')) {
      const parts = name.split('.');
      // Capitalize each part and format
      return parts.map((part) => this.formatNamePart(part)).join(' → ');
    }

    // Format snake_case to Title Case
    return this.formatNamePart(name);
  }

  // Helper to get a user-friendly agent name
  getAgentDisplayName(agentName: string): string {
    const agentDisplayNames: Record<string, string> = {
      info_agent: 'Info Agent',
      booking_validator: 'Booking Validator',
      inquiry_collector: 'Inquiry Agent',
      intent_extractor: 'Intent Analyzer',
      // Add more agent mappings as needed
    };

    return agentDisplayNames[agentName] || this.formatNamePart(agentName);
  }

  // Helper to format name parts
  private formatNamePart(name: string): string {
    return name
      .split('_')
      .map((word) => word.charAt(0).toUpperCase() + word.slice(1))
      .join(' ');
  }

  // Method to group time slots by date for better display
  private groupTimeSlotsByDate() {
    const dateGroups = new Map<string, DateGroup>();

    // Format options for displaying dates
    const dateOptions: Intl.DateTimeFormatOptions = {
      month: 'long',
      day: 'numeric',
      year: 'numeric',
    };

    const dayOptions: Intl.DateTimeFormatOptions = {
      weekday: 'long',
    };

    // Process each slot
    for (const slot of this.availableSlots) {
      // Parse the slot string (format: "Tuesday, May 13, 2025 at 18:00-18:30")
      const parts = slot.split(' at ');
      if (parts.length !== 2) continue;

      const dateString = parts[0].trim();
      const timeString = parts[1].trim();

      // Create a date object for sorting
      const dateObj = new Date(dateString);

      // Format the date nicer
      const formattedDate = dateObj.toLocaleDateString('en-US', dateOptions);
      const dayOfWeek = dateObj.toLocaleDateString('en-US', dayOptions);

      // Get or create the date group
      let dateGroup = dateGroups.get(formattedDate);
      if (!dateGroup) {
        dateGroup = {
          date: formattedDate,
          dayOfWeek: dayOfWeek,
          dateObj: dateObj,
          slots: [],
        };
        dateGroups.set(formattedDate, dateGroup);
      }

      // Add the slot to the group
      dateGroup.slots.push({
        time: timeString,
        fullSlot: slot,
      });
    }

    // Convert map to array and sort by date
    this.groupedTimeSlots = Array.from(dateGroups.values()).sort(
      (a, b) => a.dateObj.getTime() - b.dateObj.getTime()
    );
  }

  // Helper method to determine if message text should be shown
  shouldShowMessageText(msg: ChatMessage): boolean {
    // Don't show generic function call status messages like "Processing..." or "Done."
    if (!msg.text) return false;

    // Don't show redundant "Processing..." text for function calls
    if (
      msg.functionCall &&
      (msg.text === 'Processing…' ||
        msg.text.includes('Connecting to agent') ||
        msg.text.includes('Checking availability') ||
        msg.text.includes('Finding slots'))
    ) {
      return false;
    }

    // Don't show redundant "Done." text for function responses
    if (
      msg.functionResponse &&
      (msg.text === 'Done.' ||
        msg.text.includes('Connecting to agent') ||
        msg.text.includes('slots found'))
    ) {
      return false;
    }

    return true;
  }

  // Format time from 24h to 12h format for display
  formatTimeSlot(timeSlot: string): string {
    try {
      // Clean up the time slot (remove any extra spaces)
      const cleanTimeSlot = timeSlot.replace(/\s+/g, '');

      // Format like "18:00-18:30" to "6:00 PM - 6:30 PM"
      return cleanTimeSlot.replace(
        /(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})/g,
        (_, h1, m1, h2, m2) => {
          const hour1 = parseInt(h1, 10);
          const hour2 = parseInt(h2, 10);

          const period1 = hour1 >= 12 ? 'PM' : 'AM';
          const period2 = hour2 >= 12 ? 'PM' : 'AM';

          const h1Formatted = hour1 % 12 || 12;
          const h2Formatted = hour2 % 12 || 12;

          return `${h1Formatted}:${m1} ${period1} - ${h2Formatted}:${m2} ${period2}`;
        }
      );
    } catch (error) {
      console.error('Error formatting time slot:', error);
      return timeSlot; // Return original if there's an error
    }
  }
}
