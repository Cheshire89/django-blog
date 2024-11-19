from django.contrib.sitemaps import Sitemap
from .models import Post
from django.urls import reverse
from taggit.models import Tag


class PostSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9


    def items(self):
        return Post.published.all()

    def lastmod(self, obj: Post):
        return obj.updated


class TagSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.9

    def items(self):
        # Return all tags used in the blog
        return Tag.objects.all()

    def location(self, obj):
        # Generate URL for the tag-filtered view
        return reverse('blog:post_list_by_tag', kwargs={'tag_slug': obj.slug})