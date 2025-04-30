import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatRadioModule } from '@angular/material/radio';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatInputModule } from '@angular/material/input';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-qualifier-dialog',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatRadioModule,
    MatFormFieldModule,
    MatInputModule,
    MatButtonModule,
  ],
  templateUrl: './qualifier-dialog.component.html',
  styleUrls: ['./qualifier-dialog.component.scss'],
})
export class QualifierDialogComponent {
  @Input() args: any;
  selectedOption: string = '';
  otherValue: string = '';

  constructor(private dialogRef: MatDialogRef<QualifierDialogComponent>) {}

  submit() {
    const value =
      this.selectedOption === 'Other' ? this.otherValue : this.selectedOption;
    this.dialogRef.close(value);
  }
}
