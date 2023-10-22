from django.shortcuts import render , redirect , get_object_or_404
from django.http import JsonResponse
from . import models
from django.contrib import messages
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate,login,logout,get_user_model
from django.contrib.auth.models import User
from . import keys,forms
from django.contrib.auth.views import PasswordResetView, PasswordResetConfirmView
from django.urls import reverse_lazy

def home(request):
    allbooks = models.Book.objects.filter(status = 'available').order_by("-uploaded")[:10]
    return render(request, "index.html",{'allbooks':allbooks})

def get_book_subtype(request):
    selected_value = request.GET.get('selected_value')
    options = {
        'General': ['Fiction','Non-fiction','Mystery/Thriller','Science Fiction','Fantasy','Biography/Autobiography','History','Self-Help','Romance','Young Adult','Poetry','Science','Business','Travel','Art','Philosophy','Religion/Spirituality','Psychology','Health/Fitness','Cookbooks','Others'],
        'Engineering Books': ['Computer Science and Engineering','Civil Engineering','Mechanical Engineering','Electrical Engineering','Chemical Engineering','Aerospace Engineering','Environmental Engineering','Industrial Engineering','Materials Science and Engineering','Structural Engineering','Petroleum Engineering','Biomedical Engineering','Geotechnical Engineering','Control Systems Engineering','Robotics and Automation Engineering','Water Resources Engineering','Transportation Engineering','Renewable Energy Engineering','Engineering Mathematics','Engineering Ethics and Professionalism','Others'],
        'School Books': ['Science','Mathematics','English','Social Studies','History','Geography','Language Arts','Literature','Physics','Chemistry','Biology','Computer Science','Environmental Science','Economics','Others'],
        'Others': ['Others'],    
    }
    dependent_options = options.get(selected_value, [])
    return JsonResponse({'options': dependent_options})

def sell(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            bookname = request.POST['bookname']
            booktype = request.POST['booktype']
            booksubtype = request.POST['booksubtype']
            bookcondition = request.POST['bookcondition']
            bookpics = request.FILES.getlist('bookpics')
            price = request.POST['price']
            shipping = request.POST['shipping']
            paymentmode = request.POST['paymentmode']
            city = request.POST['city']
            mobile = request.POST['mobile']
            try:
                privatenumber = bool(request.POST['privatenumber'])
            except:
                privatenumber = False
                
            if bookname and booktype and booksubtype and bookcondition and price and paymentmode and city and mobile:
                if bookpics:
                    bookid = models.Book.objects.create(seller=request.user,bookname=bookname,booktype=booktype,
                                            booksubtype=booksubtype,bookcondition=bookcondition,
                                            price=price,shipping=shipping,paymentmode=paymentmode,city=city,mobile=mobile
                                            ,privatenumber=privatenumber)
                    for pic in bookpics:
                        image = models.BookImage.objects.create(file=pic,seller=request.user,bookid=bookid)
                        bookid.bookpics.add(image)

                    messages.success(request, 'Book Uploaded successfully!')
                    return redirect('book',bookid.id)
                    
                else:
                    messages.error(request, 'Please upload your book pictures!')
                    return render(request, "sell.html", {'bookname':bookname,'booktype':booktype,
                                        'booksubtype':booksubtype,'bookcondition':bookcondition,
                                        'price':price,'shipping':shipping,'paymentmode':paymentmode,'city':city,
                                        'mobile':mobile ,'privatenumber':privatenumber})
            else:
                messages.error(request, 'Please fill all required details!')
                return render(request, "sell.html", {'bookname':bookname,'booktype':booktype,
                                        'booksubtype':booksubtype,'bookcondition':bookcondition,
                                        'price':price,'shipping':shipping,'paymentmode':paymentmode,'city':city,
                                        'mobile':mobile ,'privatenumber':privatenumber})
    
        return render(request, "sell.html", {})
    else:
        messages.success(request, 'Sign in to get started with selling your books!')
        return redirect('login')
    

def books(request):
    allbooks = models.Book.objects.filter(status = 'available').order_by("-uploaded")
    return render(request, "books.html", {'allbooks':allbooks})

def book(request, bookid):
    mybook = get_object_or_404(models.Book, id = bookid)
    return render(request, "book.html", {'mybook':mybook})
    

razorpay_client = razorpay.Client(auth=(keys.RAZOR_KEY_ID, keys.RAZOR_KEY_SECRET))
def checkout(request, bookid):
    if request.user.is_authenticated:
        mybook = get_object_or_404(models.Book, id = bookid, status = 'available')
        
        amount = int(mybook.total) * 100  # Amount in paise
        payment_data = {
            'amount': amount,
            'currency': 'INR',
            'notes': {
                'email': 'admin@bookhub.com',#
            },
        }
        order = razorpay_client.order.create(data=payment_data)
        context = {
            'order_id': order['id'],
            'razorpay_merchant_key': keys.RAZOR_KEY_ID,
            'amount': amount,
            'mybook':mybook,
        }

        return render(request, "checkout.html", context)
    else:
        messages.success(request, 'Sign in to explore and purchase books!')
        return redirect('login')

def shippingdetails(request):
    if request.method == "POST":
        orderid = request.POST['hiddenorderid']
        bookid = request.POST['hiddenbook']
        firstName = request.POST['firstName']
        lastName = request.POST['lastName']
        email = request.POST['email']
        address = request.POST['address']
        address2 = request.POST['address2']
        city = request.POST['city']
        state = request.POST['state']
        pincode = request.POST['pincode']
        
        mybook = get_object_or_404(models.Book, id=bookid)
        models.Order.objects.create(orderid = orderid, buyer = request.user, amount = int(mybook.total) , book = mybook,
                                    firstName=firstName,lastName=lastName,
                                    email=email,address=address,address2=address2, 
                                    city=city,state=state,pincode=pincode )

        return JsonResponse({'status': mybook})


@csrf_exempt
def paymenthandler(request):
    if request.method == "POST":
        try:
            payment_id = request.POST.get('razorpay_payment_id', '')
            razorpay_order_id = request.POST.get('razorpay_order_id', '')
            signature = request.POST.get('razorpay_signature', '')
            params_dict = {
                'razorpay_order_id': razorpay_order_id,
                'razorpay_payment_id': payment_id,
                'razorpay_signature': signature
            }
            result = razorpay_client.utility.verify_payment_signature(params_dict)
            if result is not None:
                payment = razorpay_client.payment.fetch(payment_id)
                if payment.get('status') == 'captured':
                    myorder = get_object_or_404(models.Order, orderid=razorpay_order_id)
                    myorder.status = 'captured'
                    myorder.payment_id = payment_id
                    myorder.save()
                
                    book = get_object_or_404(models.Book, id=myorder.book.id)
                    book.status = 'sold'
                    book.save()

                    return render(request, 'payment.html',{'status':'success'})
                else:
                    return render(request, 'payment.html',{'status':'fail'})
            else:
                return render(request, 'payment.html',{'status':'fail'})
        except Exception as e:
            return render(request, 'payment.html',{'status':e})
            return redirect('home')
    else:
        return redirect('home')
    
def myorders(request):
    if request.user.is_authenticated:
        orders = models.Order.objects.filter( buyer = request.user ).order_by("-createddate")
        return render(request, 'orders.html',{'orders':orders})
    else:
        return redirect('home')
    
def loginuser(request):
    form = forms.RegisterForm()
    if request.method == "POST":
        username = request.POST['loginemail']
        password = request.POST['loginpassword']
        user = authenticate(request,username=username,password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'Invalid username or password!')
            return render(request, 'login.html', {'form': form})
    else:
        return render(request, 'login.html', {'form': form})

def logoutuser(request):
    logout(request)
    return redirect('home')

def registeruser(request):
    form = forms.RegisterForm()
    if request.method == "POST":
        form = forms.RegisterForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password1 = form.cleaned_data['password1']
            first_name = form.cleaned_data['first_name']
            user = get_user_model().objects.create_user(username=username, email=username, password=password1)
            user.first_name = first_name
            user.save()
            user = authenticate(request,username=username,password=password1)
            login(request, user)
            return redirect('home')
        else:
            return render(request, 'register.html', {'form': form})
    else:
        return render(request, 'register.html', {'form': form})
    
def profile(request):
    userprofile = models.Profile.objects.get(user = request.user)

    return render(request, 'profile.html', {'profile':userprofile})

def editprofile(request):
    userprofile = models.Profile.objects.get(user = request.user)
    if request.method == 'POST':
        fullname = request.POST['fullname']
        username = request.POST['username']
        phone = request.POST['phone']
        street = request.POST['street']
        state = request.POST['state']
        city = request.POST['city']
        pincode = request.POST['pincode']
         # Update the profile fields
        userprofile.phone = phone
        userprofile.pincode = pincode
        userprofile.street = street
        userprofile.state = state
        userprofile.city = city
        userprofile.save()
        
        if User.objects.exclude(id=request.user.id).filter(username=username).exists():
            messages.error(request, f'{username} is already taken.')
            return redirect('editprofile')
        else:
            user = request.user
            user.username = username
            user.first_name = fullname
            user.save()

            messages.success(request, 'Profile Updated!')
            return redirect('profile')
    else:
        return render(request, 'editprofile.html', {'profile':userprofile})
    
def changepassword(request):
    if request.method == 'POST':
        current_password = request.POST['current_password']
        new_password = request.POST['new_password']
        confirm_new_password = request.POST['confirm_new_password']

        if not request.user.check_password(current_password):
            messages.error(request, 'Incorrect current password.')
            return redirect('changepassword') 

        if new_password != confirm_new_password:
            messages.error(request, 'New password and confirm password do not match.')
            return redirect('changepassword')

        request.user.set_password(new_password)
        request.user.save()

        user = authenticate(request,username=request.user.username,password=new_password)
        login(request, user)

        messages.success(request, 'Password updated successfully!')
        return redirect('profile')
     
    return render(request, 'changepassword.html',{})

def mybooks(request):
    return render(request, 'mybooks.html',{})

class CustomPasswordResetView(PasswordResetView):
    template_name = 'password_reset.html'
    # email_template_name = 'custom_password_reset_email.html'
    success_url = reverse_lazy('password_reset_done')

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'password_reset_change.html'

def password_reset_done(request):
    messages.success(request, 'Check your email for a password reset link and log in.')
    return redirect('login')

def reset_done(request):
    messages.success(request, 'Password reset successful. Log in to explore.')
    return redirect('login')