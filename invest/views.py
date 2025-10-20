from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from .models import Business, Campaign, Investment, Update, ContactMessage, Profile, Payment
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from .forms import BusinessApplicationForm
from .forms import ProfileForm
from functools import wraps
from django.core.paginator import Paginator
from django.db.models import Sum
from django.http import HttpResponse, FileResponse
import csv
import os
from django.views.decorators.csrf import csrf_exempt
import json
from django.utils import timezone

# Custom login required decorator
def login_required_custom(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "YOU NEED TO LOGIN FIRST.")
            return redirect('register')
        return view_func(request, *args, **kwargs)
    return wrapper


def business_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "YOU NEED TO LOGIN FIRST.")
            return redirect('register')
        try:
            profile = request.user.profile
        except Profile.DoesNotExist:
            profile = None
        if not profile or not profile.is_business:
            messages.warning(request, "Business owner access required.")
            return redirect('home')
        return view_func(request, *args, **kwargs)
    return wrapper

def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username') or request.POST.get('email')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'invest/login.html')
    return render(request, 'invest/login.html')

def user_logout(request):
    logout(request)
    return redirect('home')

def register(request):
    if request.method == 'POST':
        username = (request.POST.get('username') or '').strip()
        email = (request.POST.get('email') or '').strip()
        password = request.POST.get('password')
        confirm = request.POST.get('confirm')
        role = request.POST.get('role')

        context = {
            'submitted_username': username,
            'submitted_email': email,
            'selected_role': role,
        }

        if role not in {'investor', 'business'}:
            context['error'] = 'Please select whether you are registering as an investor or a business owner.'
            return render(request, 'invest/register.html', context)

        if password != confirm:
            context['error'] = 'Passwords do not match.'
            return render(request, 'invest/register.html', context)

        if User.objects.filter(username=username).exists():
            context['error'] = 'Username already exists.'
            return render(request, 'invest/register.html', context)

        if User.objects.filter(email=email).exists():
            context['error'] = 'Email already exists.'
            return render(request, 'invest/register.html', context)

        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(
            user=user,
            is_investor=(role == 'investor'),
            is_business=(role == 'business'),
        )
        login(request, user)
        return redirect('home')
    return render(request, 'invest/register.html')

def home(request):
    campaigns = Campaign.objects.filter(is_funded=False).order_by('-created_at')[:6]
    return render(request, 'invest/home.html', {'campaigns': campaigns})

def about(request):
    return render(request, 'invest/about.html')

def contact(request):
    from .forms import ContactMessageForm
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Your message has been sent!")
            return redirect('contact')
    else:
        form = ContactMessageForm()
    return render(request, 'invest/contact.html', {'form': form})

def invest(request):
    qs = Campaign.objects.filter(is_funded=False)

    # sorting: 'percent' (descending), 'days' (ascending), 'new' (created_at desc)
    sort = request.GET.get('sort')
    if sort == 'percent':
        qs = sorted(qs, key=lambda c: c.percent_raised, reverse=True)
    elif sort == 'days':
        qs = qs.order_by('end_date')
    else:
        qs = qs.order_by('-created_at')

    return render(request, 'invest/invest.html', {'campaigns': qs, 'selected_sort': sort})

@login_required_custom
def portfolio(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        messages.warning(request, "Complete registration to view your portfolio.")
        return redirect('register')

    # Business owner dashboard
    if profile.is_business:
        businesses = Business.objects.filter(owner=request.user)
        businesses_data = []
        for b in businesses:
            campaigns = b.campaigns.all()
            campaign_stats = []
            total_raised = 0
            for c in campaigns:
                total = c.investments.aggregate(total=Sum('amount'))['total'] or 0
                investors_count = c.investments.values('investor').distinct().count()
                campaign_stats.append({'campaign': c, 'total': total, 'investors_count': investors_count})
                total_raised += total
            businesses_data.append({'business': b, 'campaigns': campaign_stats, 'total_raised': total_raised})
        return render(request, 'invest/portfolio.html', {'is_business': True, 'businesses_data': businesses_data})

    # Investor view (default)
    # Filtering
    qs = Investment.objects.filter(investor=request.user).order_by('-invested_at')
    status = request.GET.get('status')
    if status in {'pending', 'approved', 'rejected', 'returned'}:
        qs = qs.filter(status=status)

    # Export CSV
    if request.GET.get('export') == 'csv':
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="portfolio.csv"'
        writer = csv.writer(response)
        writer.writerow(['Campaign', 'Business', 'Amount', 'Status', 'Date', 'Transaction ID'])
        for inv in qs:
            writer.writerow([inv.campaign.title, inv.campaign.business.name, inv.amount, inv.status, inv.invested_at, inv.transaction_id])
        return response

    # Pagination
    paginator = Paginator(qs, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    totals = qs.aggregate(total_invested=Sum('amount'))

    return render(request, 'invest/portfolio.html', {'is_business': False, 'page_obj': page_obj, 'totals': totals, 'status': status})


@login_required_custom
def download_receipt(request, investment_id):
    # Only owner or staff can download receipt
    inv = get_object_or_404(Investment, id=investment_id)
    if request.user != inv.investor and not request.user.is_staff:
        return HttpResponse(status=403)
    if not inv.receipt_file:
        return HttpResponse(status=404)
    return FileResponse(open(inv.receipt_file.path, 'rb'), as_attachment=True, filename=os.path.basename(inv.receipt_file.path))


@login_required_custom
def profile_view(request):
    """Display the current user's profile."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    from django.utils import timezone
    today = timezone.localdate().strftime('%A, %d %B')
    return render(request, 'invest/profile.html', {'profile': profile, 'today': today})


@login_required_custom
def balance_view(request):
    # placeholder balance view
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    # Compute total invested as a simple example
    total = request.user.investments.filter(status='approved').aggregate(total=Sum('amount'))['total'] or 0
    return render(request, 'invest/balance.html', {'profile': profile, 'total': total})


@login_required_custom
def bank_view(request):
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    return render(request, 'invest/bank.html', {'profile': profile})


@login_required_custom
def change_password_view(request):
    # simple placeholder that links to Django's password change if configured
    return render(request, 'invest/change_password.html')


@login_required_custom
def profile_edit(request):
    """Edit the current user's profile (including avatar and KYC document)."""
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile(user=request.user)

    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            prof = form.save(commit=False)
            prof.user = request.user
            prof.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileForm(instance=profile)
    return render(request, 'invest/profile_edit.html', {'form': form})

@business_required
def apply(request):
    business = Business.objects.filter(owner=request.user).order_by('-created_at').first()
    if business:
        if business.is_approved:
            return render(request, 'invest/apply.html', {'already_applied': True, 'approved': True})
        elif business.is_rejected:
            can_reapply = True
        else:
            return render(request, 'invest/apply.html', {'already_applied': True, 'pending': True})
    else:
        can_reapply = True

    if request.method == 'POST' and can_reapply:
        form = BusinessApplicationForm(request.POST)
        if form.is_valid():
            business = form.save(commit=False)
            business.owner = request.user
            business.save()
            return render(request, 'invest/apply.html', {'success': True})
    else:
        form = BusinessApplicationForm()
    return render(request, 'invest/apply.html', {'form': form, 'can_reapply': can_reapply if business and business.is_rejected else False})

@business_required
def post(request):
    businesses = Business.objects.filter(owner=request.user)
    from .forms import CampaignForm
    if request.method == 'POST':
        form = CampaignForm(request.POST, request.FILES)
        business_id = request.POST.get('business')
        if form.is_valid() and business_id:
            business = get_object_or_404(Business, id=business_id, owner=request.user)
            c = form.save(commit=False)
            c.business = business
            c.save()
            messages.success(request, "Campaign posted successfully!")
            return redirect('business_detail', business_id=business.id)
        else:
            messages.error(request, 'Please correct the errors in the form.')
    else:
        form = CampaignForm()
    return render(request, 'invest/post.html', {'businesses': businesses, 'form': form})

def funded(request):
    campaigns = Campaign.objects.filter(is_funded=True)
    return render(request, 'invest/funded.html', {'campaigns': campaigns})

def business_detail(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    campaigns = business.campaigns.all()
    return render(request, 'invest/business_detail.html', {'business': business, 'campaigns': campaigns})

def campaign_detail(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)
    updates = campaign.updates.order_by('-created_at')
    # Compute whether current user is a business owner (safe check)
    user_is_business = False
    is_owner = False
    owner_investments = None
    owner_totals = None
    if request.user.is_authenticated:
        try:
            user_is_business = bool(request.user.profile.is_business)
        except Exception:
            user_is_business = False
        # check if current user is the owner of this campaign's business
        try:
            is_owner = (request.user == campaign.business.owner)
        except Exception:
            is_owner = False

    # If owner, collect investment breakdown and allow CSV export
    if is_owner:
        owner_investments = campaign.investments.select_related('investor').order_by('-invested_at')
        owner_totals = owner_investments.aggregate(total=Sum('amount'))
        if request.GET.get('export') == 'investors_csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{campaign.title}_investors.csv"'
            writer = csv.writer(response)
            writer.writerow(['Investor Username', 'Investor Email', 'Amount', 'Status', 'Date', 'Transaction ID'])
            for inv in owner_investments:
                writer.writerow([inv.investor.username, inv.investor.email, inv.amount, inv.status, inv.invested_at, inv.transaction_id])
            return response

    return render(request, 'invest/campaign_detail.html', {
        'campaign': campaign,
        'updates': updates,
        'user_is_business': user_is_business,
        'is_owner': is_owner,
        'owner_investments': owner_investments,
        'owner_totals': owner_totals,
    })

@login_required_custom
@login_required_custom
def invest_in_campaign(request, campaign_id):
    campaign = get_object_or_404(Campaign, id=campaign_id)

    # Prevent business owners from investing
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = None
    if profile and profile.is_business:
        messages.warning(request, "Business owners cannot invest in campaigns. You can only browse campaigns.")
        return redirect('campaign_detail', campaign_id=campaign.id)

    # prevent investing into campaigns that are already funded
    if campaign.is_funded or campaign.percent_raised >= 100.0:
        messages.warning(request, 'This campaign is already fully funded and cannot accept new investments.')
        return redirect('campaign_detail', campaign_id=campaign.id)

    # Prevent investing into campaigns after their end date
    if campaign.end_date and campaign.end_date < timezone.now().date():
        messages.warning(request, 'This campaign has ended and cannot accept new investments.')
        return redirect('campaign_detail', campaign_id=campaign.id)

    if request.method == 'POST':
        from decimal import Decimal, InvalidOperation
        amount = request.POST.get('amount')
        try:
            amt = Decimal(amount)
        except Exception:
            amt = Decimal('0')
        if amt < Decimal(str(campaign.min_investment)):
            messages.error(request, f'The minimum investment amount is ৳{campaign.min_investment}.')
            return render(request, 'invest/invest_in_campaign.html', {'campaign': campaign})
        if amt > Decimal('0'):
            # create pending investment and redirect to bKash start endpoint
            inv = Investment.objects.create(investor=request.user, campaign=campaign, amount=amt, status='pending')
            # Create a Payment record pointing to this investment
            from .models import Payment
            pay = Payment.objects.create(investment=inv, amount=amt, currency='BDT', gateway='bkash', status='pending')
            # For now we'll redirect to a local start endpoint that would call bKash
            return redirect('bkash_start', payment_id=pay.id)
    return render(request, 'invest/invest_in_campaign.html', {'campaign': campaign})


@login_required_custom
def bkash_start(request, payment_id):
    """Start a bKash payment: in production this would call bKash's token/session APIs and redirect user."""
    pay = get_object_or_404(Payment, id=payment_id, status='pending')
    # Placeholder: in a real integration you'd get a checkout url/token from bKash and redirect there.
    # For now, show a simple page with simulated 'pay' and 'cancel' links.
    return render(request, 'invest/bkash_start.html', {'payment': pay})


@csrf_exempt
def bkash_webhook(request):
    """Endpoint to receive bKash webhook notifications. Must validate signature in production."""
    # verify HMAC signature header (example header name: X-Bkash-Signature)
    import hmac
    import hashlib
    from django.conf import settings

    signature_header = request.META.get('HTTP_X_BKASH_SIGNATURE', '')
    secret = getattr(settings, 'BKASH_WEBHOOK_SECRET', '')
    if not secret:
        # If no secret is configured, reject in production; for now allow but log
        pass

    try:
        body = request.body or b''
        payload = json.loads(body)
    except Exception:
        return HttpResponse(status=400)

    # verify signature if secret provided
    if secret:
        mac = hmac.new(secret.encode('utf-8'), body, hashlib.sha256).hexdigest()
        if not hmac.compare_digest(mac, signature_header):
            return HttpResponse(status=400)

    payment_id = payload.get('payment_id')
    status = payload.get('status')
    transaction_id = payload.get('transaction_id')
    gateway_event_id = payload.get('gateway_event_id')

    try:
        pay = Payment.objects.get(id=payment_id)
    except Payment.DoesNotExist:
        return HttpResponse(status=404)

    # record the webhook event for auditing
    try:
        from .models import WebhookEvent
        we = WebhookEvent.objects.create(payment=pay, gateway='bkash', event_id=gateway_event_id or '', raw_payload=payload, signature=signature_header)
    except Exception:
        we = None

    # idempotency: if gateway_event_id already processed for this payment, skip
    if gateway_event_id and pay.gateway_event_id == gateway_event_id:
        if we:
            we.processed = False
            we.save(update_fields=['processed'])
        return HttpResponse(status=200)

    # map statuses
    if status == 'success':
        pay.status = 'succeeded'
        pay.transaction_id = transaction_id or pay.transaction_id
        pay.gateway_event_id = gateway_event_id or pay.gateway_event_id
        pay.raw_response = payload
        pay.save()
        if we:
            import django.utils.timezone as tz
            we.processed = True
            we.processed_at = tz.now()
            we.payment = pay
            we.save()
        inv = pay.investment
        if inv:
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
        if we:
            import django.utils.timezone as tz
            we.processed = True
            we.processed_at = tz.now()
            we.payment = pay
            we.save()
        inv = pay.investment
        if inv:
            inv.status = 'rejected'
            inv.save()

    return HttpResponse(status=200)


def bkash_success(request, payment_id):
    # user returned from bKash after payment (in real flow you'd verify server-side)
    pay = get_object_or_404(Payment, id=payment_id)
    return render(request, 'invest/bkash_success.html', {'payment': pay})


def bkash_cancel(request, payment_id):
    pay = get_object_or_404(Payment, id=payment_id)
    pay.status = 'cancelled'
    pay.save()
    if pay.investment:
        pay.investment.status = 'rejected'
        pay.investment.save()
    messages.info(request, 'Payment cancelled')
    return redirect('campaign_detail', campaign_id=pay.investment.campaign.id if pay.investment else 0)

@business_required
def post_update(request, campaign_id):
    from .forms import UpdateForm, UpdateEditForm
    from .models import UpdateAttachment, UpdateAudit

    campaign = get_object_or_404(Campaign, id=campaign_id, business__owner=request.user)
    last_update = Update.objects.filter(campaign=campaign).order_by('-created_at').first()
    if request.method == 'POST':
        form = UpdateForm(request.POST, request.FILES)
        if form.is_valid():
            upd = form.save(commit=False)
            upd.campaign = campaign
            upd.created_by = request.user
            # moderation: new updates require approval
            upd.is_approved = False
            upd.save()

            # save attachments
            files = request.FILES.getlist('attachments')
            for f in files:
                UpdateAttachment.objects.create(update=upd, file=f)

            # audit
            UpdateAudit.objects.create(update=upd, action='create', user=request.user, before_title='', before_content='')

            messages.success(request, "Update submitted for review. It will appear once approved by admin.")
            return redirect('campaign_detail', campaign_id=campaign.id)
    else:
        # Pre-fill the form with the most recent update for this campaign (if any)
        if last_update:
            form = UpdateForm(initial={'title': last_update.title, 'content': last_update.content})
        else:
            form = UpdateForm()
    return render(request, 'invest/post_update.html', {'campaign': campaign, 'form': form, 'last_update': last_update})


@business_required
def edit_update(request, update_id):
    from .forms import UpdateEditForm
    from .models import UpdateAudit
    upd = get_object_or_404(Update, id=update_id, campaign__business__owner=request.user)
    if request.method == 'POST':
        form = UpdateEditForm(request.POST, instance=upd)
        if form.is_valid():
            before_title = upd.title
            before_content = upd.content
            upd = form.save(commit=False)
            # edited updates must be re-approved
            upd.is_approved = False
            upd.approved_by = None
            upd.approved_at = None
            upd.save()

            # handle removal of existing attachments (checkboxes named remove_attachments)
            remove_ids = request.POST.getlist('remove_attachments')
            if remove_ids:
                from .models import UpdateAttachment
                for aid in remove_ids:
                    try:
                        a = UpdateAttachment.objects.get(id=int(aid), update=upd)
                        # delete file and record
                        a.file.delete(save=False)
                        a.delete()
                    except Exception:
                        pass

            # handle new uploaded files
            from .models import UpdateAttachment
            files = request.FILES.getlist('attachments')
            for f in files:
                UpdateAttachment.objects.create(update=upd, file=f)

            UpdateAudit.objects.create(update=upd, action='edit', user=request.user, before_title=before_title, before_content=before_content)
            messages.success(request, 'Update edited and submitted for review.')
            return redirect('campaign_detail', campaign_id=upd.campaign.id)
    else:
        form = UpdateEditForm(instance=upd)
    return render(request, 'invest/post_update.html', {'campaign': upd.campaign, 'form': form, 'editing': True, 'update': upd})


@business_required
def delete_update(request, update_id):
    from .models import UpdateAudit
    upd = get_object_or_404(Update, id=update_id, campaign__business__owner=request.user)
    if request.method == 'POST':
        UpdateAudit.objects.create(update=upd, action='delete', user=request.user, before_title=upd.title, before_content=upd.content)
        upd.delete()
        messages.success(request, 'Update deleted.')
        return redirect('campaign_detail', campaign_id=upd.campaign.id)
    return render(request, 'invest/confirm_delete.html', {'object': upd, 'type': 'update'})


def download_kyc(request, user_id):
    """Protected download for KYC documents. Only staff/superuser can access."""
    from django.http import FileResponse, HttpResponseForbidden, Http404
    import os
    if not request.user.is_authenticated or not request.user.is_staff:
        return HttpResponseForbidden('You do not have permission to access this file.')
    try:
        profile_user = User.objects.get(id=user_id)
        profile = profile_user.profile
    except (User.DoesNotExist, Profile.DoesNotExist):
        raise Http404()
    if not profile.kyc_document:
        raise Http404()
    file_path = profile.kyc_document.path
    if not os.path.exists(file_path):
        raise Http404()
    return FileResponse(open(file_path, 'rb'), as_attachment=True, filename=os.path.basename(file_path))

