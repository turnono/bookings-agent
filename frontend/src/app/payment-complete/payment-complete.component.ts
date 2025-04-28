import { Component, OnInit } from '@angular/core';
import { ActivatedRoute } from '@angular/router';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-payment-complete',
  standalone: true,
  templateUrl: './payment-complete.component.html',
  imports: [],
})
export class PaymentCompleteComponent implements OnInit {
  status: 'pending' | 'success' | 'failed' = 'pending';
  message = 'Verifying your payment...';

  constructor(private route: ActivatedRoute, private http: HttpClient) {}

  ngOnInit() {
    this.route.queryParams.subscribe((params) => {
      const reference = params['reference'];
      if (reference) {
        this.http
          .get<any>(`/api/payment-status?reference=${reference}`)
          .subscribe({
            next: (resp) => {
              if (resp.payment_status === 'success') {
                this.status = 'success';
                this.message =
                  'Your payment was successful and your booking is confirmed!';
              } else {
                this.status = 'failed';
                this.message =
                  'Payment failed or could not be confirmed. Please contact support.';
              }
            },
            error: () => {
              this.status = 'failed';
              this.message = 'Error verifying payment. Please contact support.';
            },
          });
      } else {
        this.status = 'failed';
        this.message = 'No payment reference found in the URL.';
      }
    });
  }
}
