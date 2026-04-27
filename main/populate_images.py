import os
import shutil
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'main.settings')
django.setup()

from xeon.models import Product, HeroBanner
from django.conf import settings

# Paths to generated images in artifact dir
ARTIFACT_DIR = r"C:\Users\XeonG\.gemini\antigravity\brain\2ffba295-53c7-420f-ab8f-99a296a52a85"
hero_desktop = os.path.join(ARTIFACT_DIR, "hero_desktop_premium_1777099081413.png")
hero_mobile = os.path.join(ARTIFACT_DIR, "hero_mobile_premium_1777099096198.png")
product_main = os.path.join(ARTIFACT_DIR, "product_main_dress_1777099111198.png")
product_hover = os.path.join(ARTIFACT_DIR, "product_hover_dress_1777099133240.png")

MEDIA_ROOT = settings.MEDIA_ROOT

def copy_and_update():
    # Ensure dirs exist
    os.makedirs(os.path.join(MEDIA_ROOT, 'hero', 'mobile'), exist_ok=True)
    os.makedirs(os.path.join(MEDIA_ROOT, 'products', 'hover'), exist_ok=True)

    # Copy Hero Images to First Banner
    banner = HeroBanner.objects.first()
    if banner:
        shutil.copy(hero_desktop, os.path.join(MEDIA_ROOT, 'hero', 'hero_premium_desktop.png'))
        shutil.copy(hero_mobile, os.path.join(MEDIA_ROOT, 'hero', 'mobile', 'hero_premium_mobile.png'))
        banner.image = 'hero/hero_premium_desktop.png'
        banner.mobile_image = 'hero/mobile/hero_premium_mobile.png'
        banner.save()
        print(f"Updated Banner: {banner.title}")

    # Copy Product Images to First Product
    product = Product.objects.first()
    if product:
        shutil.copy(product_main, os.path.join(MEDIA_ROOT, 'products', 'product_premium_main.png'))
        shutil.copy(product_hover, os.path.join(MEDIA_ROOT, 'products', 'hover', 'product_premium_hover.png'))
        product.image = 'products/product_premium_main.png'
        product.hover_image = 'products/hover/product_premium_hover.png'
        product.save()
        print(f"Updated Product: {product.name}")

if __name__ == "__main__":
    copy_and_update()
