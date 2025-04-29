import { Component } from '@angular/core';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatButtonModule } from '@angular/material/button';
@Component({
  selector: 'app-landing-page',
  templateUrl: './landing-page.component.html',
  standalone: true,
  styles: ``,
  imports: [MatProgressSpinnerModule, MatButtonModule],
})
export class LandingPageComponent {}
