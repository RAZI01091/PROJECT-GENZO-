from django.shortcuts import render,redirect
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
from . models import Products,Category,SubCategory,Banner
from decimal import Decimal



@never_cache
def home(request):
    banner = Banner.objects.filter(is_active=True).first()
    return render(request,"home.html",{
        "banner": banner
    })
    # if 'key' in request.session:    
    #     print("User logged in ")
    # else:
    #     print("User not logged in ")




def signup(request):
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
            if not user.is_active:
                messages.error(request,"This user is blocked")
                return redirect('loggin')

            login(request, user)
            
            request.session['key']='user'
            request.session.set_expiry(0)

            
            if user.is_staff or user.is_superuser:
                return redirect('adminpanel') 
            else:
                return redirect('home')  
            
    else:
        form = Loginform()
    
    return render(request, 'login.html', {'form': form})

def cart(request):
    if 'key' not in request.session:
        return redirect("showlogin")
    return render(request,("cart.html"))
def wishlist(request):
    if 'key' not in request.session:
        return redirect("showlogin")
    return render(request,("wishlist.html"))
def casualfit(request):
    return render(request,("casualfit.html"))
def fashionfit(request):
    return render(request,("fashionfit.html"))
def accessories(request):
    return render(request,("accessories.html"))
def newarrivals(request):
    return render(request,("newarrivals.html"))
def innerwear(request):
    return render(request,("innerwear.html"))







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

        # 1️⃣ Password mismatch check
        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('new_password')

        # 2️⃣ Get email from session safely
        email = request.session.get('reset_email')

        if not email:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot')

        # 3️⃣ Get user safely
        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "User does not exist")
            return redirect('forgot')

        # 4️⃣ Set new password
        user.set_password(password)
        user.save()   # ✅ IMPORTANT

        # 5️⃣ Clear session
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



# def addproducts(request):
#     form=ProductForm()
    
#     if request.method=="POST":
#         form=ProductForm(request.POST,request.FILES)
#         if form.is_valid():
#             form.save()
#             return redirect('adminproducts')
#     return render(request,"addproducts.html")




def addproducts(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.none()

    if request.method == 'POST':
        Products.objects.create(
            name=request.POST.get('name'),
            category_id=request.POST.get('category'),
            subcategory_id=request.POST.get('subcategory'),
            price=float(request.POST.get('price', 0)),
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
    product = Products.objects.get(id=id)
    subcategories = SubCategory.objects.filter(category=product.category)

    context = {
        'product': product,
        'subcategories': subcategories,
    }

    return render(request, 'editproducts.html', context)








