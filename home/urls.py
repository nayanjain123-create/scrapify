from django.urls import path
from home import views
from .views import seller_dashboard,collector_dashboard

urlpatterns = [
    path("",views.home,name='home'),
    path("about",views.about,name='about'),
    path("transaction",views.seller_transaction,name='transaction'),
    path("notify",views.notify,name='notify'),
    path("contact",views.contact,name='contact'),
    # path("service",views.service,name='service'),
    path("support",views.support,name='support'),
    path("price",views.price,name='price'),
    path("login",views.loginuser,name='login'),
    path("logout",views.logoutuser,name='logout'),
    path("register",views.register,name='register'),
    path('seller/', seller_dashboard, name='seller_dashboard'),
    path('collector/', collector_dashboard, name='collector_dashboard'),
    path('profile/', views.user_profile, name='user_profile'),
    path('setting/', views.setting, name='setting'),
    path('order/', views.order, name='order'),
    # path("notifications/", views.notifications, name="notifications"),
    # path('post-scrap/', views.post_scrap, name='post_scrap'),
]