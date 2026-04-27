"""
Management command to seed the database with sample products and banners.
Run with: python manage.py seed_data
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from xeon.models import Category, Product, HeroBanner
import os
from django.conf import settings


CATEGORIES = [
    {'name': 'Dresses',   'slug': 'dresses'},
    {'name': 'Co-ords',   'slug': 'co-ords'},
    {'name': 'Kurta Sets','slug': 'kurta-sets'},
    {'name': 'Tops',      'slug': 'tops'},
]

PRODUCTS = [
    {
        'name': 'Belle Floral Midi Dress',
        'slug': 'belle-floral-midi-dress',
        'category': 'Dresses',
        'description': 'A romantic midi dress with a delicate floral print on soft cream fabric. Featuring a flattering A-line silhouette with subtle ruffle hem. Perfect for garden parties, brunch dates, or a day out.',
        'price': 1699,
        'original_price': 2499,
        'image': 'products/product_1.jpg',
        'available_sizes': 'XS,S,M,L,XL',
        'is_new': True,
        'is_featured': True,
        'stock': 50,
    },
    {
        'name': 'Noir Power Co-ord Set',
        'slug': 'noir-power-co-ord-set',
        'category': 'Co-ords',
        'description': 'An elevated black co-ord set featuring a structured blazer and wide-leg trousers. A power dressing essential for the modern woman. Pairs perfectly with heels or loafers.',
        'price': 2899,
        'original_price': None,
        'image': 'products/product_2.jpg',
        'available_sizes': 'S,M,L,XL,XXL',
        'is_new': True,
        'is_featured': True,
        'stock': 35,
    },
    {
        'name': 'Golden Hour Slip Dress',
        'slug': 'golden-hour-slip-dress',
        'category': 'Dresses',
        'description': 'A minimalist beige satin slip dress with a bias cut and spaghetti straps. Effortlessly transitions from day to evening. Layer it over a tee or wear solo with statement jewelry.',
        'price': 1299,
        'original_price': 1799,
        'image': 'products/product_3.jpg',
        'available_sizes': 'XS,S,M,L',
        'is_new': True,
        'is_featured': False,
        'stock': 40,
    },
    {
        'name': 'Sage Linen Shirt Dress',
        'slug': 'sage-linen-shirt-dress',
        'category': 'Dresses',
        'description': 'An oversized sage green linen shirt dress with a belted waist for a polished silhouette. Breathable and effortlessly cool — your summer wardrobe\'s new best friend.',
        'price': 1599,
        'original_price': None,
        'image': 'products/product_4.jpg',
        'available_sizes': 'S,M,L,XL',
        'is_new': True,
        'is_featured': True,
        'stock': 60,
    },
    {
        'name': 'Bordeaux Wrap Dress',
        'slug': 'bordeaux-wrap-dress',
        'category': 'Dresses',
        'description': 'A timeless wrap dress in rich burgundy with a deep V-neck and self-tie waist. Flattering on all body types. Dress it up or down with ease.',
        'price': 1849,
        'original_price': 2299,
        'image': 'products/product_5.jpg',
        'available_sizes': 'XS,S,M,L,XL,XXL',
        'is_new': False,
        'is_featured': False,
        'stock': 45,
    },
    {
        'name': 'Ivory Knit Co-ord',
        'slug': 'ivory-knit-co-ord',
        'category': 'Co-ords',
        'description': 'A cozy-chic ivory knit sweater top paired with wide-leg camel trousers. A versatile set that works for weekend brunches to casual office days.',
        'price': 2499,
        'original_price': None,
        'image': 'products/product_6.jpg',
        'available_sizes': 'S,M,L,XL',
        'is_new': False,
        'is_featured': False,
        'stock': 30,
    },
    {
        'name': 'Azure Bloom Kurta Set',
        'slug': 'azure-bloom-kurta-set',
        'category': 'Kurta Sets',
        'description': 'A pastel blue floral embroidered kurta set with matching palazzo pants. Crafted from premium cotton, this ethnic set is perfect for festive occasions and family gatherings.',
        'price': 2199,
        'original_price': 2999,
        'image': 'products/product_7.jpg',
        'available_sizes': 'S,M,L,XL,XXL',
        'is_new': False,
        'is_featured': False,
        'stock': 55,
    },
    {
        'name': 'Cream Blazer Shorts Set',
        'slug': 'cream-blazer-shorts-set',
        'category': 'Co-ords',
        'description': 'A tailored cream blazer paired with high-waist shorts for a sharp, sophisticated look. The ultimate power suit reimagined. Take it from the boardroom to cocktail hour.',
        'price': 3199,
        'original_price': None,
        'image': 'products/product_8.jpg',
        'available_sizes': 'XS,S,M,L,XL',
        'is_new': False,
        'is_featured': True,
        'stock': 25,
    },
]


class Command(BaseCommand):
    help = 'Seeds the database with categories, products, and hero banners'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE('🌱 Seeding database...'))

        # Categories
        cat_map = {}
        for c in CATEGORIES:
            obj, created = Category.objects.get_or_create(slug=c['slug'], defaults={'name': c['name']})
            cat_map[c['name']] = obj
            if created:
                self.stdout.write(f'  ✓ Category: {obj.name}')

        # Products
        for p in PRODUCTS:
            if Product.objects.filter(slug=p['slug']).exists():
                self.stdout.write(f'  · Skipped (exists): {p["name"]}')
                continue

            prod = Product.objects.create(
                name=p['name'],
                slug=p['slug'],
                category=cat_map.get(p['category']),
                description=p['description'],
                price=p['price'],
                original_price=p.get('original_price'),
                available_sizes=p['available_sizes'],
                is_new=p['is_new'],
                is_featured=p['is_featured'],
                stock=p['stock'],
                image=p['image'],
            )
            self.stdout.write(f'  ✓ Product: {prod.name}')

        # Hero Banner
        if not HeroBanner.objects.exists():
            HeroBanner.objects.create(
                title='Summer in the Making',
                subtitle='New Season — Spring / Summer 2024',
                image='hero/hero_banner.png',
                button_text='SHOP NOW',
                button_link='/collection/',
                is_active=True,
                order=0,
            )
            self.stdout.write('  ✓ Hero Banner created')

        self.stdout.write(self.style.SUCCESS('\n✅ Database seeded successfully!'))
        self.stdout.write(self.style.NOTICE('   Run: python manage.py runserver 8000'))
