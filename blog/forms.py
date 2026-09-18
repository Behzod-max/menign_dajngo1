from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Post, Profil


class PostForma(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['sarlavha', 'matn', 'rasm']
        widgets = {
            'sarlavha': forms.TextInput(attrs={
                'class': 'forma-input',
                'placeholder': 'Post sarlavhasini kiriting...',
            }),
            'matn': forms.Textarea(attrs={
                'class': 'forma-textarea',
                'placeholder': 'Post matnini yozing...',
                'rows': 10,
            }),
            'rasm': forms.FileInput(attrs={'class': 'forma-file'}),
        }
        labels = {
            'sarlavha': 'Sarlavha',
            'matn': 'Post matni',
            'rasm': 'Rasm (ixtiyoriy)',
        }


class RoyxatdanOtishForma(UserCreationForm):
    email = forms.EmailField(required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class FoydalanuvchiYangilashForma(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']
        labels = {
            'username': 'Foydalanuvchi nomi',
            'email': 'Email',
            'first_name': 'Ism',
            'last_name': 'Familiya',
        }

class ProfilYangilashForma(forms.ModelForm):
    class Meta:
        model = Profil
        fields = ['rasm', 'bio', 'tugilgan_sana', 'manzil']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 4}),
            'tugilgan_sana': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'rasm': '📷 Profil Rasmi',
            'bio': '📝 Bio (o\'zingiz haqingizda)',
            'tugilgan_sana': '🎂 Tug\'ilgan Sana',
            'manzil': '📍 Manzil',
        }