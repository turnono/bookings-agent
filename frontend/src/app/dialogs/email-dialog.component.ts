import { Component, Inject } from '@angular/core';
import {
  FormBuilder,
  FormControl,
  FormGroup,
  Validators,
  ReactiveFormsModule,
} from '@angular/forms';
import {
  MAT_DIALOG_DATA,
  MatDialogRef,
  MatDialogModule,
} from '@angular/material/dialog';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { CommonModule } from '@angular/common';

// RFC 5322-lite regex pattern for validating email addresses
const EMAIL_REGEX =
  /^(?:[a-z0-9!#$%&'*+/=?^_`{|}~-]+(?:\.[a-z0-9!#$%&'*+/=?^_`{|}~-]+)*|"(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21\x23-\x5b\x5d-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])*")@(?:(?:[a-z0-9](?:[a-z0-9-]*[a-z0-9])?\.)+[a-z0-9](?:[a-z0-9-]*[a-z0-9])?|\[(?:(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9]))\.){3}(?:(2(5[0-5]|[0-4][0-9])|1[0-9][0-9]|[1-9]?[0-9])|[a-z0-9-]*[a-z0-9]:(?:[\x01-\x08\x0b\x0c\x0e-\x1f\x21-\x5a\x53-\x7f]|\\[\x01-\x09\x0b\x0c\x0e-\x7f])+)\])$/i;

@Component({
  selector: 'app-email-dialog',
  standalone: true,
  imports: [
    CommonModule,
    ReactiveFormsModule,
    MatDialogModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  template: `
    <h2 mat-dialog-title>{{ data.title || 'Confirm your email' }}</h2>
    <div mat-dialog-content>
      <p>
        {{ data.message || 'Please enter your email address to continue.' }}
      </p>
      <form [formGroup]="emailForm">
        <mat-form-field appearance="outline" class="full-width">
          <mat-label>Email</mat-label>
          <input
            matInput
            type="email"
            formControlName="email"
            placeholder="your.email@example.com"
            required
          />
          <mat-error *ngIf="emailForm.get('email')?.hasError('required')">
            Email is required
          </mat-error>
          <mat-error *ngIf="emailForm.get('email')?.hasError('pattern')">
            Please enter a valid email address
          </mat-error>
        </mat-form-field>
      </form>
    </div>
    <div mat-dialog-actions align="end">
      <button mat-button mat-dialog-close>Cancel</button>
      <button
        mat-raised-button
        color="primary"
        [disabled]="!emailForm.valid"
        (click)="submit()"
      >
        Continue
      </button>
    </div>
  `,
  styles: [
    `
      .full-width {
        width: 100%;
      }
      mat-form-field {
        margin-bottom: 16px;
      }
    `,
  ],
})
export class EmailDialogComponent {
  emailForm: FormGroup;

  constructor(
    private fb: FormBuilder,
    public dialogRef: MatDialogRef<EmailDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    this.emailForm = this.fb.group({
      email: ['', [Validators.required, Validators.pattern(EMAIL_REGEX)]],
    });
  }

  submit(): void {
    if (this.emailForm.valid) {
      this.dialogRef.close(this.emailForm.value.email);
    }
  }
}
