from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post

POSTS_ON_PAGE = 10
User = get_user_model()


def _get_page_obj(request, queryset):
    paginator = Paginator(queryset, POSTS_ON_PAGE)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj


def index(request):
    posts = (
        Post
        .objects
        .select_related('author')
    )

    page_obj = _get_page_obj(request, posts)

    template = 'posts/index.html'
    context = {
        'page_obj': page_obj,
    }

    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(
        Group.objects.prefetch_related('posts'),
        slug=slug
    )
    posts = group.posts.all()

    page_obj = _get_page_obj(request, posts)

    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj,
    }

    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    user_posts = user.posts.all()
    following = Follow.objects.filter(user=user).exists()

    page_obj = _get_page_obj(request, user_posts)

    context = {
        'profile_user': user,
        'page_obj': page_obj,
        'following': following,
    }
    template = 'posts/profile.html'
    return render(request, template, context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    comments = post.comments.all()
    comment_form = CommentForm(request.POST or None)
    context = {
        'post': post,
        'comments': comments,
        'comment_form': comment_form
    }
    template = 'posts/post_detail.html'
    return render(request, template, context)


@login_required
def post_create(request):

    form = PostForm(request.POST or None, files=request.FILES or None)

    context = {
        'form': form,
    }
    template = 'posts/create_post.html'

    if request.method == 'POST':
        if not form.is_valid():
            return render(request, template, context)

        post = form.save(commit=False)
        post.author = request.user
        post.save()

        return redirect('posts:profile', request.user)
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if post.author != request.user:
        return redirect('posts:post_detail', post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )

    context = {
        'form': form,
        'is_edit': True,
    }
    template = 'posts/create_post.html'

    if request.method == 'POST':
        if not form.is_valid():
            return render(request, template, context)

        form.save()
        return redirect('posts:post_detail', post_id)

    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    posts = Post.objects.filter(author__following__user=request.user)

    page_obj = _get_page_obj(request, posts)

    context = {'page_obj': page_obj}

    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = User.objects.get(username=username)
    follow_link = Follow.objects.filter(user=request.user, author=author)
    if not follow_link.exists():
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = User.objects.get(username=username)
    follow_link = Follow.objects.filter(user=request.user, author=author)
    if follow_link.exists():
        Follow.objects.get(user=request.user, author=author).delete()
    return redirect('posts:profile', username=username)
