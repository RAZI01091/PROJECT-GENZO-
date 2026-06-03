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
from . models import Products,Category,SubCategory,Banner,Wishlist,Size,Cart,Profile,Address,Order,OrderItem,ReviewRating,Notification
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login
from django.contrib.admin.views.decorators import staff_member_required
from django.db.models.functions import Coalesce
from django.db.models import Q
from django.db.models import Count
from decimal import Decimal
from django.conf import settings
from django.db.models import Sum
from django.db.models.functions import ExtractMonth
import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY












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
            user=form.save()

            Profile.objects.create(user=user)
            
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
                return redirect('admindashboard')

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
        total_price += price * item.quantity

    context = {
        "cart_items": cart_items,   
        "total_price": total_price
    }

    return render(request, "cart.html", context)


from django.contrib import messages

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
            defaults={"quantity": 1}
        )

        if not created:
            cart_item.quantity += 1
            cart_item.save()

        messages.success(request, "Product added to cart successfully")

    return redirect("productsdetail", id=product.id)

@login_required
def remove_cart(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)
    cart_item.delete()

    return redirect("cart")


@login_required
def increase_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    cart_item.quantity += 1
    cart_item.save()

    return redirect("cart")


@login_required
def decrease_qty(request, id):
    cart_item = get_object_or_404(Cart, id=id, user=request.user)

    if cart_item.quantity > 1:
        cart_item.quantity -= 1
        cart_item.save()

    return redirect("cart")

@login_required
def buy_now(request, product_id):
    request.session["buy_now_product_id"] = product_id
    return redirect("checkout")


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
    products = Products.objects.filter(category=casual,is_listed=True).annotate(effective_price=Coalesce('discount_price','price'))

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
    products=Products.objects.filter(category=formal,is_listed=True).annotate(effective_price=Coalesce('discount_price','price'))
    
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
        'selected_sizes':selected_size,
        })



def accessories(request):
    accessories=Category.objects.get(name='Accessories')
    products=Products.objects.filter(category=accessories,is_listed=True).annotate(effective_price=Coalesce('discount_price','price'))

    sub_id=request.GET.get("sub_id")

    if sub_id:
        products= Products.objects.filter(subcategory_id=sub_id)

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
        'selected_sizes':selected_size,
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
    products=Products.objects.filter(category=innerwear,is_listed=True).annotate(effective_price=Coalesce('discount_price','price'))
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
        'selected_sizes':selected_size,

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

login_required
def profile(request):
    profile, created=Profile.objects.get_or_create(user=request.user)
    return render(request,"profile.html",{'profile':profile})

login_required
def editprofile(request):
    profile, created=Profile.objects.get_or_create(user=request.user)
    if request.method=='POST':
        profile.phone=request.POST.get("phone")
        profile.address=request.POST.get("address")

        if request.FILES.get("image"):
            profile.image=request.POST.get("image")

        profile.save()
        return redirect('profile')    
    return render(request,("editprofile.html"))

@login_required
def addaddress(request):
    if request.method=="POST":

        is_default=request.POST.get('is_default')

        if is_default:
            Address.objects.filter(user=request.user,is_default=True).update(is_default=False)


        Address.objects.create(
            user=request.user,
            name=request.POST.get('name'),
            phone=request.POST.get('phone'),
            pincode=request.POST.get('pincode'),
            locality=request.POST.get('locality'),
            address=request.POST.get('address'),
            city=request.POST.get('city'),
            state=request.POST.get('state'),
        )
        return redirect('checkout')


    return render(request,'addaddress.html')
login_required
def delete_address(request,id):
    delete_address=get_object_or_404(Address,id=id,user=request.user)
    delete_address.delete()
    return redirect('checkout')




login_required
def logout(request):
    if request.user.is_authenticated:
        auth_logout(request)
    return redirect('home')

def order(request):
    orders=Order.objects.filter(user=request.user).prefetch_related("items__product")
    return render(request,"order.html",{'orders':orders})




@never_cache
@staff_member_required(login_url='home')
def admindashboard(request):

    total_orders = Order.objects.count()
    total_products = Products.objects.count()
    total_customers = User.objects.filter(is_staff=False).count()
    revenue = Order.objects.aggregate(total=Sum("total"))["total"] or 0

    monthly_sales = (
        Order.objects
        .annotate(month=ExtractMonth("created_at"))
        .values("month")
        .annotate(total=Sum("total"))
        .order_by("month")
    )

    context = {
        "total_orders": total_orders,
        "total_products": total_products,
        "total_customers": total_customers,
        "revenue": revenue,
        "monthly_sales": monthly_sales,
    }

    return render(request, "admindashboard.html", context)








staff_member_required
def adminproducts(request):
    product=Products.objects.all()
    category=Category.objects.all()
     
    category_id=request.GET.get('category') 

    if category_id:
        product=product.filter(category_id= category_id)
    
    search=request.GET.get("search")

    if search:
        product=product.filter(Q(name__icontains=search)|Q(category__name__icontains=search)).distinct()

    
    return render(request,"adminproducts.html",{
        'products':product,
        'categories':category
        })



staff_member_required
def adminorders(request):
    orders=Order.objects.prefetch_related('items__product').order_by('-id')
    return render(request,'adminorders.html',{'orders':orders})

staff_member_required
def update_order_status(request,order_id):
    if request.method=="POST":
        order=get_object_or_404(Order,id=order_id)
        new_status=request.POST.get('status')

        if new_status in dict(Order.STATUS_CHOICES):
            order.status=new_status
            order.save()

            Notification.objects.create(
                user=order.user,
                message=f"Your order #{order.id} status updated to {new_status}."
            )
    return redirect(adminorders)
staff_member_required
def adminorderdetails(request, order_id):
    order = Order.objects.prefetch_related("items__product").get(id=order_id)

    return render(request, "adminorderdetails.html", {"order": order})

staff_member_required
def adminusers(request):
    user=User.objects.filter(is_superuser=False)
    search=request.GET.get('search')

    if search:
        user=user.filter(Q(username__icontains=search)|Q(email__icontains=search))

    status=request.GET.get("status")

    if status =='active':
        user =user.filter(is_active=True)
    elif status:
        user=user.filter(is_active=False)

    return render(request,"adminusers.html",{'users':user})


staff_member_required
def block_unblock(request,user_id):
    user=User.objects.get(id=user_id)
    user.is_active =not user.is_active
    user.save()
    return redirect('adminusers')

staff_member_required
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



@login_required
def checkout(request):

    buy_now_product_id = request.session.get("buy_now_product_id")

    cart_queryset = Cart.objects.filter(user=request.user)
    addresses = Address.objects.filter(user=request.user)
    profile = Profile.objects.filter(user=request.user).first()

    # ===== BUY NOW FLOW =====
    if buy_now_product_id:
        product = get_object_or_404(Products, id=buy_now_product_id)

        price = product.discount_price or product.price
        total_price = price

        cart_items = [{
            "product": product,
            "quantity": 1,
        }]


        return render(request, "checkout.html", {
            "cart_items": cart_items,
            "total_price": total_price,
            "address": addresses,
            "profile": profile,
            "buy_now": True,
        })



    if not cart_queryset.exists():
        return redirect("cart")

    total_price = 0
    for item in cart_queryset:
        price = item.product.discount_price or item.product.price
        total_price += price * item.quantity

    return render(request, "checkout.html", {
        "cart_items": cart_queryset,
        "total_price": total_price,
        "address": addresses,
        "profile": profile,
        "buy_now": False,
    })




def payment(request):
    return render(request,"payment.html")


@staff_member_required(login_url='home')
def productsedit(request,id):
    return render('productsedit')
staff_member_required
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

staff_member_required
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

    reviews = ReviewRating.objects.filter(
        product=product,
    ).select_related("user")    

    return render(request, 'product_detail.html', {
        'product': product,
        'available_sizes': available_sizes,
        'is_top': is_top,
        'is_bottom': is_bottom,
        'has_size': has_size,
        'default_size': default_size,
        'reviews':reviews
    })


def searchbutton(request):
    query = request.GET.get('q')

    products = Products.objects.all().annotate(
        effective_price=Coalesce('discount_price', 'price')
    )

    if query:
        products = products.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(subcategory__name__icontains=query)
        ).distinct()

    sub_id = request.GET.get("sub_id")
    if sub_id:
        products = products.filter(subcategory_id=sub_id)

    top_sizes = Size.objects.filter(size_type='TOP')
    bottom_size = Size.objects.filter(size_type='BOTTOM')

    selected_size = request.GET.getlist('size')
    if selected_size:
        products = products.filter(
            sizes__name__in=selected_size
        ).distinct()

    wishlist_id = []
    if request.user.is_authenticated:

        wishlist_id = Wishlist.objects.filter(
            User=request.user
        ).values_list('Products_id', flat=True)
    

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if min_price:
        products = products.filter(effective_price__gte=min_price)

    if max_price:
        products = products.filter(effective_price__lte=max_price)

    return render(request, 'searchbutton.html', {
        'products': products,
        'query': query,
        'top_sizes': top_sizes,
        'bottom_sizes': bottom_size,
        'selected_sizes': selected_size,
        'min_price': min_price,
        'max_price': max_price,
        'wishlist_id':wishlist_id,
    })

def product_toggle(request,id):
    product=Products.objects.get(id=id)
    product.is_listed = not product.is_listed
    product.save()
    return redirect('adminproducts')


def admin_category(request):
    categories=Category.objects.annotate(sub_count=Count('subcategories',distinct=True),product_count=Count('products',distinct=True))
    return render(request,'admincategory.html',{
    'categories':categories})
staff_member_required
def add_category(request):
    if request.method=="POST":
        name =request.POST.get("name")
        
        if name:
            Category.objects.create(name=name)

    categories=Category.objects.all()

    return render(request,'addcategory.html',{
    'categories':categories})


staff_member_required
def add_subcategory(request):
    categories = Category.objects.all()

    # 🔹 handle add form
    if request.method == "POST":
        name = request.POST.get('name')
        category_id = request.POST.get('category')

        if name and category_id:
            SubCategory.objects.create(
                name=name,
                category_id=category_id
            )
            return redirect('add_subcategory')

    # 🔹 filter logic (IMPORTANT)
    selected_category = request.GET.get('filter_category')

    subcategories = SubCategory.objects.select_related('category')

    if selected_category:
        subcategories = subcategories.filter(category_id=selected_category)

    return render(request, 'addsubcategory.html', {
        'subcategories': subcategories,
        'categories': categories,
        'selected_category': selected_category,
    })
staff_member_required
def delete_category(request,id):
    category=get_object_or_404(Category,id=id)
    category.delete()
    return redirect('add_category')
staff_member_required
def update_category(request,id):
    category=get_object_or_404(Category,id=id)

    if request.method=="POST":
        name= request.POST.get("name")

        if name:
            category.name =name
            category.save()
    return redirect('add_category')
staff_member_required
def delete_subcategory(request,id):
    subcategory=get_object_or_404(SubCategory,id=id)
    subcategory.delete()
    return redirect('add_subcategory')
staff_member_required
def update_subcategory(request,id):
    subcategory=get_object_or_404(SubCategory,id=id)

    if request.method=="POST":
        name=request.POST.get('name')

        if name:
            subcategory.name=name
            subcategory.save()
    return redirect('add_subcategory')        


@login_required
def pay(request):
    address_id = request.POST.get('address_id')
    if not address_id:
        messages.error(request, 'please select the address')
        return redirect('checkout')

    discount = Decimal(str(request.session.get('discount', 0)))
    buy_now_product_id = request.session.get("buy_now_product_id")

    # ================= BUY NOW =================
    if buy_now_product_id:
        product = get_object_or_404(Products, id=buy_now_product_id)

        price = product.discount_price or product.price
        subtotal = price

        cart_items = [{
            'product': product,
            'quantity': 1,
        }]

    else:
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():  # ✅ FIXED
            messages.error(request, 'Cart is empty')
            return redirect('cart')

        subtotal = sum(
            (item.product.discount_price or item.product.price) * item.quantity
            for item in cart_items
        )

    total = max(subtotal - discount, 0)

    context = {
        "cart_items": cart_items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "address_id": address_id,
    }

    return render(request, 'pay.html', context)



@login_required
def place_order(request):

    payment_method = request.POST.get("payment_method")
    address_id = request.session.get("address_id")
    discount = Decimal(str(request.session.get("discount", 0)))
    buy_now_product_id = request.session.get("buy_now_product_id")

    #  total amount
    if buy_now_product_id:
        product = get_object_or_404(Products, id=buy_now_product_id)
        subtotal = product.discount_price or product.price
    else:
        cart_items = Cart.objects.filter(user=request.user)

        if not cart_items.exists():
            messages.error(request, "Cart is empty")
            return redirect("cart")

        subtotal = sum(
            (item.product.discount_price or item.product.price) * item.quantity
            for item in cart_items
        )

    total = max(subtotal - discount, 0)

    order = Order.objects.create(
        user=request.user,
        address_id=address_id,
        total=total,
        payment_method=payment_method,
        payment_status="PENDING",
        discount_amount=discount,
    )


    if buy_now_product_id:
        price = product.discount_price or product.price

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=1,
            price=price,
        )

    else:
        for item in cart_items:
            price = item.product.discount_price or item.product.price

            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,  
                price=price,
            )

        Notification.objects.create(
            user=request.user,
            message=f"Your order #{item.product.name} has been placed succesfully."
        )    

    if payment_method == "COD":
        order.status = "confirmed"
        order.payment_status = "PENDING"
        order.save()

        Cart.objects.filter(user=request.user).delete()
        request.session.pop("buy_now_product_id", None)

        return render(request, "paymentsuccess.html")

    elif payment_method == "STRIPE":

        session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[{
                "price_data": {
                    "currency": "inr",
                    "product_data": {"name": f"Order #{order.id}"},
                    "unit_amount": int(total * 100),
                },
                "quantity": 1,
            }],
            mode="payment",
            success_url="http://127.0.0.1:8000/paymentsuccess/?session_id={CHECKOUT_SESSION_ID}",
            cancel_url="http://127.0.0.1:8000/paymentfailed/",
        )

        order.stripe_session_id = session.id
        order.save()

        return redirect(session.url)

    return redirect("checkout")






login_required
def payment_success(request):

    session_id= request.GET.get("session_id")

    if not session_id:
        return redirect('home')
    
    try:
        order = Order.objects.get(stripe_session_id=session_id,user=request.user)

    except Order.DoesNotExist:
        return redirect('home')

    order.payment_status="PAID"
    order.status="confirmed"
    order.save()

    Cart.objects.filter(user=request.user).delete()
    request.session.pop("address_id",None)

    return render(request,'paymentsuccess.html',{
    'order':order})    

@login_required
def payment_failed(request):
    return render(request, "paymentfailed.html")    


staff_member_required
def orderdetails(request,order_id):
    order=get_object_or_404(Order.objects.prefetch_related('items__product'),id=order_id, user=request.user)
    return render(request,'orderdetails.html',{'order':order})


def review_rating(request,order_id):
    order=get_object_or_404(Order,id=order_id,user=request.user)

    if order.status !="delivered":
        messages.error(request,"You can review only delivered orders.")
        return redirect('order')
    
    if request.method =="POST":
        rating = request.POST.get('rating')
        review_text = request.POST.get('review_text')

        for item in order.items.all():
            ReviewRating.objects.update_or_create(
                user=request.user,
                product=item.product,
                defaults={
                    'rating':rating,
                    'review':review_text,
                }
            )
        Notification.objects.create(
            user=request.user,
            message=f"Your review for order #{item.product.name} was submitted sucessfully."
        )    

        messages.success(request,"Review submitted successfully.")
        return redirect('order')
    return redirect('order')


def delete_review(request,review_id):
    review=get_object_or_404(ReviewRating,id=review_id,user=request.user)
    review.delete()

    messages.success(request,'review deleted successfully')

    return redirect('order')

@login_required
def notifications(request):
    notifications=Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request,'notifications.html',{'notifications':notifications})

  