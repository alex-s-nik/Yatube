import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Group, Post, User

POST_CREATE = 'posts:post_create'
POST_DETAIL = 'posts:post_detail'
POST_EDIT = 'posts:post_edit'
PROFILE = 'posts:profile'

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


class TaskCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='user1')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание'
        )
        cls.first_post = Post.objects.create(
            text='Тестовый первый пост',
            author=cls.user,
            group=cls.group
        )
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

    def setUp(self):
        self.client = Client()
        self.client.force_login(self.user)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_create_post(self):
        '''Проверяем, что пост создается из формы'''
        post_count_before_edit = Post.objects.count()

        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'image': self.uploaded,
        }

        response = self.client.post(
            reverse(POST_CREATE),
            data=form_data,
            follow=True
        )

        self.assertTrue(
            Post.objects.filter(
                text='Текст из формы',
            ).exists()
        )
        self.assertEqual(Post.objects.count(), post_count_before_edit + 1)
        test_post = Post.objects.first()
        self.assertEqual(test_post.text, 'Текст из формы')
        self.assertEqual(test_post.group.id, self.group.id)
        self.assertEqual(test_post.author, self.user)
        self.assertTrue(str(test_post.image).startswith('posts/small'))
        self.assertRedirects(
            response,
            reverse(PROFILE, kwargs={'username': self.user.username}),
            HTTPStatus.FOUND
        )

    def test_edit_post(self):
        '''Проверяем, что пост редактируется'''
        post_count_before_edit = Post.objects.count()

        form_data = {
            'text': 'Измененный текст из формы',
            'group': self.group.id,
        }
        response = self.client.post(
            reverse(POST_EDIT, kwargs={'post_id': self.first_post.id}),
            data=form_data
        )

        post_count_after_edit = Post.objects.count()
        edited_post = Post.objects.get(id=self.first_post.id)

        self.assertTrue(
            Post.objects.filter(
                text='Измененный текст из формы'
            ).exists()
        )
        self.assertEqual(post_count_after_edit, post_count_before_edit)
        self.assertEqual(edited_post.group.id, self.group.id)
        self.assertEqual(edited_post.author, self.user)
        self.assertRedirects(
            response,
            reverse(POST_DETAIL, kwargs={'post_id': self.first_post.id}),
            HTTPStatus.FOUND
        )
