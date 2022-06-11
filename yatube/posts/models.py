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

    def __str__(self):
        return self.text[:FIRST_POST_CHARS]


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

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
        unique_together = ('user', 'author',)
        constraints = [
            models.CheckConstraint(
                name="impossible_follow_self",
                check=~models.Q(user=models.F("author")),
            ),
        ]
