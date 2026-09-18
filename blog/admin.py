from django.contrib import admin
from django.db.models import QuerySet
from .models import Like, Post, Izoh, Profil

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('sarlavha', 'muallif', 'yaratilgan_sana', 'nashr_etilgan', 'korildi')
    list_filter = ('nashr_etilgan', 'yaratilgan_sana', 'muallif')
    search_fields = ('sarlavha', 'matn')
    date_hierarchy = 'yaratilgan_sana'
    ordering = ('-yaratilgan_sana',)
    list_per_page = 20
    fieldsets = (
        ('Asosiy Malumotlar', {
            'fields': ('sarlavha', 'matn', 'muallif', 'kategoriya'),
        }),
        ('Qoshimcha', {
            'fields': ('rasm', 'nashr_etilgan'),
            'classes': ('collapse',),
        }),
        ('Statistika', {
            'fields': ('korildi', 'yaratilgan_sana', 'yangilangan_sana'),
            'classes': ('collapse',),
        }),
    )
    readonly_fields = ('yaratilgan_sana', 'yangilangan_sana', 'korildi')

    def get_queryset(self, request) -> QuerySet:
        return super().get_queryset(request).select_related('muallif')

@admin.register(Izoh)
class IzohAdmin(admin.ModelAdmin):
    list_display = ('post', 'ism', 'yaratilgan_sana')
    list_filter = ('yaratilgan_sana',)
    search_fields = ('matn', 'ism', 'post__sarlavha')

@admin.register(Profil)
class ProfilAdmin(admin.ModelAdmin):
    list_display = ('foydalanuvchi', 'manzil', 'tugilgan_sana')
    search_fields = ('foydalanuvchi__username', 'bio')
    list_filter = ('tugilgan_sana',)


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('user', 'post')
    list_filter = ('post',)
    search_fields = ('user__username', 'post__sarlavha')