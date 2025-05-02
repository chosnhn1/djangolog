from django.shortcuts import render, get_object_or_404
from django.http import Http404
from .models import Post
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

def post_list(request):
    post_list = Post.published.all()
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
    return render(request, 'blog/post/list.html', {'posts': posts})

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

    return render(request, 'blog/post/detail.html', {'post': post})