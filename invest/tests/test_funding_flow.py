from django.test import TestCase, Client
from django.contrib.auth.models import User
from invest.models import Business, Campaign, Investment
from django.urls import reverse
from django.utils import timezone


class FundingFlowTest(TestCase):
    def setUp(self):
        # create a business owner and business
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.business = Business.objects.create(owner=self.owner, name='B', description='d', location='L')
        # create a campaign with small target
        today = timezone.localdate()
        self.campaign = Campaign.objects.create(business=self.business, title='C', description='D', target_amount=5000, min_investment=3000, start_date=today, end_date=today)
        # create investor
        self.investor = User.objects.create_user(username='inv', password='pass')
        self.client = Client()

    def test_approve_investment_marks_funded_and_blocks(self):
        # login investor and post a pending investment for the full amount
        self.client.login(username='inv', password='pass')
        url = reverse('invest_in_campaign', args=[self.campaign.id])
        resp = self.client.post(url, {'amount': '5000'})
        # create investment expected
        inv = Investment.objects.filter(investor=self.investor, campaign=self.campaign).first()
        self.assertIsNotNone(inv)
        # mark approved
        inv.status = 'approved'
        inv.save()
        # campaign should now be marked funded by signal
        self.campaign.refresh_from_db()
        self.assertTrue(self.campaign.is_funded)
        # further attempts to invest should be redirected/blocked
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, 302)  # redirect to campaign_detail
