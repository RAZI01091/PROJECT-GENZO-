from django.db import models
from django.contrib.auth.models import AbstractUser
# Create your models here.

class table(AbstractUser):
    email=models.EmailField(unique=True)
    
# class Category(models.Model):
#     name=models.CharField(max_length=100,null=True)

#     def __str__(self):
#         return self.name
        

class Products(models.Model):
    name=models.CharField(max_length=100)
    price=models.DecimalField(max_digits=10,decimal_places=2)
    description=models.TextField()
    image=models.ImageField(upload_to='products/',blank=True,null=True)
    image1=models.ImageField(upload_to='products/',blank=True,null=True)
    image2=models.ImageField(upload_to='products/',blank=True,null=True)
    image3=models.ImageField(upload_to='products/',blank=True,null=True)
    stock=models.IntegerField(default=0)
    discount_price=models.DecimalField(max_digits=10,decimal_places=2,blank=True,null=True)
    discount_percentage=models.PositiveIntegerField(blank=True,null=True,help_text="Enter discount percentage(0-100)")
    
    def __str__(self):
        return self.name
    

