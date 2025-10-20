from django.core.management.base import BaseCommand
from django.test import Client
from django.contrib.auth.models import User
from invest.models import Business, Campaign, Profile, Investment
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Simulate investor posting to invest endpoint to test redirect to bkash_start'

    def handle(self, *args, **options):
        # cleanup
        User.objects.filter(username='sim_investor').delete()
        User.objects.filter(username='sim_business').delete()

        # create business owner
        bus = User.objects.create_user('sim_business', email='biz@example.com', password='bizpass')
        Profile.objects.update_or_create(user=bus, defaults={'is_business': True})
        business = Business.objects.create(owner=bus, name='SimBiz', description='desc', location='Dhaka')

        # create campaign
        camp = Campaign.objects.create(business=business, title='Sim Campaign', description='desc', target_amount=10000, min_investment=100, start_date=date.today(), end_date=date.today()+timedelta(days=30))

        # create investor
        inv = User.objects.create_user('sim_investor', email='inv@example.com', password='invpass')
        Profile.objects.update_or_create(user=inv, defaults={'is_investor': True})

        c = Client()
        logged = c.login(username='sim_investor', password='invpass')
        self.stdout.write('Logged in: %s' % logged)

        resp = c.post(f'/campaign/{camp.id}/invest/', {'amount': '500'})
        self.stdout.write('POST status: %s' % resp.status_code)
        if resp.status_code in (301,302):
            self.stdout.write('Redirect to: %s' % resp['Location'])
        else:
            self.stdout.write('Response length: %s' % len(resp.content))

        invs = Investment.objects.filter(investor=inv, campaign=camp)
        self.stdout.write('Investments found: %s' % invs.count())
        if invs.exists():
            i = invs.first()
            self.stdout.write('Investment status: %s, transaction_id: %s' % (i.status, i.transaction_id))
            pays = i.payments.all()
            self.stdout.write('Linked payments: %s' % pays.count())
            if pays.exists():
                p = pays.first()
                self.stdout.write('Payment id: %s, status: %s' % (p.id, p.status))
