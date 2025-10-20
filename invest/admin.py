from django.contrib import admin
from django.core.mail import send_mail
from django.urls import reverse
from django.utils.html import format_html
from .models import Business, Profile
from .models import Update, UpdateAttachment, UpdateAudit, Payment, Investment
from .models import WebhookEvent
from .models import Campaign


@admin.register(Business)
class BusinessAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'is_approved', 'is_rejected', 'created_at')
    list_filter = ('is_approved', 'is_rejected')
    actions = ['approve_business', 'reject_business']

    def approve_business(self, request, queryset):
        queryset.update(is_approved=True, is_rejected=False)
    approve_business.short_description = "Approve selected businesses"

    def reject_business(self, request, queryset):
        queryset.update(is_approved=False, is_rejected=True)
    reject_business.short_description = "Reject selected businesses"


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'is_business', 'is_investor', 'kyc_status', 'kyc_type', 'kyc_download')
    list_filter = ('kyc_status', 'kyc_type')
    actions = ['approve_kyc', 'reject_kyc']

    def approve_kyc(self, request, queryset):
        for profile in queryset:
            profile.kyc_status = 'approved'
            profile.save()
            # send email notification
            if profile.user.email:
                send_mail(
                    'KYC Approved',
                    'Hello {},\n\nYour KYC document has been approved. You can now access full features.'.format(profile.full_name or profile.user.username),
                    None,
                    [profile.user.email],
                    fail_silently=True,
                )
    approve_kyc.short_description = "Approve selected KYC"

    def reject_kyc(self, request, queryset):
        for profile in queryset:
            profile.kyc_status = 'rejected'
            profile.save()
            if profile.user.email:
                send_mail(
                    'KYC Rejected',
                    'Hello {},\n\nYour KYC document has been rejected. Please re-upload a valid document.'.format(profile.full_name or profile.user.username),
                    None,
                    [profile.user.email],
                    fail_silently=True,
                )
    reject_kyc.short_description = "Reject selected KYC"

    def kyc_download(self, obj):
        if obj.kyc_document:
            url = reverse('download_kyc', args=[obj.user.id])
            return format_html('<a href="{}">Download</a>', url)
        return '-'
    kyc_download.short_description = 'KYC Document'


@admin.register(Update)
class UpdateAdmin(admin.ModelAdmin):
    list_display = ('title', 'campaign', 'created_by', 'is_approved', 'created_at')
    list_filter = ('is_approved', 'campaign')
    actions = ['approve_updates', 'reject_updates']

    def approve_updates(self, request, queryset):
        for upd in queryset:
            upd.is_approved = True
            upd.approved_by = request.user
            from django.utils import timezone
            upd.approved_at = timezone.now()
            upd.save()
    approve_updates.short_description = 'Approve selected updates'

    def reject_updates(self, request, queryset):
        queryset.update(is_approved=False)
    reject_updates.short_description = 'Reject selected updates'


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display = ('title', 'business', 'risk_grade', 'percent_raised_display', 'days_left', 'is_funded', 'created_at')
    list_filter = ('risk_grade', 'is_funded', 'business')
    search_fields = ('title', 'business__name')
    actions = ['set_risk_a', 'set_risk_b', 'set_risk_c', 'set_risk_d', 'set_risk_e']
    fieldsets = (
        (None, {
            'fields': ('business', 'title', 'description', 'cover_image')
        }),
        ('Funding', {'fields': ('target_amount', 'min_investment', 'start_date', 'end_date', 'is_funded')}),
        ('Risk', {'fields': ('risk_grade',), 'description': 'Risk grading is a high-level indicator: A (Low) -> E (Very High). Use investor profile and business metrics to determine grade.'}),
    )

    def percent_raised_display(self, obj):
        try:
            return f"{obj.percent_raised:.1f}%"
        except Exception:
            return "0%"
    percent_raised_display.short_description = 'Percent Raised'

    def set_risk(self, request, queryset, grade):
        queryset.update(risk_grade=grade)

    def set_risk_a(self, request, queryset):
        return self.set_risk(request, queryset, 'A')
    set_risk_a.short_description = 'Set risk grade to A (Low)'

    def set_risk_b(self, request, queryset):
        return self.set_risk(request, queryset, 'B')
    set_risk_b.short_description = 'Set risk grade to B (Moderate)'

    def set_risk_c(self, request, queryset):
        return self.set_risk(request, queryset, 'C')
    set_risk_c.short_description = 'Set risk grade to C (Medium)'

    def set_risk_d(self, request, queryset):
        return self.set_risk(request, queryset, 'D')
    set_risk_d.short_description = 'Set risk grade to D (High)'

    def set_risk_e(self, request, queryset):
        return self.set_risk(request, queryset, 'E')
    set_risk_e.short_description = 'Set risk grade to E (Very High)'


@admin.register(UpdateAttachment)
class UpdateAttachmentAdmin(admin.ModelAdmin):
    list_display = ('update', 'file', 'uploaded_at')


@admin.register(UpdateAudit)
class UpdateAuditAdmin(admin.ModelAdmin):
    list_display = ('update', 'action', 'user', 'timestamp')


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('id', 'investment', 'gateway', 'amount', 'currency', 'status', 'transaction_id', 'created_at')
    list_filter = ('status', 'gateway')
    actions = ['approve_payments', 'reject_payments']

    def approve_payments(self, request, queryset):
        for pay in queryset:
            pay.status = 'succeeded'
            # prefer transaction_id from raw_response if available
            if not pay.transaction_id and isinstance(pay.raw_response, dict):
                pay.transaction_id = pay.raw_response.get('transaction_id', pay.transaction_id)
            pay.save()
            inv = pay.investment
            if inv:
                inv.status = 'approved'
                inv.transaction_id = pay.transaction_id or ''
                inv.gateway = pay.gateway
                inv.gateway_event_id = pay.gateway_event_id or ''
                inv.save()
                # notify investor
                if inv.investor.email:
                    send_mail('Investment approved', f'Your investment of {inv.amount} has been approved.', None, [inv.investor.email], fail_silently=True)
    approve_payments.short_description = 'Mark selected payments as approved and update investments'

    def reject_payments(self, request, queryset):
        for pay in queryset:
            pay.status = 'failed'
            pay.save()
            inv = pay.investment
            if inv:
                inv.status = 'rejected'
                inv.save()
                if inv.investor.email:
                    send_mail('Investment rejected', f'Your investment of {inv.amount} was rejected. Please contact support.', None, [inv.investor.email], fail_silently=True)
    reject_payments.short_description = 'Mark selected payments as rejected and update investments'

    # add a small admin page for pending payments and single-item approve/reject
    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        custom = [
            path('pending/', self.admin_site.admin_view(self.pending_view), name='invest_payment_pending'),
            path('<int:payment_id>/approve/', self.admin_site.admin_view(self.approve_single), name='invest_payment_approve'),
            path('<int:payment_id>/reject/', self.admin_site.admin_view(self.reject_single), name='invest_payment_reject'),
        ]
        return custom + urls

    def pending_view(self, request):
        from django.shortcuts import render, redirect
        qs = Payment.objects.filter(status='pending').order_by('-created_at')
        return render(request, 'admin/payments_pending.html', {'payments': qs, 'opts': self.model._meta})

    def approve_single(self, request, payment_id):
        from django.shortcuts import redirect, get_object_or_404
        pay = get_object_or_404(Payment, id=payment_id)
        pay.status = 'succeeded'
        pay.save()
        if pay.investment:
            inv = pay.investment
            inv.status = 'approved'
            inv.transaction_id = pay.transaction_id or ''
            inv.save()
            if inv.investor.email:
                from django.template.loader import render_to_string
                html = render_to_string('emails/payment_approved.html', {'investment': inv, 'payment': pay})
                send_mail('Investment approved', 'Your investment was approved.', None, [inv.investor.email], html_message=html, fail_silently=True)
        return redirect('..')

    def reject_single(self, request, payment_id):
        from django.shortcuts import redirect, get_object_or_404
        pay = get_object_or_404(Payment, id=payment_id)
        pay.status = 'failed'
        pay.save()
        if pay.investment:
            inv = pay.investment
            inv.status = 'rejected'
            inv.save()
            if inv.investor.email:
                from django.template.loader import render_to_string
                html = render_to_string('emails/payment_rejected.html', {'investment': inv, 'payment': pay})
                send_mail('Investment rejected', 'Your investment was rejected.', None, [inv.investor.email], html_message=html, fail_silently=True)
        return redirect('..')


@admin.register(Investment)
class InvestmentAdmin(admin.ModelAdmin):
    list_display = ('id', 'investor', 'campaign', 'amount', 'status', 'transaction_id', 'invested_at')
    list_filter = ('status', 'campaign')
    actions = ['approve_investments', 'reject_investments']

    def approve_investments(self, request, queryset):
        for inv in queryset:
            inv.status = 'approved'
            inv.save()
            if inv.investor.email:
                send_mail('Investment approved', f'Your investment of {inv.amount} has been approved.', None, [inv.investor.email], fail_silently=True)
    approve_investments.short_description = 'Approve selected investments'

    def reject_investments(self, request, queryset):
        for inv in queryset:
            inv.status = 'rejected'
            inv.save()
            if inv.investor.email:
                send_mail('Investment rejected', f'Your investment of {inv.amount} was rejected. Please contact support.', None, [inv.investor.email], fail_silently=True)
    reject_investments.short_description = 'Reject selected investments'


@admin.register(WebhookEvent)
class WebhookEventAdmin(admin.ModelAdmin):
    list_display = ('id', 'gateway', 'event_id', 'payment', 'processed', 'received_at')
    list_filter = ('gateway', 'processed')
    readonly_fields = ('raw_payload', 'signature', 'received_at', 'processed_at')