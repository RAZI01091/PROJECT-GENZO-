from django.shortcuts import render,redirect,get_object_or_404
from .forms import Signupform,Loginform
from django.contrib.auth import login
import random
from django.core.mail import send_mail
from django.contrib.auth import get_user_model
from django.contrib import messages
User = get_user_model()
from django.conf import settings
from django.views.decorators.cache import never_cache
from django.contrib.auth import logout as auth_logout
from . models import Products,Category,SubCategory,Banner,Wishlist,User
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required




@never_cache
def home(request):
    banner = Banner.objects.filter(is_active=True).first()
    return render(request,"home.html",{"banner": banner})
   



@never_cache
def signup(request):
        
        if 'key' in request.session:
            return redirect('home')
        
        form=Signupform(request.POST or None)
        if form.is_valid():
            form.save()
            return redirect('loggin')
    

        return render(request,"signup.html",{'form':form})

@never_cache
def loggin(request):
    if 'key' in request.session:
        return redirect('home')
        
    if request.method == 'POST':
        form = Loginform(request.POST)
        if form.is_valid():
            user = form.user

                        
            # request.session['key']='user'
            # request.session.set_expiry(0)

            
            if user.is_staff or user.is_superuser:
                return redirect('adminpanel') 
            else:
                request.session['key']='user'
                request.session.set_expiry(0)
                return redirect('home')  
            
    else:
        form = Loginform()
    
    return render(request, 'login.html', {'form': form})

def cart(request):
    if 'key' not in request.session:
        return redirect("showlogin")
    return render(request,("cart.html"))

@login_required
def wishlist(request, product_id):
    product = get_object_or_404(Products, id=product_id)

    wishlist_item = Wishlist.objects.filter(
        User=request.user,
        Products=product
    ).first()

    if wishlist_item:
        wishlist_item.delete()   
    else:
        Wishlist.objects.create(
            User=request.user,
            Products=product
        )                       

    return redirect(request.META.get('HTTP_REFERER'))

@login_required
def wishlists(request):
    items=Wishlist.objects.filter(User=request.user)
    return render(request,'wishlist.html',{'items':items})


def casualfit(request):
    casual = Category.objects.get(name='Casual')
    products = Products.objects.filter(category=casual)

    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)

    return render(request, 'casualfit.html', {
        'products': products
    })



def formalfit(request):
    formal=Category.objects.get(name='Formal')
    products=Products.objects.filter(category=formal)
    
    sub_id=request.GET.get("sub_id")

    if sub_id:
        products=Products.objects.filter(subcategory_id=sub_id)

    return render(request,"formalfit.html",{"products":products})

def accessories(request):
    accessories=Category.objects.get(name='Accessories')
    products=Products.objects.filter(category=accessories)
    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)

    return render(request,"accessories.html",{"products":products})

def newarrivals(request):
    newarrivals=Category.objects.get(name='New arrival')
    products=Products.objects.filter(category=newarrivals)

    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)
    return render(request,"newarrivals.html",{'products':products})

def innerwear(request):
    innerwear=Category.objects.get(name='Innerwear')
    products=Products.objects.filter(category=innerwear)
    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)
    return render(request,"innerwear.html",{"products":products})



def forgot(request):
    if request.method=="POST":
        email=request.POST.get('email')

        try:
            user=User.objects.filter(email=email).first()
        except User.DoesNotExist:
            messages.error(request,"Email not registered")
            return redirect('forgot')

        otp=random.randint(100000,999999)

        request.session['reset_email']=email
        request.session['otp']=str(otp)

        send_mail(
           subject="Password reset OTP",
           message=f"Your OTP is {otp}",
           from_email=settings.DEFAULT_FROM_EMAIL,
           recipient_list=[email],
        )

        return redirect('verify_otp')
    
    return render(request,'forgot.html')




def verify_otp(request):
    if request.method == "POST":

        # 🔁 Resend OTP
        if 'resend' in request.POST:
            email = request.session.get('reset_email')

            if not email:
                messages.error(request, "Session expired. Try again.")
                return redirect('forgot')

            otp = random.randint(100000, 999999)
            request.session['otp'] = str(otp)

            send_mail(
                subject="Password Reset OTP",
                message=f"Your OTP for password reset is {otp}",
                from_email=None,
                recipient_list=[email],
                fail_silently=False,
            )

            messages.success(request, "New OTP has been sent to your email")
            return redirect('verify_otp')

        # ✅ Verify OTP
        entered_otp = request.POST.get('otp')
        session_otp = request.session.get('otp')

        if entered_otp == session_otp:
            del request.session['otp']   #  clear OTP
            return redirect('new_password')
        else:
            messages.error(request, "Invalid OTP")
            return redirect('verify_otp')

    return render(request, 'verify_otp.html')




def new_password(request):
    if request.method == "POST":
        password = request.POST.get('password')
        confirm = request.POST.get('confirm_password')

        # Password mismatch check
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('new_password')

        # Get email from session safely
        email = request.session.get('reset_email')

        if not email:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot')

        # Get user safely
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "User does not exist")
            return redirect('forgot')

        #  Set newpas
        user.set_password(password)
        user.save()   

        
        request.session.flush()

        messages.success(request, "Password updated successfully")
        return redirect('loggin')

    return render(request, 'new_password.html')

def showlogin(request):
    return render(request,"showlogin.html")


def profile(request):
    return render(request,("profile.html"))
def profilesetup(request):
    return render(request,("profilesetup.html"))
def logout(request):
    auth_logout(request)
    request.session.flush()
    return redirect('home')
def order(request):
    return render(request,"order.html")

@never_cache
def adminpanel(request):
    
    if 'key' in request.session:
        return redirect('home')
    return render(request,"adminpanel.html")

def adminproducts(request):
    product=Products.objects.all()
   
    return render(request,"adminproducts.html",{'products':product})


def adminorders(request):
    return render(request,"adminorders.html")


def adminusers(request):
    user=User.objects.filter(is_superuser=False)
    return render(request,"adminusers.html",{'user':user})
def block_unblock(request,user_id):
    user=User.objects.get(id=user_id)
    user.is_active =not user.is_active
    user.save()
    return redirect('adminusers')


def adminsettings(request):
    return render(request,"adminsettings.html")




def addproducts(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.none()

    if request.method == 'POST':
        Products.objects.create(
            name=request.POST.get('name'),
            price = request.POST.get('price') or 0,
            category_id=request.POST.get('category'),
            subcategory_id=request.POST.get('subcategory'),
            stock=int(request.POST.get('stock', 0)),
            description=request.POST.get('description'),
            discount_price=request.POST.get('discount_price') or None,
            discount_percentage=request.POST.get('discount_percentage') or None,
            image=request.FILES.get('image'),
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),     
        )
        return redirect('adminproducts')

    first_category = categories.first()
    selected_category_id = request.GET.get('category') or (first_category.id if first_category else None)

    if selected_category_id:
        subcategories = SubCategory.objects.filter(category_id=selected_category_id)

    return render(request, 'addproducts.html', {
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': int(selected_category_id) if selected_category_id else None
    })   


def coupons(request):
    return render(request,"coupons.html")
def checkout(request):
    return render(request,"checkout.html")
def payment(request):
    return render(request,"payment.html")
def ordersummary(request):
    return render(request,"ordersummary.html")

def productsedit(request,id):
    return render('productsedit')
def productsdelete(request,id):
    Products.objects.filter(id=id).delete()
    return redirect('adminproducts')


def banner(request):
    if request.method == "POST":

        if request.POST.get("delete_banner_id"):
            banner_obj = Banner.objects.get(
                id=request.POST.get("delete_banner_id")
            )
            banner_obj.delete()
            return redirect('banner')

        Banner.objects.create(
            title=request.POST.get('title'),
            subtitle=request.POST.get('subtitle'),
            image=request.FILES.get('image'),
        )
        return redirect('banner')

    banners = Banner.objects.all()
    return render(request, 'banner.html', {
        'banners': banners
    })


def editproducts(request, id):
    product = get_object_or_404(Products, id=id)
    categories = Category.objects.all()
    subcategories = SubCategory.objects.filter(category=product.category)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')
        product.discount_price = request.POST.get('discount_price') or None
        product.discount_percentage = request.POST.get('discount_percentage') or None
        product.category_id = request.POST.get('category')
        product.subcategory_id = request.POST.get('subcategory')


        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        if request.FILES.get('image1'):
            product.image1 = request.FILES.get('image1')

        if request.FILES.get('image2'):
            product.image2 = request.FILES.get('image2')

        if request.FILES.get('image3'):
            product.image3 = request.FILES.get('image3')

        product.save()
        return redirect('adminproducts')

    return render(request, 'editproducts.html', {
        'product': product,
        'categories': categories,
        'subcategories': subcategories,
    })

def product_detail(request, id):
    product = get_object_or_404(Products, id=id)
    return render(request, 'product_detail.html', {'product': product})








