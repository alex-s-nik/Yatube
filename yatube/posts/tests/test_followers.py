from django.test import Client, TestCase
from django.urls import reverse

from posts.models import Post, User

FOLLOW_INDEX = 'posts:follow_index'
PROFILE_FOLLOW = 'posts:profile_follow'
PROFILE_UNFOLLOW = 'posts:profile_unfollow'


class FollowersTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user1 = User.objects.create_user(username='user1')
        cls.user2 = User.objects.create_user(username='user2')
        cls.user3 = User.objects.create_user(username='user3')

    def setUp(self):
        self.client1 = Client()
        self.client2 = Client()
        self.client3 = Client()
        self.client1.force_login(self.user1)
        self.client2.force_login(self.user2)
        self.client3.force_login(self.user3)

    def _check_followers_band_is_empty(self, client):
        response = client.get(
            reverse(FOLLOW_INDEX)
        )
        return len(response.context['page_obj']) == 0

    def test_user_follow_and_unfollow_to_other(self):
        '''проверяем, что пользователь может подписываться на автора
            и отписываться от него
        '''
        #  Сначала проверим, что у user1 в ленте избранных авторов ничего нет
        self.assertTrue(self._check_followers_band_is_empty(self.client1))

        #  после подписки user1 на user2 проверим, что посты user2 появились
        #  у user1 в избранных
        user2_posts_count = Post.objects.filter(author=self.user2).count()
        self.client1.get(
            reverse(PROFILE_FOLLOW, kwargs={'username': self.user2})
        )
        response = self.client1.get(
            reverse(FOLLOW_INDEX)
        )
        self.assertEqual(len(response.context['page_obj']), user2_posts_count)

        #  после отписки от user2 проверим, что у user1 в ленте избранных
        #  нет никаких постов
        self.client1.get(
            reverse(PROFILE_UNFOLLOW, kwargs={'username': self.user2})
        )
        self.assertTrue(self._check_followers_band_is_empty(self.client1))

    def test_post_in_follow_band(self):
        '''Новая запись пользователя появляется в ленте тех, кто на него
        подписан и не появляется в ленте тех, кто не подписан
        '''
        client_list = [
            self.client1,
            self.client2,
            self.client3
        ]
        #  сначала проверим, что списки избранного у всех пустые
        for client in client_list:
            with self.subTest(client=client):
                self.assertTrue(self._check_followers_band_is_empty(client))

        #  user1 подписывается на user2
        self.client1.get(
            reverse(PROFILE_FOLLOW, kwargs={'username': self.user2})
        )

        #  user2 создает пост
        post_user2 = Post.objects.create(
            author=self.user2,
            text='Тестовый пост от User2',
        )

        #  проверим, что у user1 этот пост появился
        response = self.client1.get(
            reverse(FOLLOW_INDEX)
        )
        post_list = response.context['page_obj']
        self.assertEqual(len(post_list), 1)

        self.assertEqual(post_list[0].text, post_user2.text)

        #  проверим, что у user3 никаких постов нет
        self._check_followers_band_is_empty(self.client3)
