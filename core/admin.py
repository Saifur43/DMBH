from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Product, Inquiry, SampleRequest, Order, ProductImage, OrderItem
from django.utils.html import format_html

# Customize User Admin to show roles
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'phone_number', 'role', 'is_staff')
    list_filter = ('role', 'is_staff', 'is_active')
    fieldsets = UserAdmin.fieldsets + (
        ('Role', {'fields': ('role', 'phone_number')}),
    )

admin.site.register(User, CustomUserAdmin)

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    inlines = [ProductImageInline]
    list_display = ('code', 'style_name', 'category', 'target_price', 'is_active', 'image_preview')
    list_filter = ('category', 'is_active')
    search_fields = ('code', 'style_name')

    def image_preview(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width: 50px; height: auto;" />', obj.main_image.url)
        return "No Image"

@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'requested_quantity', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('product__style_name', 'buyer__username')
    readonly_fields = ('buyer', 'product', 'requested_quantity', 'target_price', 'message')
    
    actions = ['mark_as_closed']

    def mark_as_closed(self, request, queryset):
        queryset.update(status='Closed')
    mark_as_closed.short_description = "Mark selected inquiries as Closed"

@admin.register(SampleRequest)
class SampleRequestAdmin(admin.ModelAdmin):
    list_display = ('product', 'buyer', 'sample_type', 'status', 'request_date')
    list_filter = ('status', 'request_date')
    actions = ['approve_sample', 'mark_sent']

    def approve_sample(self, request, queryset):
        queryset.update(status='Approved')
    
    def mark_sent(self, request, queryset):
        queryset.update(status='Sent')

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('total_price',)

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'buyer', 'total_items', 'total_amount', 'status', 'created_at')
    list_filter = ('status', 'created_at')
    search_fields = ('order_number', 'buyer__username')
    inlines = [OrderItemInline]

admin.site.site_header = "DMBH Management System"
admin.site.site_title = "DMBH Admin"
admin.site.index_title = "Welcome to DMBH Dashboard"
