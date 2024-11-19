from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.shortcuts import (
    get_object_or_404,
    render
)
from django.core.mail import send_mail
from django.http import HttpRequest
from django.views.decorators.http import require_POST
from taggit.models import Tag

# from django.views.generic import ListView
from .models import (
    Post,
    Comment
)
from .forms import (
    EmailPostForm,
    CommentForm,
    SearchForm
)
from django.db.models import Count
from django.contrib.postgres.search import (
    SearchVector,
    SearchQuery,
    SearchRank,
    TrigramSimilarity
)

# Create your views here.


# class PostListView(ListView):
#     '''Alternative posts list view'''

#     queryset = Post.objects.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'


@require_POST
def post_comment(request: HttpRequest, post_id):
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )
    comment: Comment = None
    form = CommentForm(data=request.POST)
    if form.is_valid():
        # Crreate a comment object without saving it
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(
        request,
        'blog/post/comment.html',
        {
            'post': post,
            'form': form,
            'comment': comment
        }
    )


def post_share(request: HttpRequest, post_id):
    # Retrieve post by id
    sent = False
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.PUBLISHED
    )

    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url()
            )
            subject = (
                f"{cd['name']} ({cd['email']})"
                f"recoments you red {post.title}"
            )
            message = (
                f"Read {post.title} at {post_url}\n\n"
                f"{cd['name']}\'s comments: {cd['comments']}"
            )
            send_mail(
                subject=subject,
                message=message,
                from_email=None,
                recipient_list=[cd['to']]
            )
            sent = True
    else:
        form = EmailPostForm()

    return render(
        request,
        'blog/post/share.html',
        {
            'post': post,
            'form': form,
            'sent': sent
        }
    )


def post_list(request: HttpRequest, tag_slug=None):
    posts_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        posts_list = posts_list.filter(tags__in=[tag])
    # Pagination
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


def post_detail(request: HttpRequest, post: Post):
    post = get_object_or_404(
        Post,
        status=Post.Status.PUBLISHED,
        slug=post
    )

    # list of active comments for this post
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # List similar posts
    post_tag_ids = post.tags.values_list('id', flat=True)
    simmilar_posts = Post.published \
        .filter(tags__in=post_tag_ids) \
        .exclude(id=post.id) \
        .annotate(same_tags=Count('tags')) \
        .order_by('-same_tags', '-publish')[:4]

    return render(
        request,
        'blog/post/detail.html',
        {
            'post': post,
            'comments': comments,
            'form': form,
            'simmilar_posts': simmilar_posts
         }
    )

def post_search(request: HttpRequest):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        print(form)
        if form.is_valid():
            query = form.cleaned_data['query']
            search_vector = SearchVector('title', weight='A') + \
                SearchVector('body', weight='B')
            search_query = SearchQuery(query)
            results = (
                Post.published.annotate(
                    # search=search_vector,
                    # rank=SearchRank(search_vector, search_query)
                    similarity=TrigramSimilarity('title', query)
                # ).filter(rank__gte=0.3) \
                ).filter(similarity__gt=0.1) \
                .order_by('-similarity')
            )

    return render(
        request,
        'blog/post/search.html',
        {
            'form': form,
            'query': query,
            'results': results,
        }
    )