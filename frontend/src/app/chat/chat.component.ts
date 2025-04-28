import { Component, OnInit } from '@angular/core';
import { AgentService } from '../agent.service';
import { ReactiveFormsModule, FormsModule } from '@angular/forms';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';

interface ChatMessage {
  role: 'user' | 'agent' | 'system';
  text: string;
  event?: string;
}

@Component({
  selector: 'app-chat',
  templateUrl: './chat.component.html',
  standalone: true,
  imports: [ReactiveFormsModule, CommonModule, FormsModule, HttpClientModule],
  styleUrls: ['./chat.component.scss'],
})
export class ChatComponent implements OnInit {
  messages: ChatMessage[] = [
    { role: 'system', text: 'Welcome! Start chatting with your agent.' },
  ];
  userInput: string = '';
  loading = false;

  constructor(private agentService: AgentService) {}

  ngOnInit() {}

  sendMessage() {
    const input = this.userInput.trim();
    if (!input) return;
    this.messages.push({ role: 'user', text: input });
    this.userInput = '';
    this.loading = true;
    this.agentService.sendMessage(input).subscribe({
      next: (events) => {
        for (const event of events) {
          if (event.content && event.content.parts) {
            for (const part of event.content.parts) {
              if (part.functionCall) {
                this.messages.push({
                  role: 'system',
                  text: `Function call: ${part.functionCall.name}`,
                  event: JSON.stringify(part.functionCall.args),
                });
              } else if (part.functionResponse) {
                this.messages.push({
                  role: 'system',
                  text: `Function response: ${part.functionResponse.name}`,
                  event: JSON.stringify(part.functionResponse.response),
                });
              } else if (part.text) {
                this.messages.push({ role: 'agent', text: part.text });
              }
            }
          }
        }
        this.loading = false;
      },
      error: (err) => {
        this.messages.push({ role: 'system', text: 'Error contacting agent.' });
        this.loading = false;
      },
    });
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
      },
      error: (err) => {
        if (
          err?.error?.detail &&
          err.error.detail.includes('Session already exists')
        ) {
          // Session already exists, proceed
        } else {
          this.messages.push({
            role: 'system',
            text: 'Error creating session.',
          });
        }
      },
    });
  }
}
