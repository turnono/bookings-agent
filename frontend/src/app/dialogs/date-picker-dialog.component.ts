import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-date-picker-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatInputModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatButtonModule,
  ],
  templateUrl: './date-picker-dialog.component.html',
  styleUrls: ['./date-picker-dialog.component.scss'],
})
export class DatePickerDialogComponent {
  @Input() args: any;
  selectedDate: Date | null = null;

  constructor(private dialogRef: MatDialogRef<DatePickerDialogComponent>) {}

  dateFilter = (date: Date | null): boolean => {
    if (!date) return false;
    const dateStr = date.toISOString().split('T')[0];
    return this.args?.dates?.includes(dateStr);
  };

  submit() {
    this.dialogRef.close(this.selectedDate);
  }
}
