from django.shortcuts import render, HttpResponse,redirect
from home.models import Contact
from .models import Profile
from django.contrib.auth.models import User
from datetime import datetime
from django.contrib import messages
from django.contrib.auth import authenticate,logout,login
from django.contrib.auth.decorators import login_required


def home(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.is_authenticated:
        if request.user.profile.role=="seller":
            return render(request,"seller_dashboard.html",{'page':'home'})
        else:
            return render(request,"collector_dashboard.html",{'page':'home'})

def about(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    return render(request,"about.html",{'page':'about'})

def setting(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.profile.role=='seller':
        return render(request,"seller_setting.html",{'page':'setting'})
    else:
        return render(request,"collector_setting.html",{'page':'setting'})

def order(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    return render(request,"order.html",{'page':'order'})


def seller_transaction(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.profile.role=='seller':
        return render(request,"seller_transaction.html",{'page':'transaction'})
    else:
        return render(request,"collector_transaction.html",{'page':'transaction'})

def notify(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.profile.role=='seller':
        return render(request,"seller_notification.html",{'page':'notification'})
    else:
        return render(request,"collector_notification.html",{'page':'notification'})

def support(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.profile.role=='seller':
        return render(request,"seller_support.html",{'page':'support'})
    else:
        return render(request,"collector_support.html",{'page':'support'})

def price(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    return render(request,"priceedit.html",{'page':'about'})

def user_profile(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.user.profile.role=='seller':
        return render(request,"seller_profile.html",{'page':'profile'})
    else:
        return render(request,"collector_profile.html",{'page':'profile'})

def contact(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    if request.method == "POST":
        name = request.POST.get('name'),
        email = request.POST.get('email'),
        phone = request.POST.get('phone'),
        desc = request.POST.get('desc'),
        contact = Contact(name=name, email=email, phone=phone, desc=desc, date = datetime. today())
        contact.save()
        messages.success(request,'The message have been sent!')
    return render(request,"contact.html",{'page':'contact'})

def service(request):
    if request.user.is_anonymous:
        return render(request,"login.html")
    
    return render(request,"service.html",{'page':'service'})

def loginuser(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method=="POST":
        username=request.POST.get('username')
        password=request.POST.get('password')
        user = authenticate(username=username, password=password)

        if user is not None:
            login(request,user)
            role = user.profile.role

            if role == 'seller':
                return redirect('seller_dashboard')
            else:
                return redirect('collector_dashboard')
        else:
            return render(request,"login.html")
    return render(request,"login.html")

def register(request):
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == "POST":
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        
        user = User.objects.create_user(username=username, email=email, password=password)
        Profile.objects.create(user=user, role=role)
        #user.save()
        messages.success(request,'You are registered Successfully!')
        return redirect('/login')
    return render(request,"register.html")

@login_required
def seller_dashboard(request):
    return render(request, 'seller_dashboard.html')

@login_required
def collector_dashboard(request):
    return render(request, 'collector_dashboard.html')

def logoutuser(request):
    logout(request)
    return redirect('/login')