from django.test import SimpleTestCase
from django.urls import resolve, reverse

from .forms import PostForma


class BlogViewsTests(SimpleTestCase):
    def test_home_url_resolves(self):
        self.assertEqual(reverse('bosh_sahifa'), '/')
        self.assertEqual(resolve('/').func.__name__, 'bosh_sahifa')

    def test_post_form_fields(self):
        self.assertEqual(list(PostForma().fields.keys()), ['sarlavha', 'matn', 'rasm'])
