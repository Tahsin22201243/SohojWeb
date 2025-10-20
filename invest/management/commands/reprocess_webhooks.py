from django.core.management.base import BaseCommand
from invest.models import WebhookEvent, Payment
import json

class Command(BaseCommand):
    help = 'Reprocess unprocessed bKash webhook events (attempt to apply them again)'

    def handle(self, *args, **options):
        events = WebhookEvent.objects.filter(processed=False).order_by('received_at')
        self.stdout.write(f'Found {events.count()} unprocessed webhook events')
        for e in events:
            try:
                payload = e.raw_payload
                payment_id = payload.get('payment_id')
                status = payload.get('status')
                transaction_id = payload.get('transaction_id')
                gateway_event_id = payload.get('gateway_event_id')
                pay = None
                if payment_id:
                    try:
                        pay = Payment.objects.get(id=payment_id)
                    except Payment.DoesNotExist:
                        self.stdout.write(f'Payment {payment_id} not found for event {e.id}')
                        continue
                if not pay:
                    self.stdout.write(f'No payment linked for event {e.id}')
                    continue

                if gateway_event_id and pay.gateway_event_id == gateway_event_id:
                    self.stdout.write(f'Event {e.event_id} already applied to payment {pay.id}')
                    e.processed = True
                    e.save()
                    continue

                if status == 'success':
                    pay.status = 'succeeded'
                    pay.transaction_id = transaction_id or pay.transaction_id
                    pay.gateway_event_id = gateway_event_id or pay.gateway_event_id
                    pay.raw_response = payload
                    pay.save()
                    if pay.investment:
                        inv = pay.investment
                        inv.status = 'approved'
                        inv.transaction_id = transaction_id or inv.transaction_id
                        inv.gateway = 'bkash'
                        inv.gateway_event_id = gateway_event_id or inv.gateway_event_id
                        inv.save()
                else:
                    pay.status = 'failed'
                    pay.raw_response = payload
                    pay.gateway_event_id = gateway_event_id or pay.gateway_event_id
                    pay.save()
                    if pay.investment:
                        pay.investment.status = 'rejected'
                        pay.investment.save()

                e.processed = True
                e.save()
                self.stdout.write(f'Processed event {e.id} for payment {pay.id}')
            except Exception as ex:
                self.stdout.write(f'Error processing event {e.id}: {ex}')