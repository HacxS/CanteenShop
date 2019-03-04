from django.shortcuts import render
from .models import OrderItem
from .forms import OrderCreateForm
from cart.cart import Cart
from django.utils.translation import get_language
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.conf import settings
from paytm import Checksum

def order_create(request):
    cart = Cart(request)
    
    if request.method == 'POST':
        MERCHANT_KEY = settings.PAYTM_MERCHANT_KEY
        MERCHANT_ID = settings.PAYTM_MERCHANT_ID
        get_lang = "/" + get_language() if get_language() else ''
        CALLBACK_URL = settings.HOST_URL  + settings.PAYTM_CALLBACK_URL
        order_id = Checksum.__id_generator__()
        bill_amount=0
        name = request.POST['name']
        email = request.POST['email']
        mob_no = request.POST['mobno']

        form = OrderCreateForm(request.POST)
        if form.is_valid():
            order = form.save()
            for item in cart:
                OrderItem.objects.create(
                    order=order,
                    product=item['product'],
                    price=item['price'],
                    quantity=item['quantity']
                )
            bill_amount = cart.get_total_price()
            cart.clear()

        if bill_amount:
            data_dict = {
                        'MID':MERCHANT_ID,
                        'ORDER_ID':order_id,
                        'TXN_AMOUNT': bill_amount,
                        'CUST_ID':email,
                        'MOBILE_NO': mob_no,
                        'INDUSTRY_TYPE_ID':'Retail',
                        'WEBSITE': settings.PAYTM_WEBSITE,
                        'CHANNEL_ID':'WEB',
                        'CALLBACK_URL':CALLBACK_URL,#"http://127.0.0.1:8000/paytm/response"
                    }
            param_dict = data_dict
            param_dict['CHECKSUMHASH'] = Checksum.generate_checksum(data_dict, MERCHANT_KEY)
            print(param_dict)
            return render(request,"paytm/payment.html",{'paytmdict':param_dict})
        else:
            return HttpResponse("Bill Amount Could not find. ?bill_amount=10")
    else:
        form = OrderCreateForm()
    return render(request, 'orders/order/create.html', {'form': form})