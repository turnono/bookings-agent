import { Component, Input } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatButtonToggleModule } from '@angular/material/button-toggle';
import { MatButtonModule } from '@angular/material/button';
import { MatDialogRef } from '@angular/material/dialog';

@Component({
  selector: 'app-service-selection-dialog',
  standalone: true,
  imports: [CommonModule, FormsModule, MatButtonToggleModule, MatButtonModule],
  templateUrl: './service-selection-dialog.component.html',
  styleUrls: ['./service-selection-dialog.component.scss'],
})
export class ServiceSelectionDialogComponent {
  @Input() args: any;
  selectedService: string = '';

  constructor(
    private dialogRef: MatDialogRef<ServiceSelectionDialogComponent>
  ) {}

  submit() {
    this.dialogRef.close(this.selectedService);
  }
}
