from django.contrib import admin
from . models import Book,BookImage,Order,Profile
# Register your models here.

class BookAdmin(admin.ModelAdmin):
    list_display = ('seller', 'bookname', 'booktype' , 'total','status')

class OrderAdmin(admin.ModelAdmin):
    list_display = ('orderid','email','city','amount','status')

admin.site.register(Book , BookAdmin)
admin.site.register(BookImage)
admin.site.register(Order, OrderAdmin)
admin.site.register(Profile)