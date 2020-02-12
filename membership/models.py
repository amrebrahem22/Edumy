from django.conf import settings
from django.db import models
from django.db.models.signals import post_save

import stripe
stripe.api_key = settings.STRIPE_SECRET_KEY

User= settings.AUTH_USER_MODEL

MEMBERSHIP_TYPE = [
    ('free', 'Free'),
    ('pro', 'Profissional'),
    ('enterprise', 'Enterprise'),
]

class Membership(models.Model): 
    slug = models.SlugField(null=True, blank=True)
    membership_type = models.CharField(max_length=30, choices=MEMBERSHIP_TYPE, default="Free")
    price = models.CharField(max_length=20) 
    stripe_plan_id = models.CharField(max_length=30)

    def __str__(self):
        return self.membership_type

class UserMembership(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    stripe_customer_id = models.CharField(max_length=30)
    membership_type = models.ForeignKey(Membership, related_name='user_membership_type', on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.user.username

def post_save_usermembership_create(sender, instance, created, *args, **kwargs):
	if created:
		UserMembership.objects.get_or_create(user=instance)

	user_membership, created = UserMembership.objects.get_or_create(user=instance)

	if user_membership.stripe_customer_id is None or user_membership.stripe_customer_id == '':
		new_customer_id = stripe.Customer.create(email=instance.email)
		user_membership.stripe_customer_id = new_customer_id['id']
		# user_membership.membership_type = "Free"
		user_membership.save()

post_save.connect(post_save_usermembership_create, sender=User)

class Subscription(models.Model):
    user_membership = models.ForeignKey(UserMembership, on_delete=models.CASCADE)
    stripe_subscription_id = models.CharField(max_length=30)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.user_membership.user.username
