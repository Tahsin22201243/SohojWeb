import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'SohojBiniyog.settings')
import django
django.setup()
from django.test import Client
from django.contrib.auth.models import User
from invest.models import Business, Campaign, Profile

# cleanup users if exist
User.objects.filter(username='test_investor').delete()
User.objects.filter(username='test_business').delete()

# create business owner
business_user = User.objects.create_user('test_business', email='biz@example.com', password='bizpass')
Profile.objects.update_or_create(user=business_user, defaults={'is_business': True})

# create campaign
business = Business.objects.create(owner=business_user, name='TestBiz', description='desc', location='Dhaka')
from datetime import date, timedelta
camp = Campaign.objects.create(business=business, title='Test Campaign', description='desc', target_amount=10000, min_investment=100, start_date=date.today(), end_date=date.today()+timedelta(days=30))

# create investor
investor = User.objects.create_user('test_investor', email='inv@example.com', password='invpass')
Profile.objects.update_or_create(user=investor, defaults={'is_investor': True})

c = Client()
logged_in = c.login(username='test_investor', password='invpass')
print('Logged in:', logged_in)

url = f'/campaign/{camp.id}/invest/'
resp = c.post(url, {'amount': '500'})
print('POST', url, '-> status', resp.status_code)
# If redirect, print redirect url
if resp.status_code in (301,302):
    print('Redirect to:', resp['Location'])
else:
    # print content for debugging
    print('Response content snippet:', resp.content[:500])

# Check payment and investment created
from invest.models import Investment, Payment
inv_qs = Investment.objects.filter(investor=investor, campaign=camp)
print('Investments found:', inv_qs.count())
if inv_qs.exists():
    inv = inv_qs.first()
    print('Investment status:', inv.status, 'transaction_id:', inv.transaction_id)
    payments = inv.payments.all()
    print('Linked payments:', payments.count())
    if payments.exists():
        print('Payment id:', payments.first().id, 'status:', payments.first().status)
else:
    print('No investment created')
