from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class User(AbstractUser):
    email=models.EmailField(unique=True)
    
class Category(models.Model):
    name=models.CharField(max_length=100,null=True)

    def __str__(self):
        return self.name
    
class SubCategory(models.Model):
    name = models.CharField(max_length=100)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name="subcategories")
    
    def __str__(self):
        return f"{self.category.name} -> {self.name}"

        

class Products(models.Model):
    name=models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
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


