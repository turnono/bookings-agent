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
import { PaymentConfirmationDialogComponent } from '../dialogs/payment-confirmation-dialog.component';
import { MatSnackBar } from '@angular/material/snack-bar';

import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';

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
  create_paystack_checkout: 'Preparing payment…',
  screening_question: 'Just a quick question…',
  // Add more mappings as needed
};

const FUNCTION_DIALOG_MAP: Record<string, any> = {
  qualifyUser: QualifierDialogComponent,
  selectService: ServiceSelectionDialogComponent,
  getAvailableDates: DatePickerDialogComponent,
  getAvailableSlots: SlotPickerDialogComponent,
  confirmPayment: PaymentConfirmationDialogComponent,
  transfer_to_agent: QualifierDialogComponent,
  get_available_time_slots: SlotPickerDialogComponent,
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
  paymentUrl: string = '';

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
    private snackBar: MatSnackBar
  ) {}

  ngOnInit() {
    this.agentService.getUserId$().subscribe({
      next: (uid) => {
        this.firebaseUserId = uid;
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
    this.snackBar
      .open(message + ' (tap to retry)', 'Retry', { duration: 5000 })
      .onAction()
      .subscribe(() => {
        // Retry logic placeholder
        // this.retryLastAction?.();
      });
    this.loading = false;
    this.focusInput();
  }

  dismissError() {
    this.errorMessage = '';
  }

  sendMessage() {
    if (!this.firebaseUserId) {
      this.handleError('Firebase UID not ready yet.');
      return;
    }
    const input = this.userInput.trim();
    if (!input) return;
    this.messages.push({
      role: 'user',
      text: input,
      timestamp: Timestamp.now(),
    });
    this.userInput = '';
    this.loading = true;
    this.scrollToBottom();
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
          this.focusInput();
        },
        error: (err: any) => {
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
          this.scrollToBottom();
        },
      });
  }

  handleAgentEvents(events: any) {
    let messageAdded = false;

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
    this.paymentUrl = '';

    // Open the mapped dialog for this function call, only if mapped
    const dialogComponent = FUNCTION_DIALOG_MAP[func.name];
    if (dialogComponent) {
      const dialogRef = this.dialog.open(dialogComponent, {
        data: {
          functionName: func.name,
          arguments: func.arguments,
        },
      });
      dialogRef.afterClosed().subscribe((result) => {
        this.scrollToBottom();
        if (result !== undefined && result !== null && result !== '') {
          this.messages.push({
            role: 'user',
            text: result,
            timestamp: Timestamp.now(),
          });
          this.scrollToBottom();
          this.loading = true;
          this.agentService
            .sendMessage(
              result,
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            )
            .subscribe({
              next: (events) => {
                this.handleAgentEvents(events);
                this.scrollToBottom();
                this.focusInput();
              },
              error: (err: any) => {
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
                this.scrollToBottom();
              },
            });
        } else {
          this.messages.push({
            role: 'user',
            text: 'cancel',
            timestamp: Timestamp.now(),
          });
          this.scrollToBottom();
          this.loading = true;
          this.agentService
            .sendMessage(
              'cancel',
              this.agentService.appName,
              this.firebaseUserId!,
              this.agentService.sessionId
            )
            .subscribe({
              next: (events) => {
                this.handleAgentEvents(events);
                this.scrollToBottom();
                this.focusInput();
              },
              error: (err: any) => {
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
                this.scrollToBottom();
              },
            });
        }
      });
    }

    // Screening question
    if (func.name === 'screening_question') {
      // args: { question: string }
      // Show input for answer
    } else if (func.name === 'availability_agent.getSlots') {
      // Extract validDates from arguments
      this.availableDates = func.arguments?.validDates || [];
    } else if (func.name === 'select_time_slot') {
      // Extract slots from arguments
      this.availableSlots = func.arguments?.slots || [];
    } else if (func.name === 'create_paystack_checkout') {
      // Extract url from arguments
      this.paymentUrl = func.arguments?.url || '';
    }
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
    if (funcResp.name === 'availability_agent.getSlots') {
      if (funcResp.response?.slots) {
        this.availableSlots = funcResp.response.slots;
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
          this.focusInput();
        },
        error: (err: any) => {
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
          this.scrollToBottom();
        },
      });
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
          this.focusInput();
        },
        error: (err: any) => {
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
          this.scrollToBottom();
        },
      });
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
          this.focusInput();
        },
        error: (err: any) => {
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
          this.scrollToBottom();
        },
      });
    this.activeFunctionCall = null;
    this.selectedSlot = '';
  }

  goToPayment() {
    if (this.paymentUrl) {
      window.location.href = this.paymentUrl;
    }
  }

  newChat() {
    if (!this.firebaseUserId) {
      this.handleError('Firebase UID not ready yet.');
      return;
    }
    this.agentService.startNewSession();
    this.messages = [
      {
        role: 'agent',
        text: 'Hello! I’m SchedulerAgent, the booking assistant for Abdullah Abrahams. How can I help you today?',
        timestamp: Timestamp.now(),
      },
    ];
    this.userInput = '';
    this.loading = false;
    this.agentService
      .createOrUpdateSession(
        this.agentService.appName,
        this.firebaseUserId!,
        this.agentService.sessionId,
        {}
      )
      .pipe(takeUntil(this.destroy$))
      .subscribe({
        next: () => {
          console.log('Session created successfully');
          // Ensure greeting is visible by scrolling after a short delay
          setTimeout(() => {
            this.scrollToBottom();
            this.focusInput();
          }, 100);
        },
        error: (err: any) => {
          console.error('AgentService error:', err);
          let errorMsg = 'Error creating session.';
          if (err?.error?.message) {
            errorMsg += ` Details: ${err.error.message}`;
          } else if (err?.message) {
            errorMsg += ` Details: ${err.message}`;
          } else if (typeof err === 'string') {
            errorMsg += ` Details: ${err}`;
          }
          this.handleError(errorMsg);
        },
      });
  }

  ngOnDestroy() {
    // Cleanup the observer
    if (this.mutationObserver) {
      this.mutationObserver.disconnect();
      this.mutationObserver = null;
    }
    this.destroy$.next();
    this.destroy$.complete();
  }
}
