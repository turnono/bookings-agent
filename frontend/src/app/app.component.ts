import { Component } from '@angular/core';
import { ChatComponent } from './chat/chat.component';
import { RouterOutlet } from '@angular/router';
import { ReactiveFormsModule } from '@angular/forms';
import { AgentService } from './agent.service';
@Component({
  selector: 'app-root',
  standalone: true,
  imports: [ChatComponent, RouterOutlet, ReactiveFormsModule],
  providers: [AgentService],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  title = 'frontend';
}
