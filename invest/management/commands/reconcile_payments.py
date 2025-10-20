from django.core.management.base import BaseCommand
from invest.models import Payment

class Command(BaseCommand):
    help = 'Simulated reconciliation: mark payments with transaction_id in raw_response as succeeded'

    def handle(self, *args, **options):
        pending = Payment.objects.filter(status='pending')
        count = 0
        for p in pending:
            data = p.raw_response or {}
            # simulate: if raw_response has status=success, mark succeeded
            if isinstance(data, dict) and data.get('status') == 'success':
                p.status = 'succeeded'
                p.transaction_id = data.get('transaction_id', p.transaction_id)
                p.save()
                if p.investment:
                    p.investment.status = 'approved'
                    p.investment.save()
                count += 1
        self.stdout.write(self.style.SUCCESS(f'Reconciled {count} payments'))
