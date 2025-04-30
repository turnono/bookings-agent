import { Component, Inject, Input } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material/dialog';
import { QualifierDialogComponent } from './qualifier-dialog.component';
import { ServiceSelectionDialogComponent } from './service-selection-dialog.component';
import { DatePickerDialogComponent } from './date-picker-dialog.component';
import { SlotPickerDialogComponent } from './slot-picker-dialog.component';
import { PaymentConfirmationDialogComponent } from './payment-confirmation-dialog.component';
import { CommonModule } from '@angular/common';

@Component({
  selector: 'app-generic-function-dialog',
  standalone: true,
  imports: [
    CommonModule,
    QualifierDialogComponent,
    ServiceSelectionDialogComponent,
    DatePickerDialogComponent,
    SlotPickerDialogComponent,
    PaymentConfirmationDialogComponent,
  ],
  templateUrl: './generic-function-dialog.component.html',
  styleUrls: ['./generic-function-dialog.component.scss'],
})
export class GenericFunctionDialogComponent {
  @Input() functionName!: string;
  @Input() arguments: any;

  constructor(
    public dialogRef: MatDialogRef<GenericFunctionDialogComponent>,
    @Inject(MAT_DIALOG_DATA)
    public data: { functionName: string; arguments: any }
  ) {
    this.functionName = data.functionName;
    this.arguments = data.arguments;
  }
}
