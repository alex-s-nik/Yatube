import shutil
import tempfile
from itertools import zip_longest

from django import forms
from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.models import Group, Post, User
from posts.views import POSTS_ON_PAGE

POST_CREATE = 'posts:post_create'
POST_DETAIL = 'posts:post_detail'
POST_EDIT = 'posts:post_edit'
PROFILE = 'posts:profile'
INDEX_PAGE = 'posts:index'
GROUP_LIST = 'posts:group_list'
ADD_COMMENT = 'posts:add_comment'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.user = User.objects.create_user(username='user1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=cls.uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.client = Client()
        self.client.force_login(PostTests.user)

    def _test_post(self, post_object):
        post_text = post_object.text
        post_pubdate = post_object.pub_date
        post_author = post_object.author
        post_image = post_object.image

        self.assertEqual(post_text, 'Тестовый пост')
        self.assertEqual(post_pubdate, self.post.pub_date)
        self.assertEqual(post_author.username, 'user1')
        self.assertEqual(post_image, 'posts/small.gif')

    def _test_post_form(self, response):
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""

        templates_pages_names = {
            reverse(INDEX_PAGE): 'posts/index.html',
            reverse(
                GROUP_LIST,
                kwargs={'slug': 'test_group'}
            ): 'posts/group_list.html',
            reverse(
                PROFILE,
                kwargs={'username': self.user.username}
            ): 'posts/profile.html',
            reverse(
                POST_DETAIL,
                kwargs={'post_id': self.post.id}
            ): 'posts/post_detail.html',
            reverse(
                POST_EDIT,
                kwargs={'post_id': self.post.id}
            ): 'posts/create_post.html',
            reverse(POST_CREATE): 'posts/create_post.html',

        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_correct_context(self, response=None):
        '''Шаблон index сформирован с правильным контекстом.'''
        response = self.client.get(reverse(INDEX_PAGE))
        first_post = response.context['page_obj'][0]
        self._test_post(first_post)

    def test_grouplist_correct(self):
        '''Шаблон group_list сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse(GROUP_LIST, kwargs={'slug': 'test_group'})
        )
        group_object = response.context['group']
        group_title = group_object.title
        group_slug = group_object.slug
        group_description = group_object.description

        self.assertEqual(group_title, 'Тестовая группа')
        self.assertEqual(group_slug, 'test_group')
        self.assertEqual(group_description, 'Тестовое описание')

        first_post_object = response.context['page_obj'][0]
        self._test_post(first_post_object)

    def test_profile_correct(self):
        '''Шаблон profile сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse(PROFILE, kwargs={'username': 'user1'})
        )
        user_object = response.context['profile_user']

        self.assertEqual(user_object.username, 'user1')
        first_post_object = response.context['page_obj'][0]
        self._test_post(first_post_object)

    def test_postdetail_correct(self):
        '''Шаблон post-detail сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse(POST_DETAIL, kwargs={'post_id': self.post.id})
        )
        post_object = response.context['post']
        self._test_post(post_object)

    def test_createpost_correct(self):
        '''Шаблон post_create сформирован с правильным контекстом.'''
        response = self.client.get(reverse(POST_CREATE))
        self._test_post_form(response)

    def test_editpost_correct(self):
        '''Шаблон post_edit сформирован с правильным контекстом.'''
        response = self.client.get(
            reverse(POST_EDIT, kwargs={'post_id': self.post.id})
        )
        self._test_post_form(response)


class PaginatorViewsTest(TestCase):
    POSTS_COUNT = 13

    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user2')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )

        cls.posts = []
        for i in range(cls.POSTS_COUNT):
            text = f'Тестовый пост №{i}'
            post = Post(
                author=cls.user,
                text=text,
                group=cls.group
            )
            cls.posts.append(post)
        Post.objects.bulk_create(cls.posts)

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def _test_first_page_contains_ten_records(self, response):
        self.assertEqual(len(response.context['page_obj']), POSTS_ON_PAGE)

    def _test_second_page_contains_three_records(self, response):
        self.assertEqual(
            len(response.context['page_obj']),
            PaginatorViewsTest.POSTS_COUNT - POSTS_ON_PAGE
        )

    def test_pagination(self):
        '''Проверяе пагинацию в index, group_list и profile'''
        page_objects = {
            'index': reverse(INDEX_PAGE),
            'group_list': reverse(
                GROUP_LIST,
                kwargs={'slug': 'test_group'}
            ),
            'profile': reverse(
                PROFILE,
                kwargs={'username': 'user2'}
            )
        }

        for name, url in page_objects.items():
            with self.subTest(field=name):
                first_page = url
                second_page = first_page + '?page=2'
                self._test_first_page_contains_ten_records(
                    self.client.get(first_page)
                )
                self._test_second_page_contains_three_records(
                    self.client.get(second_page)
                )


class GroupTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user3')

        cls.groups_list = []
        for i in range(2):
            group = Group(
                title=f'Тестовая группа{i}',
                slug=f'test_group{i}',
                description=f'Тестовое описание{i}',
            )
            cls.groups_list.append(group)
        Group.objects.bulk_create(cls.groups_list)

        posts_text = (
            'Тестовый пост1',
            'Тестовый пост2',
            'Пост без группы',
        )
        posts = []
        for text, post_group in zip_longest(posts_text, cls.groups_list):
            post = Post(
                author=cls.user,
                text=text,
                group=post_group
            )
            posts.append(post)
        Post.objects.bulk_create(posts)
        cls.posts_list = Post.objects.all()

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    def test_post_appears_on_index(self):
        '''Проверяем, что пост с группой и без присутствует
        на главной странице
        '''
        response = self.client.get(reverse(INDEX_PAGE))
        posts = response.context.get('page_obj').object_list

        for post in self.posts_list:
            with self.subTest(post=post):
                self.assertIn(post, posts)

    def test_post_appears_on_the_same_group_page(self):
        '''Проверяем, что пост с группой находится на странице
        с выбранной группой, и этот пост не находится
        на странице другой группы
        '''
        for group in self.groups_list:
            with self.subTest(group=group):
                response = self.client.get(
                    reverse(GROUP_LIST, kwargs={'slug': group.slug})
                )
                posts = response.context.get('page_obj').object_list
                for post in self.posts_list:
                    if post.group == group:
                        self.assertIn(post, posts)
                    else:
                        self.assertNotIn(post, posts)

    def test_post_appears_on_profile_page(self):
        '''Проверяем, что посты есть в профайле пользователя'''
        response = self.client.get(
            reverse(PROFILE, kwargs={'username': 'user3'})
        )
        posts = response.context.get('page_obj').object_list

        for post in self.posts_list:
            with self.subTest(post=post):
                self.assertIn(post, posts)


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user4')
        post_text = 'Тестовый пост1'
        cls.post = Post.objects.create(
            author=cls.user,
            text=post_text
        )

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_comment_by_guest(self):
        '''Проверяем, что гость не может комментировать'''
        form_data = {
            'text': 'Тестовый комментарий'
        }
        response = self.guest_client.post(
            reverse(ADD_COMMENT, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

        self.assertNotEqual(response.content.decode(), form_data['text'])

    def test_comment_by_user(self):
        '''Проверяем, что пользователь может комментировать'''
        count_comments_before_commenting = self.post.comments.count()

        form_data = {
            'text': 'Тестовый комментарий'
        }
        self.authorized_client.post(
            reverse(ADD_COMMENT, kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(
            count_comments_before_commenting + 1,
            self.post.comments.count()
        )
