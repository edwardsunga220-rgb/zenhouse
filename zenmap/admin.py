# zenmap/admin.py
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (
    CustomUser,
    MainMap,
    MainMapDetail,
    ContactMessage,
    CustomPlanRequest,
    Article,
    Contact
)

# ----------------------------
# Custom User Admin
# ----------------------------
class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active')
    search_fields = ('email', 'first_name', 'last_name')
    ordering = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'is_active', 'is_staff')}
        ),
    )

# ----------------------------
# MainMap Admin
# ----------------------------
class MainMapDetailInline(admin.TabularInline):
    model = MainMapDetail
    extra = 1

@admin.register(MainMap)
class MainMapAdmin(admin.ModelAdmin):
    list_display = ('title', 'code', 'category', 'style', 'price', 'created_at')
    list_filter = ('category', 'style')
    search_fields = ('title', 'code')
    inlines = [MainMapDetailInline]

# ----------------------------
# Contact Message Admin
# ----------------------------
@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'main_map', 'created_at', 'is_resolved')
    list_filter = ('is_resolved', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    readonly_fields = ('created_at',)

# ----------------------------
# Custom Plan Request Admin
# ----------------------------
@admin.register(CustomPlanRequest)
class CustomPlanRequestAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'submitted_at')
    search_fields = ('full_name', 'email', 'phone')
    readonly_fields = ('submitted_at',)

# ----------------------------
# Article Admin
# ----------------------------
@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ('title', 'uploaded_by', 'uploaded_at', 'views')
    search_fields = ('title', 'description', 'uploaded_by__email')
    readonly_fields = ('uploaded_at', 'views')

# ----------------------------
# Contact Form Admin
# ----------------------------
@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'subject', 'page', 'created_at')
    search_fields = ('name', 'email', 'subject', 'message')
    list_filter = ('page', 'created_at')
    readonly_fields = ('created_at',)

# ----------------------------
# Register CustomUser
# ----------------------------
admin.site.register(CustomUser, CustomUserAdmin)
