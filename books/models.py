from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(User , on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True, null=True)
    street = models.CharField(max_length=255, blank=True, null=True)
    city = models.CharField(max_length=255, blank=True, null=True)
    state = models.CharField(max_length=255, blank=True, null=True)
    pincode = models.CharField(max_length=10, blank=True, null=True)
    isverified = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

def createProfile(sender,instance,created,**kwargs):
    if created:
        user_profile = Profile(user = instance)
        user_profile.save()

post_save.connect(createProfile,sender = User)


class Book(models.Model):
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    bookname = models.CharField(max_length=255)
    booktype = models.CharField(max_length=255)
    booksubtype = models.CharField(max_length=255)
    bookcondition = models.CharField(max_length=255)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    shipping = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True )
    total = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    moneytopay = models.DecimalField(max_digits=20, decimal_places=2, blank=True, null=True)
    paymentmode = models.CharField(max_length=255)
    city = models.CharField(max_length=255)
    mobile = models.CharField(max_length=13)
    privatenumber = models.BooleanField(default=False)
    uploaded = models.DateTimeField(auto_now_add=True)
    bookpics = models.ManyToManyField('BookImage')
    status = models.CharField(max_length=50, default="available")

    def save(self, *args, **kwargs):
        if(self.shipping == '' ):
            self.shipping = 0;
        totalamount = int(self.price) + int(self.shipping)
        self.total = totalamount
        self.moneytopay = totalamount - (totalamount * 0.1)
        super().save(*args, **kwargs)

class BookImage(models.Model):
    file = models.FileField(upload_to="book_pics/",null=True)
    seller = models.ForeignKey(User, on_delete=models.CASCADE)
    bookid = models.ForeignKey(Book, on_delete=models.CASCADE)

class Order(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    buyer = models.ForeignKey(User, on_delete=models.CASCADE)
    orderid = models.CharField(max_length=255)
    amount = models.IntegerField()
    status = models.CharField(max_length=10, blank=True)
    payment_id = models.CharField(max_length=255, blank=True)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
    email = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    address2 = models.CharField(max_length=255 , blank=True, null=True)
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)
    pincode = models.CharField(max_length=255)
    createddate = models.DateTimeField(auto_now_add=True, blank=True, null=True)