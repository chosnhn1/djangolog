from django.shortcuts import render, get_object_or_404
from django.http import Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView
from django.core.mail import send_mail
import os
from .models import Post
from .forms import EmailPostForm

# function-based view
# def post_list(request):
#     post_list = Post.published.all()
#     # do pagination
#     paginator = Paginator(post_list, 3)
#     page_number = request.GET.get('page', 1)

#     # add page validation
#     try:
#         posts = paginator.page(page_number)
#     except PageNotAnInteger:
#         # return first page if got not integer
#         posts = paginator.page(1)
#     except EmptyPage:
#         # return final page if page is blank
#         posts = paginator.page(paginator.num_pages)
    

#     # posts = paginator.page(page_number)
#     return render(request, 'blog/post/list.html', {'posts': posts})

# class-based view
class PostListView(ListView):
    queryset = Post.published.all()
    context_object_name = 'posts'
    paginate_by = 3
    template_name = 'blog/post/list.html'

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

