from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.template.loader import get_template
from django.http import HttpResponse
from .models import CollectorReview
from django.db.models import Avg
from datetime import datetime
from datetime import date
from .models import Profile, PickupRequest, PickupReceipt
from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.db.models import Sum
from .models import Profile, PickupReceipt
from xhtml2pdf import pisa
from .models import PickupRequest, Profile, RegistrationOTP, Scrap, Notification, ScrapPrice, PickupReceipt, ReceiptItem, CollectorReview
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate, logout, login
import random
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404
from .models import Notification
from .models import PickupRequest
from django.core.mail import send_mail
from django.conf import settings

@login_required
def mark_all_notifications_read(request):
    Notification.objects.filter(
        receiver=request.user,
        is_read=False
    ).update(is_read=True)

    return redirect('notifications')

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(
        Notification,
        id=notification_id,
        receiver=request.user
    )
    notification.is_read = True
    notification.save()
    return redirect('notifications')


def get_user_profile(user):
    try:
        return Profile.objects.get(user=user)
    except Profile.DoesNotExist:
        return None

def home(request):
    if not request.user.is_authenticated:
        return redirect('login')

    profile = get_user_profile(request.user)

    if not profile:
        messages.error(request, "Profile not found. Contact support.")
        return redirect('logout')

    if profile.role == "seller":
        return render(request,'seller_dashboard.html', {'page': 'home'})
    else:
        return render(request,'collector_dashboard.html', {'page': 'home'})

@login_required
def complete_pickup(request, request_id):

    pickup_request = get_object_or_404(PickupRequest, id=request_id)

    # only collector can complete
    if request.user != pickup_request.collector:
        return redirect("collector_orders")

    pickup_request.status = "completed"
    pickup_request.scrap.status = "completed"

    pickup_request.save()
    pickup_request.scrap.save()

    Notification.objects.create(
        receiver=pickup_request.seller,
        message="Your scrap has been collected successfully."
    )

    return redirect("collector_orders")

def about(request):
    if request.user.is_anonymous:
        return render(request, "login.html")
    return render(request, "about.html", {'page': 'about'})

@login_required
def order(request):

    orders = None

    profile = get_user_profile(request.user)

    if profile.role == "collector":
        orders = PickupRequest.objects.filter(
            collector=request.user
        ).exclude(status="completed").order_by("-id")

    return render(request, "order.html", {'orders': orders,'page': 'order'})

def setting(request):
    if request.user.is_anonymous:
        return render(request, "login.html")
    profile = get_user_profile(request.user)
    if profile.role == 'seller':
        return render(request, "seller_setting.html", {'page': 'setting'})
    return render(request, "collector_setting.html", {'page': 'setting'})

def support(request):
    profile=get_user_profile(request.user)
    if profile.role=="seller":
        template="seller_support.html"
    else:
        template="support.html"
    if request.method == "POST":

        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")

        subject = f"Support Request from {name}"

        full_message = f"""
Name: {name}
Email: {email}

Message:
{message}
"""

        send_mail(
            subject,
            full_message,
            settings.EMAIL_HOST_USER,
            ['Scrapify <scrapify148@gmail.com>'],
            fail_silently=False
        )
        messages.success(request, "Support Request Sent successfully!")

        return render(request, template, {
            "success": True, "page":"support"
        })

    return render(request, template,{"page":"support"})

def service(request):
    if request.user.is_anonymous:
        return render(request, "login.html")
    return render(request, "service.html", {'page': 'service'})

def contact(request):
    if request.user.is_anonymous:
        return render(request, "login.html")
    return render(request, "contact.html", {'page': 'contact'})

@login_required
def edit_prices(request):

    prices = ScrapPrice.objects.filter(collector=request.user)

    if request.method == "POST":
        scrap_type = request.POST.get("scrap_type")
        price = request.POST.get("price")

        ScrapPrice.objects.create(
            collector=request.user,
            scrap_type=scrap_type,
            price_per_kg=price
        )
        messages.success(request, "Scrap item added successfully!")
        return redirect("price")

    return render(request, "collector_price.html", {
        "prices": prices,
        "page": "pricing"
    })

@login_required
def edit_price(request, id):

    item = ScrapPrice.objects.get(id=id, collector=request.user)

    if request.method == "POST":
        item.scrap_type = request.POST.get("scrap_type")
        item.price_per_kg = request.POST.get("price")
        item.save()
    messages.success(request, "Scrap item edited successfully!")
    return redirect("price")


@login_required
def submit_review(request):

    if request.method == "POST":

        collector_id = request.POST.get("collector_id")
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        collector = User.objects.get(id=collector_id)

        # check if review already exists
        if CollectorReview.objects.filter(collector=collector, seller=request.user).exists():

            messages.warning(request, "You have already reviewed this collector.")
            return redirect("seller_dashboard")

        CollectorReview.objects.create(
            collector=collector,
            seller=request.user,
            rating=rating,
            comment=comment
        )

        messages.success(request, "Review submitted successfully!")

        return redirect("seller_dashboard")

@login_required
def delete_price(request, id):

    item = ScrapPrice.objects.get(id=id, collector=request.user)
    item.delete()
    messages.success(request, "Scrap item deleted successfully!")
    return redirect("price")

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            login(request, user)
            profile = get_user_profile(user)

            if profile.role == 'seller':
                return redirect('seller_dashboard')
            return redirect('collector_dashboard')

        messages.error(request, "Invalid username or password")

    return render(request, "login.html")

def logoutuser(request):
    logout(request)
    return redirect('login')

def register(request):
    if request.method == "POST":
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        mobile = request.POST['mobile']
        role = request.POST['role']

        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists")
            return redirect('register')

        if Profile.objects.filter(mobile=mobile).exists():
            messages.error(request, "Mobile number already registered")
            return redirect('register')

        otp = str(random.randint(100000, 999999))

        RegistrationOTP.objects.update_or_create(
            email=email,
            defaults={'otp': otp}
        )

        send_mail(
            subject="Scrapify OTP Verification",
            message=f"Your Registeration OTP is:{otp}",
            from_email="Scrapify <scrapify148@gmail.com>",
            recipient_list=[email],
        )

        request.session['reg_data'] = {
            'username': username,
            'email': email,
            'password': password,
            'mobile': mobile,
            'role': role
        }

        messages.success(request, "OTP sent to your email")
        return redirect('verify_otp')

    return render(request, "register.html")

def verify_otp(request):
    if request.method == "POST":
        entered_otp = request.POST['otp']
        reg_data = request.session.get('reg_data')

        otp_obj = RegistrationOTP.objects.filter(email=reg_data['email']).first()

        if otp_obj and otp_obj.otp == entered_otp:

            user = User.objects.create_user(
                username=reg_data['username'],
                email=reg_data['email'],
                password=reg_data['password']
            )

            Profile.objects.create(
                user=user,
                mobile=reg_data['mobile'],
                role=reg_data['role']
            )

            send_mail(
                subject="Welcome to Scrapify♻️",
                message=f"""
                Hello {user.username},

                Your account has been successfully created.

                Welcome to Scrapify♻️

                You can now request scrap pickups and manage your recycling easily.

                Thank you for joining us.

                Team Scrapify
                """,
                from_email="Scrapify <scrapify148@gmail.com>",
                recipient_list=[user.email],
                fail_silently=False,
            )

            del request.session['reg_data']

            messages.success(request, "Account created successfully!")
            return redirect('login')

        else:
            messages.error(request, "Enter valid OTP!")

    return render(request, "verify_otp.html")

@login_required
def user_profile(request):
    profile = get_user_profile(request.user)

    if request.method == "POST":
        
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.email = request.POST.get('email')
        request.user.save()

        
        profile.flat_no = request.POST.get('flat_no')
        profile.building_name = request.POST.get('building_name')
        profile.area = request.POST.get('area')
        profile.pincode = request.POST.get('pincode')
        profile.dob = request.POST.get('dob')

        
        if profile.flat_no and profile.building_name and profile.area and profile.pincode:
            profile.profile_completed = True

        profile.save()

        messages.success(request, "Profile updated successfully")

        return redirect('user_profile')

    context = {
        'profile': profile,
        'page': 'profile'
    }

    if profile.role == 'seller':
        return render(request, "seller_profile.html", context)

    return render(request, "collector_profile.html", context)

    

@login_required
def post_scrap(request):

    if request.method == "POST":

        scrap_type = request.POST.get("scrap_type")
        quantity = request.POST.get("quantity")

        flat_no = request.POST.get("flat_no")
        building_name = request.POST.get("building_name")
        area = request.POST.get("area")
        pincode = request.POST.get("pincode")

        scrap_image = request.FILES.get("scrap_image")

        seller = request.user

        scrap = Scrap.objects.create(
            seller=seller,
            scrap_type=scrap_type,
            quantity=quantity,
            flat_no=flat_no,
            building_name=building_name,
            area=area,
            pincode=pincode,
            scrap_image=scrap_image
        )

        return redirect("select_collector", scrap_id=scrap.id)

    return redirect("home")
    
@login_required
def select_collector(request, scrap_id):

    scrap = get_object_or_404(Scrap, id=scrap_id)

    # Get collectors who added price for this scrap type
    collectors = User.objects.filter(
        profile__role="collector",
        profile__pincode=scrap.pincode,
        scrapprice__scrap_type=scrap.scrap_type
    ).distinct().select_related("profile")

    # Price list for this scrap type
    prices = ScrapPrice.objects.filter(scrap_type=scrap.scrap_type)

    return render(request, "select_collector.html", {
        "scrap": scrap,
        "collectors": collectors,
        "prices": prices
    })

@login_required
def view_collectors(request):

    profile = Profile.objects.get(user=request.user)
    if not profile.mobile or not profile.area or not profile.pincode:
        messages.warning(request, "Incomplete profile. Please complete your profile first.")
        return redirect("user_profile")
    collectors = User.objects.filter(
        profile__role="collector",
        profile__pincode=profile.pincode
    ).select_related("profile")
    

    collectors = collectors.annotate(
        avg_rating=Avg("collector_reviews__rating")
    )
    return render(request, "view_collectors.html", {
        "collectors": collectors,
        "page": "collectors"
    })

@login_required
def dealer_pricing(request, collector_id):

    collector = get_object_or_404(User, id=collector_id)

    prices = ScrapPrice.objects.filter(collector=collector)

    return render(request, "dealer_pricing.html", {
        "collector": collector,
        "prices": prices
    })

def collector_prices(request, collector_id):

    collector = get_object_or_404(User, id=collector_id)

    prices = ScrapPrice.objects.filter(collector=collector)

    data = []

    for price in prices:
        data.append({
            "scrap_type": price.scrap_type,
            "price": price.price_per_kg
        })

    return JsonResponse({"prices": data})

@login_required
def post_scrap_to_collector(request, collector_id):

    collector = get_object_or_404(User, id=collector_id)

    if request.method == "POST":

        scrap = Scrap.objects.create(
            seller=request.user,
            scrap_type=request.POST.get("scrap_type"),
            quantity=request.POST.get("quantity"),
            flat_no=request.POST.get("flat_no"),
            building_name=request.POST.get("building_name"),
            area=request.POST.get("area"),
            pincode=request.POST.get("pincode"),
        )

        PickupRequest.objects.create(
            scrap=scrap,
            seller=request.user,
            collector=collector
        )

        Notification.objects.create(
            receiver=collector,
            message=f"New scrap pickup request from {request.user.username}"
        )

        messages.success(request, "Request sent successfully")

        return redirect("seller_dashboard")

    return render(request, "post_scrap_request.html", {
        "collector": collector
    })

@login_required
def send_request_popup(request):

    if request.method == "POST":

        collector_id = request.POST.get("collector_id")
        scrap_type = request.POST.get("scrap_type")
        quantity = request.POST.get("quantity")

        flat_no = request.POST.get("flat_no")
        building_name = request.POST.get("building_name")
        area = request.POST.get("area")
        pincode = request.POST.get("pincode")

        scrap_image = request.FILES.get("scrap_image")

        seller = request.user
        collector = User.objects.get(id=collector_id)

        scrap = Scrap.objects.create(
            seller=seller,
            scrap_type=scrap_type,
            quantity=quantity,
            flat_no=flat_no,
            building_name=building_name,
            area=area,
            pincode=pincode,
            scrap_image=scrap_image
        )

        scrap.status = "requested"
        scrap.save()

        PickupRequest.objects.create(
            seller=seller,
            collector=collector,
            scrap=scrap,
            status="pending"
        )

        Notification.objects.create(
            receiver=collector,
            message=f"New scrap request from {seller.username}"
        )

        seller_message = f"""
Hello {seller.username},

Your pickup request has been sent successfully.

Scrap Type: {scrap.scrap_type}
Quantity: {scrap.quantity}
Area: {scrap.area}

Collector: {collector.username}

Collector will soon accept your request.

Thank you for using Scrapify.
"""

        send_mail(
            "Request Sent Successfully",
            seller_message,
            "Scrapify <scrapify148@gmail.com>",
            [seller.email],
        )

        collector_message = f"""
Hello {collector.username},

You have received a new pickup request.

Seller: {seller.username}
Scrap Type: {scrap.scrap_type}
Quantity: {scrap.quantity}

Address: {scrap.flat_no}, {scrap.building_name}
Area: {scrap.area}
Pincode: {scrap.pincode}

Login to Scrapify to accept or reject the request.
"""

        send_mail(
            "New Scrap Request Received",
            collector_message,
            "Scrapify <scrapify148@gmail.com>",
            [collector.email],
        )

        messages.success(request, "Request sent successfully!")
        return redirect("seller_dashboard")

    return redirect("home")

@login_required
def collector_price_view(request, scrap_id, collector_id):

    scrap = Scrap.objects.get(id=scrap_id)
    collector = User.objects.get(id=collector_id)

    price = ScrapPrice.objects.filter(
        collector=collector,
        scrap_type=scrap.scrap_type
    ).first()

    context = {
        'scrap': scrap,
        'collector': collector,
        'price': price
    }

    return render(request, "collector_price_view.html", context)

@login_required
def seller_dashboard(request):

    profile = Profile.objects.get(user=request.user)
    auto_cancel_requests()
    show_popup = False

    if (
        not request.user.first_name or
        not request.user.last_name or
        not profile.dob or
        not profile.flat_no or
        not profile.building_name or
        not profile.area or
        not profile.pincode
    ):
        show_popup = True

    return render(request, "seller_dashboard.html", {
        "show_popup": show_popup
    })



@login_required
def collector_dashboard(request):

    profile = Profile.objects.get(user=request.user)

    show_popup = False

    if (
        not request.user.first_name or
        not request.user.last_name or
        not profile.dob or
        not profile.flat_no or
        not profile.building_name or
        not profile.area or
        not profile.pincode
    ):
        show_popup = True


    # ALL ORDERS FOR THIS COLLECTOR
    orders = PickupRequest.objects.filter(collector=request.user)

    # TOTAL ORDERS
    total_orders = PickupRequest.objects.filter(
    collector=request.user
    ).count()

    # TOTAL SELLERS
    total_users = orders.values('seller').distinct().count()

    # TOTAL EARNINGS
    total_earning = PickupReceipt.objects.filter(
        collector=request.user
    ).aggregate(total=Sum('total_amount'))['total'] or 0

    # TOTAL SCRAP COLLECTED
    total_scrap = ReceiptItem.objects.filter(
    receipt__collector=request.user
    ).aggregate(total=Sum('quantity'))['total'] or 0

    # RECENT ORDERS
    recent_orders = orders.order_by('-created_at')[:5]


    return render(request, "collector_dashboard.html", {
        "show_popup": show_popup,
        "total_orders": total_orders,
        "total_users": total_users,
        "monthly_turnover": total_earning,
        "total_scrap": total_scrap,
        "recent_orders": recent_orders,
        "page": "home"
    })

def download_receipt_pdf(request, receipt_id):

    receipt = PickupReceipt.objects.get(id=receipt_id)

    template = get_template("receipt_pdf.html")

    context = {
        "receipt": receipt
    }

    html = template.render(context)

    response = HttpResponse(content_type="application/pdf")
    response['Content-Disposition'] = f'attachment; filename="receipt_{receipt.id}.pdf"'

    pisa.CreatePDF(html, dest=response)

    return response

@login_required
def generate_receipt(request, request_id):

    pickup = get_object_or_404(PickupRequest, id=request_id)

    if request.method == "POST":

        scrap_types = request.POST.getlist("scrap_type[]")
        quantities = request.POST.getlist("quantity[]")
        prices = request.POST.getlist("price[]")

        receipt = PickupReceipt.objects.create(
            pickup_request=pickup,
            collector=request.user
        )

        total_amount = 0

        for scrap, qty, price in zip(scrap_types, quantities, prices):

            qty = float(qty)
            price = float(price)

            total = qty * price

            ReceiptItem.objects.create(
                receipt=receipt,
                scrap_type=scrap,
                quantity=qty,
                price_per_kg=price,
                total=total
            )

            total_amount += total

        receipt.total_amount = total_amount
        receipt.save()

        pickup.status = "completed"
        pickup.save()

        # -------- Notification to Seller --------

        Notification.objects.create(
        receiver=pickup.seller,
        message="Your scrap has been collected successfully. You can login and check the receipt."
        )

        # -------- Email to Seller and Collector --------

        subject = "Scrap Collection Completed - Scrapify"

        message = f"""
Hello,

Your scrap collection has been completed successfully.

Seller: {pickup.seller.username}
Collector: {request.user.username}

Please login to Scrapify to view your receipt.

Thank you,
Scrapify Team
"""

        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [pickup.seller.email, request.user.email],
            fail_silently=False,
        )

        messages.success(request, "Receipt generated successfully")

        return redirect("view_receipt", receipt_id=receipt.id)

    return render(request, "generate_receipt.html", {"pickup": pickup})

def collector_receipts(request):

    receipts = PickupReceipt.objects.filter(collector=request.user).order_by("-created_at")

    return render(request, "collector_receipts.html", {
        "receipts": receipts,
        "page":"receipts"
    })


@login_required
def seller_receipts(request):

    receipts = PickupReceipt.objects.filter(
        pickup_request__seller=request.user
    )

    reviewed_collectors = CollectorReview.objects.filter(
        seller=request.user
    ).values_list("collector_id", flat=True)

    return render(request, "seller_receipts.html", {
        "receipts": receipts,
        "reviewed_collectors": reviewed_collectors
    })
    
@login_required
def delete_receipt(request, receipt_id):

    receipt = PickupReceipt.objects.get(id=receipt_id)

    if receipt.pickup_request.seller == request.user:
        receipt.delete()
    messages.success(request, "Reciept deleted successfully")
    return redirect("seller_receipts")

@login_required
def view_receipt(request, receipt_id):

    receipt = get_object_or_404(PickupReceipt, id=receipt_id)

    return render(request, "view_receipt.html", {
        "receipt": receipt
    })

def collector_history(request):

    receipts = PickupReceipt.objects.filter(collector=request.user)

    return render(request, "collector_history.html", {
        "receipts": receipts
    })

@login_required
def notifications_view(request):
    notifications = Notification.objects.filter(receiver=request.user).order_by('-created_at')
    profile = get_user_profile(request.user)

    if profile.role == "seller":
        return render(request, "seller_notification.html", {
            'notifications': notifications,
            'page': 'notification'
        })

    return render(request, "collector_notification.html", {
        'notifications': notifications,
        'page': 'notification'
    })

@login_required
def seller_transaction(request):

    transactions = PickupRequest.objects.filter(
        seller=request.user
    ).select_related('collector').order_by('-scheduled_date')

    return render(request,
        "seller_transaction.html",{
        "transactions":transactions,
        "page":"transaction"
        })
    
@login_required
def request_collector(request, scrap_id, collector_id):

    scrap = Scrap.objects.get(id=scrap_id)
    collector = User.objects.get(id=collector_id)

    PickupRequest.objects.create(
        scrap=scrap,
        seller=request.user,
        collector=collector
    )

    scrap.status = 'requested'
    scrap.save()

    Notification.objects.create(
        receiver=collector,
        message=f"New scrap request from {scrap.area}"
    )

    if collector.email:
        send_mail(
            subject="New Scrap Pickup Request",
            message=f"""
Hello {collector.username},

You have received a new scrap pickup request.

Seller: {request.user.username}
Scrap Type: {scrap.scrap_type}
Quantity: {scrap.quantity}

Address: {scrap.flat_no}, {scrap.building_name}
Area: {scrap.area}
Pincode: {scrap.pincode}

Login Scrapify to accept or reject the request.
""",
            from_email="Scrapify <scrapify148@gmail.com>",
            recipient_list=[collector.email],
            fail_silently=True,
        )

    if request.user.email:
        send_mail(
            subject="Request Sent Successfully",
            message=f"""
Hello {request.user.username},

Your request has been successfully sent to {collector.username}.

Scrap Type: {scrap.scrap_type}
Quantity: {scrap.quantity}
Area: {scrap.area}

Collector will soon accept your request.
""",
            from_email="Scrapify <scrapify148@gmail.com>",
            recipient_list=[request.user.email],
            fail_silently=True,
        )

    messages.success(request, "Request sent successfully")
    return redirect('seller_dashboard')

@login_required
def pickup_request_popup(request, request_id):

    pickup_request = PickupRequest.objects.select_related(
        'scrap',
        'seller',
        'collector'
    ).get(id=request_id)

    seller_profile = Profile.objects.get(user=pickup_request.seller)

    data = {
        "seller": pickup_request.seller.username,
        "phone": seller_profile.mobile,
        "email": pickup_request.seller.email,

        "area": pickup_request.scrap.area,
        "address": pickup_request.scrap.address,
        "pincode": pickup_request.scrap.pincode,

        "type": pickup_request.scrap.scrap_type,
        "quantity": pickup_request.scrap.quantity,

        "status": pickup_request.status,
        "scheduled": pickup_request.scheduled_date
    }

    return JsonResponse(data)

def get_request_details(request, request_id):

    req = PickupRequest.objects.get(id=request_id)

    return JsonResponse({
        "seller_name": req.seller.username,
        "phone": req.seller.profile.mobile,
        "scrap_type": req.scrap.scrap_type,
        "quantity": req.scrap.quantity,
        "area": req.scrap.area,
    })

@login_required
def collector_orders(request):

    orders = PickupRequest.objects.filter(
        collector=request.user
    ).order_by("-created_at")

    return render(request, "order.html", {
        "orders": orders,
        "page": "order"
    })

from datetime import datetime
from django.utils import timezone
from django.contrib import messages

from django.core.mail import send_mail
from django.conf import settings

@login_required
def accept_pickup(request, request_id):

    pickup = PickupRequest.objects.get(id=request_id)

    if request.method == "POST":

        pickup_date_raw = request.POST.get("scheduled_date")

        print("DATE RECEIVED:", pickup_date_raw)

        if not pickup_date_raw:
            messages.error(request, "Please select a pickup date.")
            return redirect(request.META.get('HTTP_REFERER'))

        pickup_date = datetime.strptime(pickup_date_raw, "%Y-%m-%dT%H:%M")
        pickup_date = timezone.make_aware(pickup_date)

        if pickup_date.date() <= timezone.now().date():
            messages.error(request, "Pickup must be scheduled for a future date.")
            return redirect(request.META.get('HTTP_REFERER'))

        # Save pickup
        pickup.scheduled_date = pickup_date
        pickup.status = "accepted"
        pickup.collector = request.user
        pickup.save()

        # ==============================
        # CREATE WEBSITE NOTIFICATION
        # ==============================

        Notification.objects.create(
            receiver=pickup.seller,
            message=f"Your pickup has been scheduled on {pickup_date.strftime('%d %b %Y at %I:%M %p')} by {request.user.username}."
        )

        # ==============================
        # SEND EMAIL TO SELLER
        # ==============================

        subject = "Scrap Pickup Scheduled - Scrapify"

        email_message = f"""
Hello {pickup.seller.username},

Your scrap pickup request has been accepted.

Collector: {request.user.username}
Pickup Date: {pickup_date.strftime('%d %B %Y')}
Pickup Time: {pickup_date.strftime('%I:%M %p')}

Thank you for using Scrapify.

Team Scrapify
"""

        send_mail(
            subject,
            email_message,
            settings.EMAIL_HOST_USER,
            [pickup.seller.email],
            fail_silently=False,
        )

        messages.success(request, "Pickup scheduled successfully!")

        return redirect("order")
    
# @login_required
# def accept_pickup(request, request_id):
#     pickup_request = get_object_or_404(PickupRequest, id=request_id)

#     if request.method == "POST":
#         pickup_date_raw = request.POST.get('pickup_date')
#         pickup_date = timezone.make_aware(datetime.fromisoformat(pickup_date_raw))

#         PickupSchedule.objects.create(
#             request=pickup_request,
#             pickup_date=pickup_date,
#             collector_name=request.user.username,
#             collector_phone=request.user.profile.mobile,
#             collector_email=request.user.email
#         )

#         pickup_request.status = 'accepted'
#         pickup_request.scrap.status = 'accepted'
#         pickup_request.save()
#         pickup_request.scrap.save()

#         Notification.objects.create(
#             receiver=pickup_request.seller,
#             message="Your scrap pickup request was accepted"
#         )

#         if pickup_request.seller.email:
#             send_mail(
#                 "Scrap Pickup Accepted",
#                 f"""
#                 Hello {pickup_request.seller.username},

#                 Your scrap pickup request has been accepted.

#                 Collector: {request.user.username}
#                 Pickup Date: {pickup_date.strftime("%d %B %Y, %I:%M %p")}
#                 Area: {pickup_request.scrap.area}

#                 Please keep your scrap ready for collection.

#                 Thank you for using Scrapify.
#                 """,
#                 settings.DEFAULT_FROM_EMAIL,
#                 [pickup_request.seller.email],
#                 fail_silently=True
#             )
#         messages.success(request, "Order Scheduled successfully.")
#         return redirect('collector_orders')

#     return render(request, 'accept_pickup.html', {'request': pickup_request})

@login_required
def reject_pickup(request, request_id):
    pickup_request = PickupRequest.objects.get(id=request_id)
    pickup_request.status = 'rejected'
    pickup_request.save()

    Notification.objects.create(
        receiver=pickup_request.seller,
        message="Your scrap request was rejected"
    )
    messages.success(request, "Request Rejected successfully.")
    return redirect('collector_orders')

@login_required
def pickup_request_detail(request, request_id):
    pickup_request = PickupRequest.objects.select_related(
        'scrap',
        'seller',
        'collector'
    ).get(id=request_id)

    seller_profile = Profile.objects.get(user=pickup_request.seller)

    context = {
        'pickup_request': pickup_request,
        'seller_profile': seller_profile,
        'scrap': pickup_request.scrap,
    }

    return render(request, 'pickup_request_detail.html', context)

from datetime import date
from django.contrib import messages

@login_required
def schedule_pickup(request, request_id):

    pickup = get_object_or_404(PickupRequest, id=request_id)

    if request.method == "POST":
        scheduled_date = request.POST.get("scheduled_date")

        if scheduled_date:
            scheduled_date = date.fromisoformat(scheduled_date)

            # ❌ Prevent past or today date
            if scheduled_date <= date.today():
                messages.error(request, "Pickup date must be a future date.")
                return redirect("collector_requests")

            pickup.scheduled_date = scheduled_date
            pickup.status = "scheduled"
            pickup.collector = request.user
            pickup.save()

            messages.success(request, "Pickup scheduled successfully!")
            return redirect("collector_requests")

    return redirect("collector_requests")

def auto_cancel_requests():

    today = timezone.now().date()

    expired_requests = PickupRequest.objects.filter(
        status="scheduled",
        scheduled_date__lt=today
    )

    expired_requests.update(status="failed")

def complete_pickup(request, request_id):
    pickup_request = get_object_or_404(PickupRequest, id=request_id)

    pickup_request.status = 'completed'
    pickup_request.scrap.status = 'completed'
    pickup_request.save()
    pickup_request.scrap.save()

    send_mail(
        subject="Scrap Pickup Completed",
        message=f"""
        Hello {pickup_request.seller.username},

        Your scrap pickup has been successfully completed.

        Scrap Type: {pickup_request.scrap.scrap_type}
        Quantity: {pickup_request.scrap.quantity}

        Thank you for using Scrapify.
        """,
        from_email="Scrapify <scrapify148@gmail.com>",
        recipient_list=[pickup_request.seller.email],
        fail_silently=False,
    )
    messages.success(request, "Order Completed successfully.")
    return redirect('collector_orders')

@login_required
def delete_notification(request, notification_id):

    notification = get_object_or_404(
        Notification,
        id=notification_id,
        receiver=request.user
    )

    notification.delete()
    messages.success(request, "Notification deleted successfully!")
    return redirect('notifications')

@login_required
def delete_all_notifications(request):

    Notification.objects.filter(
        receiver=request.user
    ).delete()
    messages.success(request, "Notifications deleted successfully!")
    return redirect('notifications')