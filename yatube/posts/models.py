from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
FIRST_POST_CHARS = 15


class Post(models.Model):
    text = models.TextField(verbose_name='Текст поста')
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор'
    )
    group = models.ForeignKey(
        to='Group',
        verbose_name='Группа',
        on_delete=models.SET_NULL,
        related_name='posts',
        blank=True,
        null=True
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name='Пост'
        verbose_name_plural='Посты'

    def __str__(self):
        return self.text[:FIRST_POST_CHARS]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    class Meta:
        verbose_name='Группа'
        verbose_name_plural='Группы'

    def __str__(self):
        return self.title


class Comment(models.Model):
    post = models.ForeignKey(
        to=Post,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        to=User,
        related_name='comments',
        on_delete=models.CASCADE,
        verbose_name='Автор комментария'
    )
    text = models.TextField(max_length=200, verbose_name='Текст комментария')
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name='Комментарий'
        verbose_name_plural='Комментарии'

    def __str__(self):
        return f'{self.author.username} (к посту {self.post}): {self.text}'



class Follow(models.Model):
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
    )

    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        constraints = [
            models.CheckConstraint(
                name='impossible_follow_self',
                check=~models.Q(user=models.F('author')),
            ),
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='selffollow'
            )
        ]
