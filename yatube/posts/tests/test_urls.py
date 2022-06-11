from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

POST_INDEX = 'posts:index'
POST_LIST_GROUP = 'posts:group_list'
POST_PROFILE = 'posts:profile'
POST_DETAIL = 'posts:post_detail'
POST_CREATE = 'posts:post_create'
POST_EDIT = 'posts:post_edit'


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user_has_a_post = User.objects.create_user(username='user1')
        cls.user_has_no_posts = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user_has_a_post,
            text='Тестовый пост',
        )

        cls.url_objects = (
            reverse(POST_INDEX),
            reverse(POST_LIST_GROUP, kwargs={'slug': cls.group.slug}),
            reverse(POST_PROFILE, kwargs={'username': cls.user_has_a_post}),
            reverse(POST_DETAIL, kwargs={'post_id': cls.post.pk}),
        )

        cls.url_objects_authorized = (
            reverse(POST_CREATE),
        )

        cls.url_objects_author = (
            reverse(POST_EDIT, kwargs={'post_id': cls.post.pk}),
        )

        cls.urls_with_templates = {
            reverse(POST_INDEX): 'posts/index.html',
            reverse(
                POST_LIST_GROUP,
                kwargs={'slug': cls.group.slug}
            ): 'posts/group_list.html',
            reverse(
                POST_PROFILE,
                kwargs={'username': cls.user_has_a_post}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL,
                kwargs={'post_id': cls.post.pk}
            ): 'posts/post_detail.html',
            reverse(POST_CREATE): 'posts/create_post.html',
            reverse(
                POST_EDIT,
                kwargs={'post_id': cls.post.pk}
            ): 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(StaticURLTests.user_has_no_posts)

        self.client_with_a_post = Client()
        self.client_with_a_post.force_login(StaticURLTests.user_has_a_post)

    def test_urls_accessibility_for_all(self):
        '''Проверяем доступность страниц неавторизованным пользователям'''
        for path in self.url_objects:
            with self.subTest(path=path):
                response = self.guest_client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_accessibility_for_authorized(self):
        '''Проверяем, что некоторые страницы доступны
        только авторизованным пользователям
        '''
        redirect_path = ''.join((
            reverse('users:login'),
            '?next=',
            reverse(POST_CREATE),
        ))

        for path in self.url_objects:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)
        for path in self.url_objects_authorized:
            with self.subTest(path=path):
                response = self.authorized_client.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.guest_client.get(path)
                self.assertRedirects(
                    response,
                    redirect_path,
                    HTTPStatus.FOUND
                )

    def test_urls_accessibility_only_for_author(self):
        '''
        Проверяем, что страница редактирования поста доступна только автору
        '''
        for path in self.url_objects_author:
            with self.subTest(path=path):
                response = self.client_with_a_post.get(path)
                self.assertEqual(response.status_code, HTTPStatus.OK)
                response = self.authorized_client.get(path)
                redirect_path = reverse(
                    POST_DETAIL,
                    kwargs={'post_id': self.post.id}
                )
                self.assertRedirects(response, redirect_path, HTTPStatus.FOUND)

    def test_correct_templates(self):
        '''Проверяем, что шаблоны соответсвуют своим URL'ам'''
        for path, template in self.urls_with_templates.items():
            with self.subTest(path=path):
                response = self.client_with_a_post.get(path)
                self.assertTemplateUsed(response, template)
