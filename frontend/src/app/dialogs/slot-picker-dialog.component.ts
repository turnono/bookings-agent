import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatChipsModule } from '@angular/material/chips';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-slot-picker-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatChipsModule, MatButtonModule],
  templateUrl: './slot-picker-dialog.component.html',
  styleUrls: ['./slot-picker-dialog.component.scss'],
})
export class SlotPickerDialogComponent {
  @Input() args: any;
  selectedSlot: string = '';

  constructor(private dialogRef: MatDialogRef<SlotPickerDialogComponent>) {}

  submit() {
    this.dialogRef.close(this.selectedSlot);
  }
}
