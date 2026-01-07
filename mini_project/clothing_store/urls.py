from django.urls import path
from . import views

urlpatterns = [
    path('',views.home,name='home'),
    path('login/',views.loggin,name='loggin'),
    path('signup/',views.signup,name='signup'),
    path('cart/',views.cart,name='cart'),
    path('wishlist/',views.wishlist,name='wishlist'),
    path('casualfit/',views.casualfit,name='casualfit'),
    path('fashionfit/',views.fashionfit,name='fashionfit'),
    path('innerwear/',views.innerwear,name='innerwear'),
    path('accessories/',views.accessories,name='accessories'),
    path('newarrivals/',views.newarrivals,name='newarrivals'),
    path('forgot/',views.forgot,name='forgot'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('new_password/', views.new_password, name='new_password'),
    path('profile/',views.profile,name='profile'),
    path('profilesetup/',views.profilesetup,name='profilesetup'),
    path('logout/',views.logout,name='logout'),
    path('order/',views.order,name='order'),
    path('adminpanel/',views.adminpanel,name='adminpanel'),
    path('adminproducts/',views.adminproducts,name='adminproducts'),
    path('adminorders/',views.adminorders,name='adminorders'),
    path('adminusers/',views.adminusers,name='adminusers'),
    path('adminusers/<int:user_id>/',views.block_unblock,name='block_unblock'),
    path('showlogin/',views.showlogin,name='showlogin'),
    path('productsedit/<int:id>/', views.productsedit, name='productsedit'),
    path('adminsettings/',views.adminsettings,name='adminsettings'),
    path('addproducts/',views.addproducts,name='addproducts'),
    path('coupons/',views.coupons,name='coupons'),
    path('checkout/',views.checkout,name='checkout'),
    path("payment/",views.payment,name="payment"),
    path('ordersummary/',views.ordersummary,name="ordersummary"),
    path('productsdelete/<int:id>/', views.productsdelete, name='productsdelete'),





]
