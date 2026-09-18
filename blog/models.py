from django.db import models
from django.contrib.auth.models import User
from PIL import Image
class Post(models.Model):
    KATEGORIYA_TANLOVLARI = [
        ('texnologiya', 'Texnologiya'),
        ('hayot', 'Hayot'),
        ('sport', 'Sport'),
    ]

    sarlavha = models.CharField(max_length=200)
    matn = models.TextField()
    muallif = models.ForeignKey(User, on_delete=models.CASCADE)
    rasm = models.ImageField(upload_to='postlar/', blank=True, null=True)  # YANGI!
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)
    yangilangan_sana = models.DateTimeField(auto_now=True)
    kategoriya = models.CharField(
        max_length=50,
        choices=KATEGORIYA_TANLOVLARI,
        default='texnologiya',
    )
    nashr_etilgan = models.BooleanField(default=True)
    korildi = models.IntegerField(default=0)

    def __str__(self):
        return self.sarlavha

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.rasm and self.rasm.storage.exists(self.rasm.name):
            with Image.open(self.rasm.path) as img:
                if img.height > 800 or img.width > 800:
                    img.thumbnail((800, 800))
                    img.save(self.rasm.path)


class Izoh(models.Model):
    ism = models.CharField(max_length=100)
    matn = models.TextField()
    yaratilgan_sana = models.DateTimeField(auto_now_add=True)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='izohlar')


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likelar')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'post'], name='unique_user_post_like'),
        ]



class Profil(models.Model):
    foydalanuvchi = models.OneToOneField(User, on_delete=models.CASCADE)
    rasm = models.ImageField(upload_to='profillar/', default='profillar/default.jpg')
    bio = models.TextField(max_length=500, blank=True)
    tugilgan_sana = models.DateField(null=True, blank=True)
    manzil = models.CharField(max_length=200, blank=True)

    def __str__(self):
        return f"{self.foydalanuvchi.username} profili"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        if self.rasm and self.rasm.storage.exists(self.rasm.name):
            with Image.open(self.rasm.path) as img:
                if img.height > 300 or img.width > 300:
                    img.thumbnail((300, 300))
                    img.save(self.rasm.path)