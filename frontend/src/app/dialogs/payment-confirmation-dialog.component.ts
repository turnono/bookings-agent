import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-payment-confirmation-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule],
  templateUrl: './payment-confirmation-dialog.component.html',
  styleUrls: ['./payment-confirmation-dialog.component.scss'],
})
export class PaymentConfirmationDialogComponent {
  @Input() args: any;

  constructor(
    private dialogRef: MatDialogRef<PaymentConfirmationDialogComponent>
  ) {}

  pay() {
    this.dialogRef.close(this.args?.amount);
  }
}
