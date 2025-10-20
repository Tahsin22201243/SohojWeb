from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class Profile(models.Model):
    """Extended user profile."""
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    full_name = models.CharField(max_length=150, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.CharField(max_length=255, blank=True)
    is_business = models.BooleanField(default=False)
    is_investor = models.BooleanField(default=False)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(blank=True)
    # KYC / verification fields
    kyc_status = models.CharField(max_length=20, choices=[('pending', 'Pending'), ('approved', 'Approved'), ('rejected', 'Rejected')], default='pending')
    # Type of document uploaded for KYC
    kyc_type = models.CharField(
        max_length=50,
        choices=[
            ('nid', 'National ID / NID card'),
            ('passport', 'Passport'),
            ('driver_license', "Driver's license"),
            ('utility_bill', 'Recent utility bill or bank statement (address proof)'),
        ],
        blank=True,
    )
    kyc_document = models.FileField(upload_to='kyc_docs/', blank=True, null=True)
    bank_account = models.CharField(max_length=100, blank=True)
    # Additional profile fields requested in UI
    birthdate = models.DateField(null=True, blank=True)
    country = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.user.username

class Business(models.Model):
    """Business seeking investment."""
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='businesses')
    name = models.CharField(max_length=100)
    description = models.TextField()
    location = models.CharField(max_length=100)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    # Optionally, add a rejection reason
    rejection_reason = models.TextField(blank=True)

    def __str__(self):
        return self.name

class Campaign(models.Model):
    """Investment campaign for a business."""
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='campaigns')
    title = models.CharField(max_length=150)
    description = models.TextField()
    target_amount = models.DecimalField(max_digits=12, decimal_places=2)
    min_investment = models.DecimalField(max_digits=12, decimal_places=2, default=3000)
    start_date = models.DateField()
    end_date = models.DateField()
    is_funded = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    RISK_CHOICES = [
        ('A', 'A - Low'),
        ('B', 'B - Moderate'),
        ('C', 'C - Medium'),
        ('D', 'D - High'),
        ('E', 'E - Very High'),
    ]
    risk_grade = models.CharField(max_length=1, choices=RISK_CHOICES, default='C')
    # optional cover image for campaign card
    cover_image = models.ImageField(upload_to='campaign_covers/', blank=True, null=True)

    @property
    def raised_amount(self):
        # Count only approved investments for a realistic raised total
        from django.db.models import Sum
        total = self.investments.filter(status='approved').aggregate(total=Sum('amount'))['total']
        return total or 0

    @property
    def percent_raised(self):
        try:
            from decimal import Decimal, InvalidOperation, getcontext
            # Use Decimal for money math
            getcontext().prec = 12
            target = Decimal(self.target_amount)
            raised = Decimal(self.raised_amount)
            if target <= Decimal('0'):
                return Decimal('0')
            percent = (raised / target) * Decimal('100')
            if percent >= Decimal('100'):
                return Decimal('100')
            # quantize to 2 decimal places
            return percent.quantize(Decimal('0.01'))
        except Exception:
            return Decimal('0')

    @property
    def days_left(self):
        from django.utils import timezone
        today = timezone.localdate()
        delta = (self.end_date - today).days
        return max(0, delta)

    def __str__(self):
        return f"{self.title} ({self.business.name})"

class Investment(models.Model):
    """Investment made by a user in a campaign."""
    investor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='investments')
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='investments')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    invested_at = models.DateTimeField(auto_now_add=True)
    # More detailed status field (keeps is_approved for backward compatibility)
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('returned', 'Returned'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    is_approved = models.BooleanField(default=False)
    transaction_id = models.CharField(max_length=200, blank=True)
    payment_method = models.CharField(max_length=100, blank=True)
    receipt_file = models.FileField(upload_to='receipts/', blank=True, null=True)
    # optional gateway/event tracking
    gateway = models.CharField(max_length=50, blank=True)
    gateway_event_id = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.investor.username} - {self.campaign.title} - {self.amount}"


class Payment(models.Model):
    GATEWAY_CHOICES = [
        ('bkash', 'bKash'),
    ]
    investment = models.ForeignKey(Investment, on_delete=models.CASCADE, related_name='payments', null=True, blank=True)
    gateway = models.CharField(max_length=50, choices=GATEWAY_CHOICES, default='bkash')
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default='BDT')
    transaction_id = models.CharField(max_length=200, blank=True)
    gateway_event_id = models.CharField(max_length=200, blank=True)
    status = models.CharField(max_length=20, default='pending')
    raw_response = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment {self.id} - {self.gateway} - {self.amount} ({self.status})"


class WebhookEvent(models.Model):
    """Store raw webhook events for auditing and idempotency."""
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, related_name='webhook_events')
    gateway = models.CharField(max_length=50, blank=True)
    event_id = models.CharField(max_length=200, blank=True, db_index=True)
    raw_payload = models.JSONField()
    signature = models.CharField(max_length=500, blank=True)
    processed = models.BooleanField(default=False, db_index=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    received_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [models.Index(fields=['gateway', 'event_id'])]

    def __str__(self):
        return f"Webhook {self.gateway} {self.event_id} ({self.received_at})"

class Update(models.Model):
    """Updates posted by businesses for their campaigns."""
    campaign = models.ForeignKey(Campaign, on_delete=models.CASCADE, related_name='updates')
    title = models.CharField(max_length=150)
    content = models.TextField()
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updates_created')
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='updates_approved')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Update: {self.title} ({self.campaign.title})"


class UpdateAttachment(models.Model):
    update = models.ForeignKey(Update, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='update_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Attachment for {self.update.id}: {self.file.name}"


class UpdateAudit(models.Model):
    ACTION_CHOICES = [
        ('create', 'Create'),
        ('edit', 'Edit'),
        ('delete', 'Delete'),
    ]
    update = models.ForeignKey(Update, on_delete=models.CASCADE, related_name='audits')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    before_title = models.CharField(max_length=150, blank=True)
    before_content = models.TextField(blank=True)

    def __str__(self):
        return f"{self.get_action_display()} by {self.user} on {self.timestamp}"

class ContactMessage(models.Model):
    """Contact form submissions."""
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=150)
    message = models.TextField()
    sent_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.subject}"


# Automatically toggle Campaign.is_funded when investments are approved/changed
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver


@receiver(post_save, sender=Investment)
def update_campaign_funded_on_investment_save(sender, instance, **kwargs):
    try:
        campaign = instance.campaign
        # One-way funded behavior: if percent >= 100, mark funded. Do NOT unset once funded.
        from decimal import Decimal
        try:
            pct = Decimal(campaign.percent_raised)
        except Exception:
            pct = Decimal('0')
        if pct >= Decimal('100') and not campaign.is_funded:
            campaign.is_funded = True
            campaign.save(update_fields=['is_funded'])
    except Exception:
        # avoid raising in signal handler
        pass


@receiver(post_delete, sender=Investment)
def update_campaign_funded_on_investment_delete(sender, instance, **kwargs):
    try:
        campaign = instance.campaign
        # On deletion, if campaign reached funding we can set it; do NOT unset once funded.
        from decimal import Decimal
        try:
            pct = Decimal(campaign.percent_raised)
        except Exception:
            pct = Decimal('0')
        if pct >= Decimal('100') and not campaign.is_funded:
            campaign.is_funded = True
            campaign.save(update_fields=['is_funded'])
    except Exception:
        pass
