from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home , name="home"),
    path('sell/', views.sell , name="sell"),
    path('get_book_subtype/', views.get_book_subtype , name="get_book_subtype"),
    path('books/', views.books , name="books"),
    path('books/<int:bookid>', views.book , name="book"),
    path('checkout/<int:bookid>', views.checkout , name="checkout"),
    path('shippingdetails/', views.shippingdetails, name='shippingdetails'),
    path('paymenthandler/', views.paymenthandler, name='paymenthandler'),
    path('myorders/', views.myorders , name="myorders"),
    path('mybooks/', views.mybooks , name="mybooks"),
    path('profile/', views.profile , name="profile"),
    path('editprofile/', views.editprofile , name="editprofile"),
    path('changepassword/', views.changepassword , name="changepassword"),
    path('login/', views.loginuser , name="login"),
    path('logout/', views.logoutuser , name="logout"),
    path('register/', views.registeruser , name="register"),
    path('password_reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password_reset/done/', views.password_reset_done, name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.reset_done, name='password_reset_complete'),
]
