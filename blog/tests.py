from django.contrib.auth.models import User
from django.test import Client, TestCase
from django.urls import reverse

from .forms import PostForma
from .models import Post


class PostModelTest(TestCase):
    """Post modeli testlari"""

    def setUp(self):
        self.user = User.objects.create_user(
            username='test_user',
            password='test_parol123',
        )
        self.post = Post.objects.create(
            sarlavha='Test Post',
            matn='Bu test uchun post',
            muallif=self.user,
            nashr_etilgan=True,
        )

    def test_post_yaratildi(self):
        self.assertEqual(self.post.sarlavha, 'Test Post')
        self.assertEqual(self.post.muallif.username, 'test_user')
        self.assertTrue(self.post.nashr_etilgan)

    def test_post_str(self):
        self.assertEqual(str(self.post), 'Test Post')

    def test_post_soni(self):
        self.assertEqual(Post.objects.count(), 1)


class BoshSahifaTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='test_user',
            password='test_parol123',
        )

        for i in range(5):
            Post.objects.create(
                sarlavha=f'Post {i + 1}',
                matn=f'Bu {i + 1}-post matni',
                muallif=self.user,
                nashr_etilgan=True,
            )

    def test_bosh_sahifa_ochiladi(self):
        response = self.client.get(reverse('bosh_sahifa'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'blog/bosh.html')

    def test_postlar_korsatiladi(self):
        response = self.client.get(reverse('bosh_sahifa'))
        self.assertEqual(len(response.context['postlar']), 5)
        self.assertContains(response, 'Post 1')
        self.assertContains(response, 'Post 5')

    def test_nashr_etilmaganlar_korinmaydi(self):
        Post.objects.create(
            sarlavha='Post nashr etilmagan',
            matn='Bu post nashr etilmagan',
            muallif=self.user,
            nashr_etilgan=False,
        )
        response = self.client.get(reverse('bosh_sahifa'))
        self.assertNotContains(response, 'Post nashr etilmagan')


class PostFormaTest(TestCase):
    def test_forma_togri_maydonlar(self):
        forma = PostForma()
        self.assertIn('sarlavha', forma.fields)
        self.assertIn('matn', forma.fields)

    def test_forma_togri_malumot(self):
        forma = PostForma(data={
            'sarlavha': 'Test sarlavha',
            'matn': 'Test matn',
        })
        self.assertTrue(forma.is_valid())

    def test_forma_bosh_sarlavha(self):
        forma = PostForma(data={
            'sarlavha': '',
            'matn': 'Test matn',
        })
        self.assertFalse(forma.is_valid())
        self.assertIn('sarlavha', forma.errors)

    def test_forma_uzun_sarlavha(self):
        forma = PostForma(data={
            'sarlavha': 'a' * 201,
            'matn': 'Test matn',
        })
        self.assertFalse(forma.is_valid())