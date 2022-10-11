from django.shortcuts import render, redirect, get_object_or_404
from blogapp.models import Post, Profile
from django.contrib.auth.decorators import user_passes_test, login_required
from blogapp.forms import PostForm, ProfileEditForm, UserUpdateForm, ProfileUpdateForm
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
import os
User = get_user_model()

#Posts views
@login_required
@user_passes_test(lambda u: u.is_superuser)
def list_posts(request):
    posts = Post.objects.select_related('author').all()
    return render(request, 'dashboard/posts/list.html', {"posts": posts})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def detail_post(request, pk):
    post = Post.objects.select_related('author').filter(pk=pk)[0]
    return render(request, 'dashboard/posts/detail.html', {"post": post})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_post(request):
    if request.method == 'POST':
        post_form = PostForm(request.POST, request.FILES)
        if post_form.is_valid():
            cd = post_form.cleaned_data
            new_post = post_form.save(commit=False)
            new_post.author = request.user
            new_post.save()
            for tag in cd['tags']:
                new_post.tags.add(tag)
            return redirect('list_posts')
    else:
        post_form = PostForm()
    return render(request, 'dashboard/posts/create.html', {"form":post_form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_post(request, pk):
    post = Post.objects.filter(pk=pk)[0]
    if request.method == 'POST':
        if request.FILES:
            post_form = PostForm(request.POST, request.FILES, instance=post)
            if post.picture:
                os.remove(post.picture.path)
        else:    
            post_form = PostForm(request.POST, instance=post)
        if post_form.is_valid():
            post_form.save()
        return redirect("list_posts")
    else:
        form = PostForm(instance=post)
    return render(request, 'dashboard/posts/update.html', {"post": post, "form":form})

@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_post(request, pk):
    post = Post.objects.filter(pk=pk)[0]
    if post.picture:
        os.remove(post.picture.path)
    post.delete()
    return redirect("list_posts")


# user views
@login_required
@user_passes_test(lambda u: u.is_superuser)
def list_users(request):
    users = User.objects.select_related("user_profile").all()
    return render(request, 'dashboard/users/list.html', {"users":users})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def detail_user(request, pk):
    user = User.objects.select_related("user_profile").filter(pk=pk)[0]
    return render(request, 'dashboard/users/detail.html', {'useer':user})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def update_user(request, pk):
    user = User.objects.select_related("user_profile").filter(pk=pk)[0]
    profile = user.user_profile
    print(profile)
    if request.method == "POST":
        user_form = UserUpdateForm(request.POST, instance=user)
        if request.FILES:
            profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)
            if profile.photo:
                os.remove(profile.photo.path)
        else:
            profile_form = ProfileUpdateForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            if user_form.cleaned_data['is_superuser'] == True and profile.restrict == True:
                profile.restrict = False
                profile.save()
            user_form.save()
            profile_form.save()
            return redirect('list_users')
    else:
        user_form = UserUpdateForm(instance=user)
        profile_form = ProfileUpdateForm(instance=profile)
    return render(request, 'dashboard/users/update.html', {'user_form':user_form, 'profile_form':profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def delete_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.user_profile
    if profile.photo:
        os.remove(profile.photo.path)
    profile.delete()
    user.delete()
    return redirect('list_users')

@login_required
@user_passes_test(lambda u: u.is_superuser)
def create_user(request):
    if request.method == "POST":
        user_form = UserCreationForm(request.POST)
        profile_form = ProfileEditForm(request.POST, request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user = user_form.save()
            Profile.objects.create( user = user,
                                    date_of_birth = profile_form.cleaned_data['date_of_birth'],
                                    photo = profile_form.cleaned_data['photo'])
            return redirect('list_users')
    else:
        user_form = UserCreationForm()
        profile_form = ProfileEditForm()
    return render(request, 'dashboard/users/create.html', {'user_form':user_form, 'profile_form':profile_form})


@login_required
@user_passes_test(lambda u: u.is_superuser)
def restrict_user(request, pk):
    user = get_object_or_404(User, pk=pk)
    profile = user.user_profile
    if profile.restrict:
        profile.restrict = False
    else:
        profile.restrict = True
    profile.save()
    return redirect('list_users')