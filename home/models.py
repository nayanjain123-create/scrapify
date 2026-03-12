from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Contact(models.Model):
    name=models.CharField(max_length=122)
    email=models.EmailField(max_length=254)
    phone= models.CharField(max_length=12)
    desc=models.TextField()
    date=models.DateField()

    def __str__(self):
        return self.name
    
class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    role = models.CharField(
        max_length=20,
        choices=[
            ('seller', 'Seller'),
            ('collector', 'Collector')
        ]
    )

    mobile = models.CharField(max_length=15, unique=True)

    dob = models.DateField(null=True, blank=True)

    flat_no = models.TextField(blank=True, null=True)
    building_name = models.CharField(max_length=100, blank=True, null=True)
    area = models.CharField(max_length=100, blank=True, null=True)
    pincode = models.CharField(max_length=6, blank=True, null=True)

    profile_completed = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class RegistrationOTP(models.Model):
    email = models.EmailField(unique=True)
    otp = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email

class Scrap(models.Model):

    SCRAP_TYPES = [
        ('plastic', 'Plastic'),
        ('paper', 'Paper'),
        ('aluminium', 'Aluminium'),
        ('iron', 'Iron'),
        ('brass','Brass'),
        ('copper', 'Copper'),
        ('electronics', 'E-Waste'),
        ('glass', 'Glass'),
        ('mixed', 'Mixed Scrap'),
    ]

    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    scrap_type = models.CharField(max_length=50, choices=SCRAP_TYPES)

    quantity = models.DecimalField(max_digits=6, decimal_places=2)

    scrap_image = models.ImageField(upload_to="scrap_images/", null=True, blank=True)

    flat_no = models.CharField(max_length=100,blank=True,null=True)
    building_name = models.CharField(max_length=200,blank=True,null=True)
    area = models.CharField(max_length=200)
    pincode = models.CharField(max_length=10)

    status = models.CharField(
        max_length=20,
        choices=[
            ('posted', 'Posted'),
            ('requested', 'Requested'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('completed', 'Completed'),
        ],
        default='posted'
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scrap_type} - {self.seller.username}"
        
class Notification(models.Model):
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.receiver.username} - {self.message[:30]}"


class PickupRequest(models.Model):

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('completed', 'Completed'),
        ('failed','Failed'),
        ('cancelled',"Cancelled")
    ]

    scrap = models.ForeignKey(Scrap, on_delete=models.CASCADE)
    seller = models.ForeignKey(User, related_name='seller_requests', on_delete=models.CASCADE)
    collector = models.ForeignKey(User, related_name='collector_requests', on_delete=models.CASCADE)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    scheduled_date = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.scrap.scrap_type} - {self.seller.username}"
    

class ScrapPrice(models.Model):
    collector = models.ForeignKey(User, on_delete=models.CASCADE)
    scrap_type = models.CharField(
    max_length=50,
    choices=Scrap.SCRAP_TYPES
    )

    price_per_kg = models.DecimalField(max_digits=6, decimal_places=2)

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.collector.username} - {self.scrap_type}"

class PickupReceipt(models.Model):

    pickup_request = models.ForeignKey(
        "PickupRequest",
        on_delete=models.CASCADE
    )

    collector = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    total_amount = models.FloatField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Receipt {self.id}"
        
class ReceiptItem(models.Model):

    receipt = models.ForeignKey(
        PickupReceipt,
        on_delete=models.CASCADE
    )

    scrap_type = models.CharField(max_length=100)

    quantity = models.FloatField()

    price_per_kg = models.FloatField()

    total = models.FloatField()

    def __str__(self):
        return self.scrap_type
    
class CollectorReview(models.Model):

    collector = models.ForeignKey(User, on_delete=models.CASCADE, related_name="collector_reviews")
    seller = models.ForeignKey(User, on_delete=models.CASCADE)

    rating = models.IntegerField(
    choices=[
        (1,"1 Star"),
        (2,"2 Stars"),
        (3,"3 Stars"),
        (4,"4 Stars"),
        (5,"5 Stars"),
    ]
    )
    comment = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('collector', 'seller')

    def __str__(self):
        return f"{self.collector.username} - {self.rating}"