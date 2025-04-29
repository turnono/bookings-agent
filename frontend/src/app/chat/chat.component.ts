import {
  Component,
  OnInit,
  ViewChild,
  ElementRef,
  AfterViewInit,
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

import {
  trigger,
  state,
  style,
  animate,
  transition,
} from '@angular/animations';

interface ChatMessage {
  role: 'user' | 'agent' | 'system';
  text: string;
  event?: string;
  functionCall?: any;
  functionResponse?: any;
  timestamp?: Timestamp;
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
export class ChatComponent implements OnInit, AfterViewInit {
  messages: ChatMessage[] = [
    { role: 'system', text: 'Welcome! Start chatting with your agent.' },
  ];
  userInput: string = '';
  loading = false;
  errorMessage: string = '';

  // Interactive controls state
  activeFunctionCall: any = null;
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

  constructor(private agentService: AgentService) {}

  ngOnInit() {
    this.newChat();
  }

  ngAfterViewInit() {
    this.scrollToBottom();
  }

  scrollToBottom() {
    setTimeout(() => {
      if (this.messageListRef) {
        this.messageListRef.nativeElement.scrollTop =
          this.messageListRef.nativeElement.scrollHeight;
      }
    }, 0);
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
    if (!this.messages.some((m) => m.role === 'system' && m.text === message)) {
      this.messages.push({
        role: 'system',
        text: message,
        timestamp: Timestamp.now(),
      });
    }
    this.loading = false;
    this.focusInput();
  }

  dismissError() {
    this.errorMessage = '';
  }

  sendMessage() {
    const input = this.userInput.trim();
    if (!input) return;
    this.messages.push({
      role: 'user',
      text: input,
      timestamp: Timestamp.now(),
    });
    this.userInput = '';
    this.loading = true;
    this.agentService.sendMessage(input).subscribe({
      next: (events) => {
        this.handleAgentEvents(events);
        this.scrollToBottom();
        this.focusInput();
      },
      error: () => {
        this.handleError('Error contacting agent.');
      },
    });
  }

  handleAgentEvents(events: any) {
    for (const event of events) {
      if (event.content && event.content.parts) {
        for (const part of event.content.parts) {
          // Internal logic: handle function calls and responses for UI triggers
          if (part.functionCall) {
            this.activeFunctionCall = part.functionCall;
            this.handleFunctionCall(part.functionCall);
          } else if (part.functionResponse) {
            this.activeFunctionCall = null;
            this.handleFunctionResponse(part.functionResponse);
          }
          // User-facing: only show text
          if (part.text) {
            this.messages.push({
              role: 'agent',
              text: part.text,
              timestamp: Timestamp.now(),
            });
          }
        }
      }
    }
    this.loading = false;
    this.scrollToBottom();
    this.focusInput();
  }

  handleFunctionCall(func: any) {
    // Reset all controls
    this.screeningAnswer = '';
    this.selectedDate = null;
    this.availableDates = [];
    this.availableSlots = [];
    this.selectedSlot = '';
    this.paymentUrl = '';
    // Screening question
    if (func.name === 'screening_question') {
      // args: { question: string }
      // Show input for answer
    } else if (func.name === 'availability_agent.getSlots') {
      // args: { validDates: string[] }
      this.availableDates = func.args?.validDates || [];
    } else if (func.name === 'select_time_slot') {
      // args: { slots: string[] }
      this.availableSlots = func.args?.slots || [];
    } else if (func.name === 'create_paystack_checkout') {
      // args: { url: string }
      this.paymentUrl = func.args?.url || '';
    }
  }

  handleFunctionResponse(funcResp: any) {
    // Optionally handle function response if needed
    if (funcResp.name === 'availability_agent.getSlots') {
      // If response contains slots, update availableSlots
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
    this.agentService.sendMessage(this.screeningAnswer).subscribe({
      next: (events) => {
        this.handleAgentEvents(events);
        this.scrollToBottom();
        this.focusInput();
      },
      error: () => {
        this.handleError('Error contacting agent.');
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
    this.agentService.sendMessage(dateStr).subscribe({
      next: (events) => {
        this.handleAgentEvents(events);
        this.scrollToBottom();
        this.focusInput();
      },
      error: () => {
        this.handleError('Error contacting agent.');
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
    this.agentService.sendMessage(slot).subscribe({
      next: (events) => {
        this.handleAgentEvents(events);
        this.scrollToBottom();
        this.focusInput();
      },
      error: () => {
        this.handleError('Error contacting agent.');
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
    this.agentService.startNewSession();
    this.messages = [
      { role: 'system', text: 'Welcome! Start chatting with your agent.' },
    ];
    this.userInput = '';
    this.loading = false;
    this.agentService.createSession().subscribe({
      next: () => {
        console.log('Session created successfully');
        this.scrollToBottom();
        this.focusInput();
      },
      error: () => {
        this.handleError('Error creating session.');
      },
    });
  }
}
