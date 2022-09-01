from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.shortcuts import redirect
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.shortcuts import render,get_object_or_404
from django.http import HttpResponse
from django.contrib.auth import authenticate,login
from django.contrib.auth.decorators import login_required
from .models import Post,Blocked_words
from .forms import EmailPostForm, CommentForm, SearchForm, PostForm,Profile
from django.core.mail import send_mail
from taggit.models import Tag
from django.db.models import Count
from .forms import LoginForm,UserRegistrationForm



@login_required
def post_list(request, tag_slug=None):
    objects = Post.published.all()
    paginator = Paginator(objects, 3)
    page = request.GET.get('page')
    tag = None
    if tag_slug:
        tag = get_object_or_404(Tag, slug=tag_slug)
        objects = objects.filter(tags__in=[tag])
    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        posts = paginator.page(1)
    except EmptyPage:
        posts = paginator.page(paginator.num_pages)
    return render(request, 'post/list.html', {'page': page, 'posts': posts, 'tag': tag})

@login_required
def post_detail(request, post, year, month, day):
    post = get_object_or_404(Post, slug=post, publish__year=year, publish__month=month, publish__day=day)
    comments = post.comments.filter(active=True)
    blocked_words = Blocked_words.objects.all()
    new_comment = None
    if request.method == 'POST':
        comment_form = CommentForm(data=request.POST)
        if comment_form.is_valid():
            new_comment = comment_form.save(commit=False)
            new_comment.post = post
            new_comment.name = request.user.username
            new_comment.email = request.user.email
            for word in blocked_words:
                if word.bow in new_comment.body.split():
                    new = new_comment.body.split()
                    index = new.index(word.bow)
                    length = len(new[index])
                    ast = length * '*'
                    new[index] = ast
                    new_body = ' '.join(new)
                    new_comment.body = new_body
            new_comment.save()
    else:
        comment_form = CommentForm()
    post_tags_ids = post.tags.values_list('id', flat=True)
    similar_posts = Post.published.filter(tags__in=post_tags_ids).exclude(id=post.id)
    similar_posts = similar_posts.annotate(same_tags=Count('tags')).order_by('-same_tags', '-publish')[:4]

    return render(request, 'post/detail.html', {'post': post,
                                                'comments': comments,
                                                'new_comment': new_comment,
                                                'comment_form': comment_form,
                                                'similar_posts': similar_posts, })

@login_required
def post_share(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    sent = False
    if request.method == 'POST':
        form = EmailPostForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            post_url = request.build_absolute_uri(
                post.get_absolute_url())
            subject = f"{cd['name']} recommends you read {post.title}"
            message = f"Read {post.title} at {post_url}\n\n" \
                      f"{cd['name']}\'s comments: {cd['comments']}"
            send_mail(subject, message, 'hazemm913@gmail.com.com',
                      [cd['to']])
            sent = True
    # if the request isn't post that's mean the req method is GET
    else:
        form = EmailPostForm()

    return render(request, 'post/share.html', {'post': post,
                                               'form': form,
                                               'sent': sent})

@login_required
def post_search(request):
    form = SearchForm()
    query = None
    results = []
    if 'query' in request.GET:
        form = SearchForm(request.GET)
    if form.is_valid():
        search_vector = SearchVector('title', 'body')
        search_query = SearchQuery(query)
        query = form.cleaned_data['query']
        results = Post.published.annotate(
            search=search_vector,
            rank=SearchRank(search_vector, search_query)
        ).filter(search=query).order_by('-rank')

    return render(request, 'post/search.html', {'form': form, 'query': query, 'results': results})

@login_required
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST,request.FILES)
        if post_form.is_valid():
            cd = post_form.cleaned_data
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            for tag in cd['tags']:
                new_post.tags.add(tag)
            return redirect('blogapp:post_list')
    else:
        post_form = PostForm()

    return render(request, 'post/create.html', {'post_form': post_form})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            new_user.set_password(user_form.cleaned_data['password'])
            new_user.save()
            Profile.objects.create(user=new_user)
            return render(request, 'registration/register_done.html', {'new_user': new_user})
    else:
        user_form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'user_form': user_form})


def user_login(request):
    # Instantiate the form with the submitted data
    if request.method == 'POST':
        form = LoginForm(request.POST)
        # check if the form is valid
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Login successfully')
                else:
                    return HttpResponse('Disable registration')
            else:
                return HttpResponse('Invalid Login')
    else:
        form = LoginForm()
    return render(request, 'registration/login.html', {'form': form})
