from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import render
from django.shortcuts import get_object_or_404
# from django.views.generic import ListView
from .models import Post
from pprint import pprint
# Create your views here.


# class PostListView(ListView):
#     '''Alternative posts list view'''

#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


def post_list(request):
    posts_list = Post.published.all()
    paginator = Paginator(posts_list, 3)
    page_number = request.GET.get('page', 1)

    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)


    return render(
        request,
        'blog/post/list.html',
        {'posts': posts}
    )


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

