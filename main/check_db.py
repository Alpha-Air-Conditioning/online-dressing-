import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from xeon.models import Product, HeroBanner

print(f"Products count: {Product.objects.count()}")
print(f"Banners count: {HeroBanner.objects.count()}")

for p in Product.objects.all()[:3]:
    print(f"Product: {p.name}")
    print(f"  Main: {p.image}")
    print(f"  Hover: {p.hover_image}")

for b in HeroBanner.objects.all():
    print(f"Banner: {b.title}")
    print(f"  Main: {b.image}")
    print(f"  Mobile: {b.mobile_image}")
