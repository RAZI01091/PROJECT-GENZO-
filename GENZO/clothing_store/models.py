from django.db import models
from django.contrib.auth.models import AbstractUser
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
    quandity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.size:
            return f"{self.product.name} ({self.size})"
        return self.product.name
    

class Profile(models.Model):
    user=models.OneToOneField(User,on_delete=models.CASCADE)
    phone=models.CharField(max_length=15,blank=True)
    address=models.TextField(blank=True)
    image = models.ImageField(upload_to='profile_images/', default='profile_images/default.png')

    def __str__(self):
        return self.user.username


    



