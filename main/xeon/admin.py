from django.contrib import admin
from .models import Product, Category, HeroBanner, Order, OrderItem, NewsletterSubscriber


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'size', 'quantity', 'price']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'original_price', 'stock', 'is_featured', 'is_new', 'created_at']
    list_filter = ['category', 'is_featured', 'is_new']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    list_editable = ['price', 'stock', 'is_featured', 'is_new']
    list_per_page = 20
    actions = ['remove_from_new_drop', 'mark_as_new_drop']
    fieldsets = (
        ('Product Info', {
            'fields': ('name', 'slug', 'category', 'description')
        }),
        ('Pricing & Stock', {
            'fields': ('price', 'original_price', 'stock')
        }),
        ('Media & Sizes', {
            'fields': ('image', 'available_sizes')
        }),
        ('Display Settings', {
            'fields': ('is_featured', 'is_new', 'created_at')
        }),
    )
    readonly_fields = ['updated_at']

    def remove_from_new_drop(self, request, queryset):
        updated = queryset.update(is_new=False)
        self.message_user(request, f"{updated} products successfully moved to the regular collection (removed from Latest Drop).")
    remove_from_new_drop.short_description = "Move selected to regular collection (Unset as New)"

    def mark_as_new_drop(self, request, queryset):
        updated = queryset.update(is_new=True)
        self.message_user(request, f"{updated} products marked as Latest Drop.")
    mark_as_new_drop.short_description = "Mark selected as Latest Drop"


@admin.register(HeroBanner)
class HeroBannerAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'order']
    list_editable = ['is_active', 'order']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'full_name', 'email', 'total_amount', 'status', 'created_at']
    list_filter = ['status']
    search_fields = ['full_name', 'email']
    list_editable = ['status']
    inlines = [OrderItemInline]


@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at']
