from django.shortcuts import get_object_or_404, render, redirect
from django.contrib import messages
from django.views import View
from django.contrib.auth.decorators import login_required
from django.conf import settings
from .models import Order, OrderItem, Payment
from courses.models import Course, EnrolledCourse

from django.utils import timezone
from django.urls import reverse

import decimal
import stripe

stripe.api_key = settings.STRIPE_SECRET_KEY


def order(request):
    order_qs= Order.objects.filter(user=request.user, ordered=False)
    order = None
    if order_qs.exists():
        order = order_qs.first()
    
    context = {
        'order': order
    }

    return render(request, 'cart/cart.html', context)


@login_required
def add_to_cart(request, slug):
    course = get_object_or_404(Course, slug=slug)
    order_item, created = OrderItem.objects.get_or_create(user=request.user, item=course)

    if order_item:
        order_qs= Order.objects.filter(user=request.user, ordered=False)
        if order_qs.exists():
            order = order_qs.first()
        else:
            order = Order.objects.create(user=request.user, ordered=False, ordered_date=timezone.now())
        
        if order.items.filter(item__slug=order_item.item.slug).exists():
            messages.info(request, "This course is Exist in you Cart")
            return redirect(reverse('courses:detail', kwargs={'slug': slug}))
        else:
            order.items.add(order_item)
            order.ordered_date = timezone.now()
            order.save()

        messages.success(request, f'{order_item.item.title} successfully Added to the Cart.')
        return redirect(reverse('courses:detail', kwargs={'slug': slug}))


@login_required
def remove_from_cart(request, slug):
    item = get_object_or_404(Course, slug=slug)
    order_qs = Order.objects.filter(
        user=request.user,
        ordered=False
    )
    if order_qs.exists():
        order = order_qs[0]
        # check if the order item is in the order
        if order.items.filter(item__slug=item.slug).exists():
            order_item = OrderItem.objects.filter(
                item=item,
                user=request.user,
                ordered=False
            )[0]
            order.items.remove(order_item)
            messages.info(request, "This item was removed from your cart.")
            return redirect(reverse('cart:order'))
        else:
            messages.info(request, "This item was not in your cart")
            return redirect(reverse('cart:order'))
    else:
        messages.info(request, "You do not have an active order")
        return redirect(reverse('cart:order'))
    

class PaymentView(View):
    def get(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        context = {
            'order': order,
            'pub_key': settings.STRIBE_PUB_KEY
        }
        return render(self.request, "cart/payment.html", context)

    def post(self, *args, **kwargs):
        order = Order.objects.get(user=self.request.user, ordered=False)
        token = self.request.POST.get('stripeToken')
        total = order.get_total
        amount = round(decimal.Decimal(total * 100))


        charge = stripe.Charge.create(
            amount=amount,  # cents
            currency="usd",
            source=token
        )

        # create the payment
        payment = Payment()
        payment.stripe_charge_id = charge['id']
        payment.user = self.request.user
        payment.amount = order.get_total
        payment.save()

        enrolled = EnrolledCourse()
        enrolled.user = self.request.user
        enrolled.save()
        for course in order.items.all():
            enrolled.courses.add(course.item)
            enrolled.save()

        # assign the payment to the order
        order.ordered = True
        order.payment = payment
        order.save()

        messages.success(self.request, "Your order was successful!")
        return redirect("/")

        # except stripe.error.CardError as e:
        #     body = e.json_body
        #     err = body.get('error', {})
        #     messages.error(self.request, f"{err.get('message')}")
        #     return redirect("/")

        # except stripe.error.RateLimitError as e:
        #     # Too many requests made to the API too quickly
        #     messages.error(self.request, "Rate limit error")
        #     return redirect("/")

        # except stripe.error.InvalidRequestError as e:
        #     # Invalid parameters were supplied to Stripe's API
        #     messages.error(self.request, "Invalid parameters")
        #     return redirect("/")

        # except stripe.error.AuthenticationError as e:
        #     # Authentication with Stripe's API failed
        #     # (maybe you changed API keys recently)
        #     messages.error(self.request, "Not authenticated")
        #     return redirect("/")

        # except stripe.error.APIConnectionError as e:
        #     # Network communication with Stripe failed
        #     messages.error(self.request, "Network error")
        #     return redirect("/")

        # except stripe.error.StripeError as e:
        #     # Display a very generic error to the user, and maybe send
        #     # yourself an email
        #     messages.error(
        #         self.request, "Something went wrong. You were not charged. Please try again.")
        #     return redirect("/")

        # except Exception as e:
        #     # send an email to ourselves
        #     messages.error(
        #         self.request, "A serious error occurred. We have been notifed.")
        #     return redirect("/")