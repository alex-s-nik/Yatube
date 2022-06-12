from django.test import Client, TestCase
from django.urls import reverse
from django.core.cache import cache

from posts.models import Post, User

INDEX_PAGE = 'posts:index'


class CacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user1')

    def setUp(self):
        self.client = Client()

    def test_index_cache(self):
        '''Проверяем кеширование главной страницы'''
        response0 = self.client.get(reverse(INDEX_PAGE))
        post = Post.objects.create(
            text='Тестовый пост',
            author=self.user,
        )
        response1 = self.client.get(reverse(INDEX_PAGE))
        Post.objects.filter(pk=post.pk).delete()
        response2 = self.client.get(reverse(INDEX_PAGE))
        self.assertEqual(response1.content, response2.content)
        cache.clear()
        response3 = self.client.get(reverse(INDEX_PAGE))
        self.assertEqual(response0.content, response3.content)
