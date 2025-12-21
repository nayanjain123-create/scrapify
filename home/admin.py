from django.contrib import admin
from home.models import Contact,Profile
from django.contrib.auth.models import User


# Register your models here.
admin.site.register(Contact),

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role')  # Columns in list view
    list_filter = ('role',)           # Optional: filter by role

admin.site.register(Profile, ProfileAdmin),
