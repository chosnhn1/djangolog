import os
from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.db.models import Count
from django.core.mail import send_mail
from django.views.decorators.http import require_POST
from django.contrib.postgres.search import SearchVector
from .models import Post, Comment
from .forms import EmailPostForm, CommentForm, SearchForm
from taggit.models import Tag

# function-based view
def post_list(request, tag_slug=None):
    post_list = Post.published.all()
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        post_list = post_list.filter(tags__in=[tag])
    # do pagination
    paginator = Paginator(post_list, 3)
    page_number = request.GET.get('page', 1)

    # add page validation
    try:
        posts = paginator.page(page_number)
    except PageNotAnInteger:
        # return first page if got not integer
        posts = paginator.page(1)
    except EmptyPage:
        # return final page if page is blank
        posts = paginator.page(paginator.num_pages)
    

    # posts = paginator.page(page_number)
    return render(request, 'blog/post/list.html', {'posts': posts, 'tag': tag, })

# class-based view
# class PostListView(ListView):
#     queryset = Post.published.all()
#     context_object_name = 'posts'
#     paginate_by = 3
#     template_name = 'blog/post/list.html'

# before url optimization:
# def post_detail(request, id):
#     post = get_object_or_404(Post, id=id, status=Post.Status.PUBLISHED)
def post_detail(request, year, month, day, post):
    post = get_object_or_404(Post, status=Post.Status.PUBLISHED, 
                             slug=post, publish__year=year, publish__month=month, publish__day=day)
    # use above instead:
    # try:
    #     post = Post.published.get(id=id)
    # except Post.DoesNotExist:
    #     raise Http404("No Post found.")

    # Comments part
    comments = post.comments.filter(active=True)
    form = CommentForm()

    # Tag and recommendation part
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    # build context
    context = {
        'post': post,
        'comments': comments,
        'form': form,
        'similar_posts': similar_posts
    }

    return render(request, 'blog/post/detail.html', context=context)

def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cleaned = form.cleaned_data

            # perform sending email
            post_url = request.build_absolute_uri(post.get_absolute_url())
            subject = f"{cleaned['name']} recommends you read " f"{post.title}"
            message = f"Read {post.title} at {post_url}\n\n" f"{cleaned['name']}\'s comments: {cleaned['comments']}"
            mail_account = os.getenv('EMAIL_HOST_USER')
            send_mail(subject, message, mail_account, [cleaned['to']])
            sent = True
    else:
        form = EmailPostForm()
    return render(request, 'blog/post/share.html', {'post': post, 'form': form, 'sent': sent})

@require_POST
def post_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id, status=Post.Status.PUBLISHED)
    comment = None

    form = CommentForm(data=request.POST)
    if form.is_valid():
        # set post into comment, with ModelForm's save method
        # notice that Form cannot perform this
        comment = form.save(commit=False)
        comment.post = post
        comment.save()

    return render(request, 'blog/post/comment.html', {'post': post, 'form': form, 'comment': comment})


def post_search(request):
    form = SearchForm()
    query = None
    results = []

    if 'query' in request.GET:
        form = SearchForm(request.GET)
        if form.is_valid():
            query = form.cleaned_data['query']
            results = Post.published.annotate(search=SearchVector('title', 'body'),).filter(search=query)
    
    return render(request, 'blog/post/search.html', {'form': form, 'query': query, 'results': results})
