from django.test import TestCase

from posts.models import FIRST_POST_CHARS, Group, Post, User

TEST_GROUP_TITLE = 'Тестовая группа'
TEST_POST_TEXT = 'Длинный тестовый текст для проверки'


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title=TEST_GROUP_TITLE,
            slug='test_slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text=TEST_POST_TEXT,
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = self.post
        group = self.group

        str_objects = {
            post: TEST_POST_TEXT[:FIRST_POST_CHARS],
            group: TEST_GROUP_TITLE
        }

        for obj, expected_value in str_objects.items():
            with self.subTest(field=obj):
                self.assertEqual(str(obj), expected_value)
