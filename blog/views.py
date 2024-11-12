from django.shortcuts import render
from django.http import Http404
from django.shortcuts import get_object_or_404
from .models import Post
# Create your views here.


def post_list(request):
    posts = Post.published.all()
    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )

# def post_list_by_author(request):
#     posts = Post.objects.all()

def post_detail(request, post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post
    )
    return render(
        request,
        'blog/post/detail.html',
        {'post': post}
    )

