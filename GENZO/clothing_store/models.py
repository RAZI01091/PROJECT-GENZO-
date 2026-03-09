from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings

# Create your models here.

class User(AbstractUser):
    email=models.EmailField(unique=True)
    
class Category(models.Model):
    name=models.CharField(max_length=100,null=True)
    has_size = models.BooleanField(default=True)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    
    def __str__(self):
        return f"{self.category.name} -> {self.name}"

class Size(models.Model):

    SIZE_TYPE = (
        ('TOP', 'Top Wear'),
        ('BOTTOM', 'Bottom Wear'),
    )

    size_type = models.CharField(max_length=10, choices=SIZE_TYPE)
    name = models.CharField(max_length=10)

    def __str__(self):
        return f"{self.name} ({self.size_type})"
    
class Products(models.Model):
    name=models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    sizes = models.ManyToManyField(Size, blank=True)
    description = models.TextField(null=True, blank=True)
    image=models.ImageField(upload_to='products/',blank=True,null=True)
    image1=models.ImageField(upload_to='products/',blank=True,null=True)
    image2=models.ImageField(upload_to='products/',blank=True,null=True)
    image3=models.ImageField(upload_to='products/',blank=True,null=True)
    stock=models.IntegerField(default=0)
    discount_price=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    discount_percentage=models.PositiveIntegerField(blank=True,null=True,help_text="Enter discount percentage(0-100)")
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    subcategory = models.ForeignKey(SubCategory, on_delete=models.CASCADE, null=True, blank=True)
    is_trending = models.BooleanField(default=False)
    is_listed=models.BooleanField(default=True)
    

    
    def __str__(self):
        return self.name
    
    


class Banner(models.Model):
    title = models.CharField(max_length=200, blank=True)
    subtitle = models.CharField(max_length=255, blank=True, null=True)
    image = models.ImageField(upload_to="banners/")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title if self.title else "Banner"


class Wishlist(models.Model):
    User=models.ForeignKey(User,on_delete=models.CASCADE,related_name='Wishlists')
    Products=models.ForeignKey(Products,on_delete=models.CASCADE,related_name='Wishlisted_by')

    class Meta:
        unique_together=('User','Products')

    def __str__(self):
        return f"{self.User.email}>{self.Products.name}"
    
class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Products, on_delete=models.CASCADE)
    size_text = models.CharField(max_length=10, blank=True)
    size = models.ForeignKey(Size,on_delete=models.CASCADE,null=True,blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.size:
            return f"{self.product.name} ({self.size})"
        return self.product.name
    

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15,blank=True,null=True)
    address=models.TextField(blank=True,null=True)
    image = models.ImageField(upload_to='profiles/', blank=True,null=True)

    def __str__(self):
        return self.user.username
    

class Address(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    name=models.CharField(max_length=10)
    phone=models.CharField(max_length=15)
    pincode=models.CharField(max_length=6)
    locality=models.CharField(max_length=30)
    address=models.CharField(max_length=100)
    city=models.CharField(max_length=20)
    state = models.CharField(max_length=30)
    is_default = models.BooleanField(default=False)



class Order(models.Model):

    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("confirmed", "Confirmed"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
    ]

    PAYMENT_METHOD_CHOICES = [
        ("COD", "Cash on Delivery"),
        ("STRIPE", "Stripe"),
    ]

    PAYMENT_STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("PAID", "Paid"),
        ("FAILED", "Failed"),
    ]
    

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,related_name='orders')
    address = models.ForeignKey("Address", on_delete=models.SET_NULL, null=True)
    
    total = models.DecimalField(max_digits=10, decimal_places=2)

    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHOD_CHOICES
    )

    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default="PENDING"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    stripe_session_id = models.CharField(max_length=255, blank=True, null=True)

    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)




    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-id"]

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name="items"   
    )

    product = models.ForeignKey(
        "Products",   
        on_delete=models.CASCADE
    )

    quantity = models.PositiveIntegerField(default=1)

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.product.name} x {self.quantity}"
    


class ReviewRating(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    product=models.ForeignKey(Products,on_delete=models.CASCADE)

    rating=models.IntegerField()
    review=models.TextField(blank=True,null=True)


    created_at=models.DateTimeField(auto_now_add=True)
    updated_at=models.DateTimeField(auto_now=True)

    class Meta:
        unique_together =('user', 'product')

    def __str__(self):
        return f"{self.user} - {self.product} -{self.rating}"   


class Notification(models.Model):
    user=models.ForeignKey(User,on_delete=models.CASCADE)
    message=models.CharField(max_length=250)
    is_read=models.BooleanField(default=False)
    created_at=models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
    
