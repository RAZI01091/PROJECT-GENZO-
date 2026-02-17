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
from . models import Products,Category,SubCategory,Banner,Wishlist,Size,Cart,Profile
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import Coalesce







@never_cache
def home(request):
    banner = Banner.objects.filter(is_active=True).first()
    trending = Products.objects.filter(is_trending=True)
    return render(request,"home.html",{"banner": banner,'trending':trending})
   


@never_cache
def signup(request):

    if request.user.is_authenticated:
        return redirect('home')

    if request.method == "POST":
        form = Signupform(request.POST)

        if form.is_valid():
            form.save()
            
            return redirect('loggin')

    else:
        form = Signupform()

    return render(request, "signup.html", {'form': form})

@never_cache
def loggin(request):



    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':

        form = Loginform(request.POST)

        if form.is_valid():

            user = form.user

            login(request, user)   

            if user.is_staff or user.is_superuser:
                return redirect('adminpanel')

            return redirect('home')

    else:
        form = Loginform()

    return render(request, 'login.html', {'form': form})



@login_required(login_url='showlogin')
def cart(request):
    cart_items = Cart.objects.filter(user=request.user)

    total_price = 0
    for item in cart_items:
        price = item.product.discount_price or item.product.price
        total_price += price * item.quandity

    context = {
        "cart_items": cart_items,   
        "total_price": total_price
    }

    return render(request, "cart.html", context)




@login_required(login_url='showlogin')
def carts(request, product_id):

    product = get_object_or_404(Products, id=product_id)

    if request.method == "POST":

        size_id = request.POST.get("size")


        if product.category.has_size:
            if not size_id:
                return redirect("productsdetail", id=product.id)

            size = get_object_or_404(Size, id=size_id)



        else:
            size = None

        cart_item, created = Cart.objects.get_or_create(
            user=request.user,
            product=product,
            size=size,
            defaults={"quandity": 1}
        )

        if not created:
            cart_item.quandity += 1
            cart_item.save()

    return redirect("cart")



@login_required
def remove_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()

    return redirect("cart")


@login_required
def increase_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    cart_item.quandity += 1
    cart_item.save()

    return redirect("cart")


@login_required
def decrease_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    if cart_item.quandity > 1:
        cart_item.quandity -= 1
        cart_item.save()

    return redirect("cart")




@login_required(login_url='loggin')
def wishlists(request):
    wishlist_items = Wishlist.objects.filter(
        User=request.user
    ).select_related('Products')

    return render(request, 'wishlist.html', {
        'wishlist_items': wishlist_items
    })

@login_required(login_url='loggin')
def wishlist(request, product_id):

    if request.method != "POST":
        return redirect('casualfit')

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

    return redirect(request.META.get('HTTP_REFERER', '/'))



def casualfit(request):
    casual = Category.objects.get(name='Casual')
    products = Products.objects.filter(category=casual).annotate(effective_price=Coalesce('discount_price','price'))

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)


    top_sizes=Size.objects.filter(size_type='TOP')
    bottom_sizes=Size.objects.filter(size_type='BOTTOM')

    selected_size = request.GET.getlist('size')
    if selected_size:                       
        products = products.filter(sizes__name__in=selected_size).distinct()

    

    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')

    if min_price:
        products =products.filter(effective_price__gte=min_price)

    if max_price:
        products=products.filter(effective_price__lte=max_price)



    wishlist_id = []
    if request.user.is_authenticated:
        wishlist_id = Wishlist.objects.filter(User=request.user).values_list('Products_id', flat=True)

    return render(request, 'casualfit.html', {
        'products': products,
        'wishlist_id': wishlist_id,
        'selected_sizes':selected_size,
        'bottom_sizes':bottom_sizes,
        'top_sizes':top_sizes
    })




def formalfit(request):
    formal=Category.objects.get(name='Formal')
    products=Products.objects.filter(category=formal).annotate(effective_price=Coalesce('discount_price','price'))
    
    sub_id=request.GET.get("sub_id")

    if sub_id:
        products=Products.objects.filter(subcategory_id=sub_id)

    top_sizes=Size.objects.filter(size_type='TOP')  
    bottom_size=Size.objects.filter(size_type='BOTTOM')

    selected_size= request.GET.getlist('size')
    if selected_size:
        products=products.filter(sizes__name__in=selected_size).distinct()

    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price') 

    if min_price:
        products=products.filter(effective_price__gte=min_price)
        
    if max_price:
        products=products.filter(effective_price__lte=max_price)    

    wishlist_id=[]
    if request.user.is_authenticated:
        wishlist_id=Wishlist.objects.filter(User=request.user).values_list('Products_id',flat=True)    

    return render(request,"formalfit.html",{
        "products":products,
        'wishlist_id':wishlist_id,
        'top_sizes':top_sizes,
        'bottom_sizes':bottom_size,
        'selected_size':selected_size,
        })



def accessories(request):
    accessories=Category.objects.get(name='Accessories')
    products=Products.objects.filter(category=accessories).annotate(effective_price=Coalesce('discount_price','price'))

    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.filter(subcategory_id=sub_id)

    top_sizes=Size.objects.filter(size_type='TOP')

    selected_size=request.GET.getlist('size')
    if selected_size:
        products=products.filter(sizes__name__in=selected_size).distinct() 

    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')

    if min_price:
        products=products.filter(effective_price__gte=min_price)

    if max_price:
        products=products.filter(effective_price__lte=max_price)           

    wishlist_id=[]

    if request.user.is_authenticated:
            wishlist_id=Wishlist.objects.filter(User=request.user).values_list('Products_id',flat=True)
    else:
        wishlist_id=[]


    return render(request,"accessories.html",{
        "products":products,
        'wishlist_id':wishlist_id,
        'top_sizes':top_sizes,
        'selected_size':selected_size,
        'min_price':min_price,
        'max_price':max_price
        
        })

def newarrivals(request):
    newarrivals=Category.objects.get(name='New arrival')
    products=Products.objects.filter(category=newarrivals)

    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)

    wishlist_id=[]

    if request.user.is_authenticated:
            wishlist_id=Wishlist.objects.filter(User=request.user).values_list('Products_id',flat=True)
    else:
        wishlist_id=[]
    return render(request,"newarrivals.html",{'products':products,'wishlist_id':wishlist_id})




def innerwear(request):
    innerwear=Category.objects.get(name='Innerwear')
    products=Products.objects.filter(category=innerwear).annotate(effective_price=Coalesce('discount_price','price'))
    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)



    wishlist_id=[]

    if request.user.is_authenticated:
        wishlist_id=Wishlist.objects.filter(User=request.user).values_list('Products_id',flat=True)

    top_sizes=Size.objects.filter(size_type='TOP')

    selected_size=request.GET.getlist('size')
    if selected_size:
        products=products.filter(sizes__name__in=selected_size).distinct()

    min_price=request.GET.get('min_price')
    max_price=request.GET.get('max_price')

    if min_price:
        products=products.filter(effective_price__gte=min_price)

    if max_price:
        products=products.filter(effective_price__lte=max_price)    


    return render(request,"innerwear.html",{
        "products":products,
        'wishlist_id':wishlist_id,
        'top_sizes':top_sizes,
        'selected_size':selected_size,

        })



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



        if password != confirm:
            messages.error(request, "Passwords do not match")
            return redirect('new_password')


        email = request.session.get('reset_email')

        if not email:
            messages.error(request, "Session expired. Please try again.")
            return redirect('forgot')


        user = User.objects.filter(email=email).first()

        if not user:
            messages.error(request, "User does not exist")
            return redirect('forgot')

        user.set_password(password)
        user.save()   

        
        request.session.flush()

        messages.success(request, "Password updated successfully")
        return redirect('loggin')

    return render(request, 'new_password.html')

def showlogin(request):
    return render(request,"showlogin.html")


def profile(request):
    user=Profile.objects.get(user=request.user)
    return render(request,"profile.html",{'user':user})
def profilesetup(request):
    return render(request,("profilesetup.html"))

def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')

def order(request):
    return render(request,"order.html")

@never_cache
@staff_member_required(login_url='home')
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



@staff_member_required(login_url='home')
def addproducts(request):
    categories = Category.objects.all()
    subcategories = SubCategory.objects.none()

    size_top=Size.objects.filter(size_type='TOP')
    size_bottom=Size.objects.filter(size_type='BOTTOM')

    if request.method=="POST":
        selected_sizes=request.POST.getlist('sizes')
        
        selected_sizes_objs=Size.objects.filter(id__in=selected_sizes)

        top_selected=selected_sizes_objs.filter(size_type="TOP").exists()
        bottom_selected=selected_sizes_objs.filter(size_type="BOTTOM").exists()

        if top_selected and bottom_selected:
            messages.error(request,"Please select sizes from ONLY ONE group (Top OR Bottom).")

            return redirect(request.path)

    if request.method == 'POST':
        product=Products.objects.create(
            name=request.POST.get('name'),
            price = request.POST.get('price') or 0,
            category_id=request.POST.get('category'),
            subcategory_id=request.POST.get('subcategory'),
            stock=int(request.POST.get('stock', 0)),
            description=request.POST.get('description'),
            discount_price=request.POST.get('discount_price') or None,
            discount_percentage=request.POST.get('discount_percentage') or None,
            is_trending = request.POST.get('is_trending') == 'on',


            image=request.FILES.get('image'),
            image1=request.FILES.get('image1'),
            image2=request.FILES.get('image2'),
            image3=request.FILES.get('image3'),     
        )
        product.sizes.set(selected_sizes)
        return redirect('adminproducts')

    first_category = categories.first()
    selected_category_id = request.GET.get('category') or (first_category.id if first_category else None)

    if selected_category_id:
        subcategories = SubCategory.objects.filter(category_id=selected_category_id)

    return render(request, 'addproducts.html', {
        'categories': categories,
        'subcategories': subcategories,
        'selected_category': int(selected_category_id) if selected_category_id else None,
        'sizes_top':size_top,
        'sizes_bottom':size_bottom
    })   


def coupons(request):
    return render(request,"coupons.html")
def checkout(request):
    return render(request,"checkout.html")
def payment(request):
    return render(request,"payment.html")
def ordersummary(request):
    return render(request,"ordersummary.html")


@staff_member_required(login_url='home')
def productsedit(request,id):
    return render('productsedit')


def productsdelete(request,id):
    Products.objects.filter(id=id).delete()
    return redirect('adminproducts')

@staff_member_required(login_url='home')
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

    sizes_top=Size.objects.filter(size_type='TOP')
    size_Bottom=Size.objects.filter(size_type='BOTTOM')

    if request.method=="POST":
        select_sizes=request.POST.getlist('sizes')

        select_sizes_objs=Size.objects.filter(id__in=select_sizes)

        top_selected=select_sizes_objs.filter(size_type="TOP").exists()
        bottom_selecetd=select_sizes_objs.filter(size_type="BOTTOM").exists()

        if top_selected and bottom_selecetd:
            messages.error(request,"Please select sizes from ONLY ONE group (Top OR Bottom).")

            return redirect(request.path)

    if request.method == 'POST':
        product.name = request.POST.get('name')
        product.price = request.POST.get('price')
        product.stock = request.POST.get('stock')
        product.description = request.POST.get('description')
        product.discount_price = request.POST.get('discount_price') or None
        product.discount_percentage = request.POST.get('discount_percentage') or None
        product.category_id = request.POST.get('category')
        product.subcategory_id = request.POST.get('subcategory')
        product.trending = request.POST.get('is_trending') == 'on'
        

        
        if request.FILES.get('image'):
            product.image = request.FILES.get('image')

        if request.FILES.get('image1'):
            product.image1 = request.FILES.get('image1')

        if request.FILES.get('image2'):
            product.image2 = request.FILES.get('image2')

        if request.FILES.get('image3'):
            product.image3 = request.FILES.get('image3')

        product.save()

        product.sizes.set(select_sizes)
        return redirect('adminproducts')

    return render(request, 'editproducts.html', {
        'product': product,
        'categories': categories,
        'subcategories': subcategories,
        'sizes_top':sizes_top,
        'sizes_bottom':size_Bottom
    })


def product_detail(request, id):
    product = get_object_or_404(Products, id=id)


    available_sizes = product.sizes.all()


    is_top = available_sizes.filter(size_type='TOP').exists()
    is_bottom = available_sizes.filter(size_type='BOTTOM').exists()


    has_size = product.category.has_size


    default_size = None
    if has_size:
        default_size = available_sizes.first()

    return render(request, 'product_detail.html', {
        'product': product,
        'available_sizes': available_sizes,
        'is_top': is_top,
        'is_bottom': is_bottom,
        'has_size': has_size,
        'default_size': default_size,
    })










