from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Order
from django.conf import settings
import threading
import smtplib
from email.message import EmailMessage

def send_admin_email_worker(subject, message):
    try:
        msg = EmailMessage()
        msg.set_content(message)
        msg['Subject'] = subject
        msg['From'] = settings.EMAIL_HOST_USER  # Must match login exactly!
        msg['To'] = settings.ADMIN_EMAIL
        
        # Set local_hostname='localhost' to prevent Gmail from dropping invalid Windows hostnames (like ????.mshome.net)
        server = smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT, local_hostname='localhost', timeout=10)
        server.login(settings.EMAIL_HOST_USER, settings.EMAIL_HOST_PASSWORD)
        server.send_message(msg)
        server.quit()
    except Exception as e:
        print(f"Failed to send email: {e}")

def send_admin_email(subject, message):
    # Running in a separate thread so the checkout/registration page resolves quickly
    threading.Thread(target=send_admin_email_worker, args=(subject, message)).start()

@receiver(post_save, sender=User)
def notify_admin_new_user(sender, instance, created, **kwargs):
    if created:
        subject = "New Store Customer! 🥳"
        name = f"{instance.first_name} {instance.last_name}".strip() or instance.username
        message = f"A new customer just registered their account.\n\nName: {name}\nEmail: {instance.email}"
        send_admin_email(subject, message)

@receiver(post_save, sender=Order)
def notify_admin_new_order(sender, instance, created, **kwargs):
    if created:
        subject = f"New Order #{instance.id} Placed! 💰"
        message = f"You received a new order for ₹{instance.total_amount}!\n\nCustomer: {instance.full_name}\nEmail: {instance.email}\nPhone: {instance.phone}\n\nLog in to the admin dashboard to view the products and arrange shipping."
        send_admin_email(subject, message)
