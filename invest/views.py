import random, time
from django.core.mail import send_mail
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.http import HttpResponse

from invest.models import Update

def home(request):
    return render(request, 'invest/home.html')


def about(request):
    return render(request, 'invest/about.html')


def contact(request):
    return render(request, 'invest/contact.html')


def invest(request):
    return render(request, 'invest/invest.html')


def portfolio(request):
    return render(request, 'invest/portfolio.html')


def apply(request):
    return render(request, 'invest/apply.html')


def post(request):
    return render(request, 'invest/post.html')


def funded(request):
    return render(request, 'invest/funded.html')

# --------------------- OTP Helper ---------------------

def send_otp(request, email):
    otp = str(random.randint(100000, 999999))  # 6-digit OTP
    request.session['otp'] = otp
    request.session['email'] = email
    request.session['otp_time'] = time.time()

    try:
        send_mail(
            subject="Your Investor Verification Code",
            message=f"Your verification code is {otp}",
            from_email=settings.EMAIL_HOST_USER,
            recipient_list=[email],
            fail_silently=False,
        )
    except Exception as e:
        print("Email sending failed:", e)
        messages.error(request, "Could not send OTP. Try again later.")


# --------------------- Register & Verify ---------------------

def register(request):
    if request.method == "POST":
        full_name = request.POST.get("full_name")
        email = request.POST.get("email")
        password = request.POST.get("password")
        confirm_password = request.POST.get("reset_password")

        # Password check
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, "invest/register.html")

        # Email already exists check
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email is already registered.")
            return render(request, "invest/register.html")

        # Save temp user data
        request.session['temp_user'] = {
            "full_name": full_name,
            "email": email,
            "password": password,
        }

        send_otp(request, email)
        return redirect("verify")

    return render(request, "invest/register.html")


def verify(request):
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "submit":
            entered_otp = request.POST.get("otp")
            saved_otp = request.session.get("otp")
            otp_time = request.session.get("otp_time")

            # Expiry check (5 minutes)
            if otp_time and time.time() - otp_time > 300:
                return render(request, "invest/verify.html", {"error": "OTP expired. Please resend."})

            if entered_otp == saved_otp:
                data = request.session.get("temp_user")

                if data:
                    # Create user
                    user = User.objects.create_user(
                        username=data["email"],
                        email=data["email"],
                        password=data["password"],
                        first_name=data["full_name"]
                    )
                    user.save()

                    # Auto login after verify
                    auth_login(request, user)

                    # Clear session
                    for key in ["otp", "otp_time", "temp_user", "email"]:
                        request.session.pop(key, None)

                    messages.success(request, "Account created successfully!")
                    return redirect("dashboard")
            else:
                return render(request, "invest/verify.html", {"error": "Wrong code"})

        elif action == "resend":
            email = request.session.get("email")
            if email:
                send_otp(request, email)
                return render(request, "invest/verify.html", {"error": "A new OTP has been sent"})
            else:
                return redirect("register")

    return render(request, "invest/verify.html")


# --------------------- Auth ---------------------

def login(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is not None:
            auth_login(request, user)
            return redirect("dashboard")
        else:
            messages.error(request, "Invalid username or password")
            return redirect("login")

    return render(request, "invest/login.html")


def logout(request):
    auth_logout(request)
    return redirect("home")


# --------------------- Protected Pages ---------------------

@login_required(login_url='login')
def dashboard(request):
    updates = Update.objects.all().order_by("-created_at")[:5]
    return render(request, "invest/dashboard.html", {"updates": updates})

@login_required(login_url='login')
def funded(request):
    return render(request, "invest/funded.html")

@login_required(login_url='login')
def post(request):
    return render(request, "invest/post.html")

@login_required(login_url='login')
def apply(request):
    return render(request, "invest/apply.html")

@login_required(login_url='login')
def protfolio(request):
    return render(request, "invest/portfolio.html")

def verify_email(request):
    return render(request, "htmlpages/verifyemail.html")


# --------------------- Contact Form ---------------------

def send_message(request):
    if request.method == 'POST':
        name = request.POST['name']
        email = request.POST['email']
        message = request.POST['message']

        send_mail(
            f"New Message from {name}",
            message,
            email,
            [settings.AUTHORITY_EMAIL],
        )

        return HttpResponse("Thank you for contacting us! We will get back to you soon.")
    return redirect('home')

