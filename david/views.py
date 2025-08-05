from django.contrib import messages, auth
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.template.defaulttags import comment
from django.shortcuts import get_object_or_404
from django.db.models import Count, Sum
from django import forms
from django.views.decorators.http import condition
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from django.utils.dateparse import parse_datetime
from .models import Profile,Post, LikePost, Comment,Tag, PostMedia,Launchpad,Followers,Notification,BlackFridayDeal, Product, ProductImage,Color, Size,Category
from django.db import IntegrityError
from django.db.models import F, ExpressionWrapper, FloatField
from django.utils import timezone
from django.db.models import Avg
from django.db.models import Q
import random
from django.http import JsonResponse
from django.core.mail import send_mail

@login_required(login_url='signin')
def index(request):
    try:
        user_profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        image = request.FILES.get('profileimg')
        user_profile = Profile.objects.create(user=request.user,
                                              bio='',
                                              location='',
                                              profileimg=image if image else 'default.png'
                                              )
    if request.user.is_authenticated:
        posts = recommended_posts(request.user)
    else:
        posts = Post.objects.all().order_by('-created_at')[:30]

    if request.method == 'POST':
        content = request.POST.get('content')
        post_id = request.POST.get('post_id')

        print("Received POST:", content, post_id)

        if not content or not post_id:
            print("Missing content or post_id.")
            return redirect('index')

        try:
            post = Post.objects.get(id=post_id)
        except Post.DoesNotExist:
            print(f"Post with ID {post_id} does not exist.")
            return redirect('index')

        Comment.objects.create(post=post, content=content, user=request.user)
        print("✅ Comment saved.")
        return redirect('index')
    return render(request, 'index.html', {'user_profile':user_profile, 'posts':posts})

def recommended_posts(user):
    most_liked = Post.objects.all().order_by('-no_of_likes')[:20]

    try:
        following_users = User.objects.filter(followers__followers=user)
    except:
        following_users = User.objects.none()

    followed_posts = Post.objects.filter(user__in=following_users).exclude(
        id__in=most_liked.values_list('id', flat=True)
    )[:20]

    excluded_ids = list(most_liked.values_list('id', flat=True)) + list(followed_posts.values_list('id', flat=True))
    random_posts = Post.objects.exclude(id__in=excluded_ids).order_by('?')[:20]

    return list(most_liked) + list(followed_posts) + list(random_posts)

@login_required(login_url='signin')
def like_post(request):
    username= request.user.username
    post_id= request.GET.get('post_id')

    post=Post.objects.get(id=post_id)

    like_filter=LikePost.objects.filter(post_id=post_id, username=username)

    if not like_filter.exists():
        new_like=LikePost.objects.create(post_id=post_id, username=username)
        new_like.save()
        post.no_of_likes=post.no_of_likes+1
        post.save()
        return redirect('/')
    else:
        like_filter.delete()
        post.no_of_likes = post.no_of_likes-1
        post.save()
        return redirect('/')

@login_required(login_url='signin')
def upload(request):
    if request.method == 'POST':
        user = request.user
        caption = request.POST.get('caption')
        files = request.FILES.getlist('media')

        if len(files) > 5:
            return render(request, 'upload.html', {
                'error': 'You can only upload a maximum of 5 media files.'
            })

        new_post = Post.objects.create(user=user, caption=caption)

        for file in files:
            PostMedia.objects.create(post=new_post, media=file)

        try:
            followers_obj = Followers.objects.get(user=user)
            for follower in followers_obj.followers.all():
                Notification.objects.create(
                    recipient=follower,
                    message=f"{user.username} made a new post!",
                    link=reverse('profile', kwargs={'username': user.username})
                )
        except Followers.DoesNotExist:
            pass

        return redirect('/')

    return render(request, 'upload.html')


@login_required(login_url='signin')
def settings(request):
    try:
       user_profile, created = Profile.objects.get_or_create(user=request.user)
    except IntegrityError:
        user_profile = Profile.objects.get(user=request.user)

    if request.method=='POST':

        if request.FILES.get('image') is None:
            image= user_profile.profileimg
            bio=request.POST['bio']
            location=request.POST['location']

            user_profile.profileimg=image
            user_profile.bio=bio
            user_profile.location=location
            user_profile.save()

        if request.FILES.get('image') is not None:
            image=request.FILES.get('image')
            bio = request.POST['bio']
            location = request.POST['location']

            user_profile.profileimg = image
            user_profile.bio = bio
            user_profile.location = location
            user_profile.save()
        return redirect('/')

    return render(request, 'setting.html',{'user_profile':user_profile})

def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        password2 = request.POST['password']

        if password == password2:
            if User.objects.filter(email=email).exists():
                messages.info(request, 'Email Taken')
                return redirect('signup')
            elif User.objects.filter(username=username).exists():
                messages.info(request, 'Username Taken')
                return redirect('signup')
            else:
                user = User.objects.create_user(username=username, email=email, password=password)
                user.save()

                user_login=auth.authenticate(username=username, password=password)
                auth.login(request, user_login)

                #create a profile object for new user
                user_model = User.objects.get(username=username)
                new_profile = Profile.objects.create(user=user_model, id_user =user_model.id)
                new_profile.save()
                return redirect('settings')
        else:
            messages.info(request, 'Incorrect Password')
            return redirect('signup')

    else:
        return render(request, 'signup.html')

def signin(request):
    if request.method=='POST':
        username=request.POST ['username']
        password= request.POST ['password']

        user=auth.authenticate(username=username,password=password)

        if user is not None:
            auth.login(request,user)
            return redirect('/')
        else:
            messages.info(request,'Account Not Found')
            return redirect('signin')
    else:
       return render(request, 'signin.html')


def generate_code():
    return str(random.randint(100000, 999999))

def forgot_password_request(request):
    if request.method == 'POST':
        email = request.POST['email']
        try:
            user = User.objects.get(email=email)
            code = generate_code()

            profile = Profile.objects.get(user=user)
            profile.email_verification_code = code
            profile.save()


            send_mail(
                'Your Password Reset Code',
                f'Your verification code is: {code}',
                'noreply@example.com',
                [user.email],
                fail_silently=False,
            )

            return redirect('verify_code', username=user.username)

        except User.DoesNotExist:
            messages.error(request, "Email not found.")
    return render(request, 'forgot_password.html')


def verify_code(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)

    if request.method == 'POST':
        code = request.POST['code']
        if profile.email_verification_code == code:
            profile.email_verification_code = ''
            profile.save()
            return redirect('reset_password', username=user.username)
        else:
            messages.error(request, "Invalid code.")
    return render(request, 'verify_code.html', {'username': username})


def reset_password(request, username):
    user = get_object_or_404(User, username=username)
    if request.method == 'POST':
        new_password = request.POST['new_password']
        user.set_password(new_password)
        user.save()
        messages.success(request, "Password reset successfully.")
        return redirect('signin')
    return render(request, 'reset_password.html', {'username': username})

def logout(request):
    auth.logout(request)
    return redirect('signin')

@login_required(login_url='signin')
def profile(request,username):
    user_object=User.objects.get(username=username)
    user_profile= Profile.objects.get(user=user_object)
    user_posts=Post.objects.filter(user=user_object)
    user_posts_length= len(user_posts)
    total_likes = Post.objects.filter(user=user_object).aggregate(Sum('no_of_likes'))['no_of_likes__sum'] or 0
    followers_obj, _ = Followers.objects.get_or_create(user=user_profile.user)
    is_following = request.user in followers_obj.followers.all()
    total_followers = followers_obj.total_followers()
    user_launchpads = Launchpad.objects.filter(user=user_object)

    context={
    'user_object':user_object,
    'user_profile':user_profile,
    'user_posts': user_posts,
    'user_posts_length':  user_posts_length,
    'total_likes':total_likes,
    'followers_obj': followers_obj,
    'is_following': is_following,
    'total_followers': total_followers,
    'user_launchpads': user_launchpads
    }

    return render(request,'profile.html',context )

@login_required(login_url='signin')
def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    media_files = post.media_files.all()  # from your related_name

    return render(request, 'post_detail.html', {
        'post': post,
        'media_files': media_files
    })

@login_required(login_url='signin')
def upload_launchpad(request):
    if request.method == 'POST':
        product_name = request.POST.get('product_name')
        company_name = request.POST.get('company_name')
        date = request.POST.get('date')
        location_point = request.POST.get('location_point')
        product_description = request.POST.get('product_description')
        product_link = request.POST.get('product_link')
        product_image = request.FILES.get('product_image')

        Launchpad.objects.create(
            product_name=product_name,
            company_name=company_name,
            date=date,
            location_point=location_point,
            product_description=product_description,
            product_link=product_link,
            product_image=product_image
        )
        return redirect('launchpad')

    users = User.objects.all()
    for user in users:
        Notification.objects.create(
            recipient=user,
            message=f"New Launchpad Product!",
            link=reverse('launchpad')
        )
    return render(request, 'launchpad_upload.html')

def launchpad(request):
    launchpads = Launchpad.objects.all().order_by('-id')
    return render(request, 'launchpad.html', {'launchpads': launchpads})

def terms(request):
    return render(request,'terms and condition.html')

def question(request):
    return render(request,'question.html')

def about(request):
    return render(request,'about.html')

@login_required(login_url='signin')
def follow(request, username):
    user_to_follow = User.objects.get(username=username)
    followers_obj, created = Followers.objects.get_or_create(user=user_to_follow)

    if request.user in followers_obj.followers.all():
        followers_obj.followers.remove(request.user)
    else:
        followers_obj.followers.add(request.user)

    return redirect('profile', username=username)

@login_required(login_url='signin')
def profile_view(request, username):
    user = get_object_or_404(User, username=username)
    followers_obj, _ = Followers.objects.get_or_create(user=user)

    context = {
        'user_profile': user,
        'followers_obj': followers_obj,
    }
    return render(request, 'profile.html', context)

@login_required(login_url='signin')
def notifications(request):
    notifications = Notification.objects.filter(recipient=request.user).order_by('-timestamp')
    return render(request, 'notification.html', {'notifications': notifications})

@login_required(login_url='signin')
def share_post(request, post_id):
    original_post = get_object_or_404(Post, id=post_id)
    Post.objects.create(
        user=request.user,
        caption=f"Shared from {original_post.user.username}: {original_post.caption}",
        media=original_post.media
    )
    messages.success(request, "Post shared successfully!")
    return redirect('index')

@login_required(login_url='signin')
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id, user=request.user)
    if post.user == request.user:
        post.delete()
    return redirect('index')

def black_friday(request):
    deals = BlackFridayDeal.objects.filter(is_active=True).order_by('-start_time')
    return render(request, 'black_friday.html.html', {'deals': deals})

@login_required(login_url='signin')
def upload_deal(request):
    if request.method == 'POST':
        title = request.POST.get('title')
        original_price = request.POST.get('original_price')
        discount_price = request.POST.get('discount_price')
        link = request.POST.get('link')
        description = request.POST.get('description', '').strip()
        image = request.FILES.get('image')
        start_time_str = request.POST.get('start_time')
        end_time_str = request.POST.get('end_time')

        # Validate required fields
        if not all([title, original_price, discount_price, image, start_time_str, end_time_str]):
            messages.error(request, "All required fields must be filled.")
            return redirect('upload_deal')

        # Convert time
        start_time = parse_datetime(start_time_str)
        end_time = parse_datetime(end_time_str)

        if not start_time or not end_time:
            messages.error(request, "Invalid date/time.")
            return redirect('upload_deal')

        deal = BlackFridayDeal.objects.create(
            title=title,
            original_price=original_price,
            discount_price=discount_price,
            link=link,
            description=description,
            image=image,
            start_time=start_time,
            end_time=end_time,
            user=request.user
        )

        # Send notification
        users = User.objects.exclude(id=request.user.id)
        for user in users:
            Notification.objects.create(
                recipient=user,
                message=f"New Black Friday Deal: {title}",
                link=reverse('black_friday')
            )

        messages.success(request, "Deal uploaded successfully!")
        return redirect('black_friday')

    return render(request, 'black_friday_upload.html')

@login_required(login_url='signin')
def search_user(request):
    query = request.GET.get('q', '')

    user_results = User.objects.filter(
        Q(username__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )

    post_results = Post.objects.filter(
        Q(caption__icontains=query) |
        Q(caption__icontains=query)
    )

    launchpad_results = Launchpad.objects.filter(
        Q( company_name__icontains=query) |
        Q(product_description__icontains=query)
    )

    deal_results = BlackFridayDeal.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )

    context = {
        'query': query,
        'user_results': user_results,
        'post_results': post_results,
        'launchpad_results': launchpad_results,
        'deal_results': deal_results,
    }
    return render(request, 'search_results.html', context)

@login_required(login_url='signin')
def explore(request):
    categories = Category.objects.all()


    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        discount_price= request.POST.get('discount_price')
        if discount_price == "":
            discount_price = None
        quantity = request.POST.get('quantity')
        main_image = request.FILES.get('image')
        image1 = request.FILES.get('image1')
        image2 = request.FILES.get('image2')
        image3 = request.FILES.get('image3')
        image4 = request.FILES.get('image4')
        color_ids = request.POST.getlist('colors')
        size_ids = request.POST.getlist('sizes')
        category_id = request.POST.get('category')
        link = request.POST.get('link')
        tag_ids = request.POST.getlist('tags')

        if not name or not price or not main_image:
            return render(request, 'explore.html', {
                'error': 'Please fill all required fields (name, price, main image).',
                'colors': Color.objects.all(),
                'sizes': Size.objects.all(),
                'categories': categories,  # re-render tags on error
            })
        category = Category.objects.filter(id=category_id).first()
        product = Product.objects.create(
            name=name,
            description=description,
            price=price,
            quantity=quantity,
            image=main_image,
            seller=request.user,
            link=link,
            discount_price=discount_price,
            category = category,
        )

        # Save extra images
        for img in [image1, image2, image3, image4]:
            if img:
                ProductImage.objects.create(product=product, image=img)

        # Save selected colors and sizes
        if color_ids:
            product.colors.set(Color.objects.filter(id__in=color_ids))
        if size_ids:
            product.sizes.set(Size.objects.filter(id__in=size_ids))
        if tag_ids:
            product.tags.set(Tag.objects.filter(id__in=tag_ids))

        return redirect('product_detail', product_id=product.id)

    return render(request, 'explore.html', {
        'colors': Color.objects.all(),
        'sizes': Size.objects.all(),
        'categories': categories,
    })

@login_required(login_url='signin')
def get_tags_for_category(request):
    category_id = request.GET.get('category_id')
    if category_id:
        tags = Tag.objects.filter(categories__id=category_id).values('id', 'name')
        return JsonResponse({'tags': list(tags)})
    return JsonResponse({'tags': []})
@login_required(login_url='signin')
def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    extra_images = product.images.all()[:4]
    tag_ids = product.tags.values_list('id', flat=True)

    similar_products = Product.objects.filter(tags__in=tag_ids).exclude(id=product.id).distinct()[:5]

    related_products = Product.objects.filter(seller=product.seller).exclude(id=product.id)[:5]

    return render(request, 'product_detail.html', {
        'product': product,
        'extra_images': extra_images,
        'related_products': related_products,
        'similar_products': similar_products,
    })

@login_required(login_url='signin')
def market_place(request):
    products = Product.objects.all()
    return render(request, 'marketplace.html',{'products': products})

@login_required(login_url='signin')
def tagged_products(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    tags = product.tags.all()
    related_products = Product.objects.filter(tags__in=tags).exclude(id=product.id).distinct()

    return render(request, 'related_products.html', {
        'product': product,
        'related_products': related_products
    })

@login_required(login_url='signin')
def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)

    tags = category.tags.all()

    products = Product.objects.filter(tags__name__iexact=category).distinct()


    return render(request, 'category.html', {
        'category': category,
        'products': products,
        'tags': tags,
    })

@login_required(login_url='signin')
def fashion_custom_view(request):
    fashion = get_object_or_404(Category, slug="fashion")


    fashion_tags = Tag.objects.filter(categories=fashion)

    products = Product.objects.filter(tags__in=fashion_tags).distinct()

    related_category_slugs = ['men', 'women', 'baby', 'pets']
    related_categories = Category.objects.filter(slug__in=related_category_slugs)

    return render(request, 'fashion_custom.html', {
        'category': fashion,
        'products': products,
        'tags': fashion_tags,
        'related_categories': related_categories,
    })

@login_required(login_url='signin')
def men_view(request):
    category = get_object_or_404(Category, name__iexact='men')
    products = Product.objects.filter(category=category)

    return render(request, 'custom.html', {
        'products': products,
        'category_name': 'Men',
        'category_slug': 'men',
    })

@login_required(login_url='signin')
def women_view(request):
    category = get_object_or_404(Category, name__iexact='women')
    tags = Tag.objects.filter(categories=category)
    products = Product.objects.filter(tags__in=tags).distinct()
    subcategories = tags.values_list('name', flat=True)
    return render(request, 'custom.html', {
        'products': products,
        'category_name': 'Women',
        'subcategories': subcategories,
        'category_slug': 'women',
    })

@login_required(login_url='signin')
def baby_view(request):
    category = get_object_or_404(Category, name__iexact='baby')
    tags = Tag.objects.filter(categories=category)
    products = Product.objects.filter(tags__in=tags).distinct()
    subcategories = tags.values_list('name', flat=True)
    return render(request, 'custom.html', {
        'products': products,
        'category_name': 'Baby',
        'subcategories': subcategories,
        'category_slug': 'baby',
    })

@login_required(login_url='signin')
def pets_view(request):
    category = get_object_or_404(Category, name__iexact='pets')
    tags = Tag.objects.filter(categories=category)
    products = Product.objects.filter(tags__in=tags).distinct()
    subcategories = tags.values_list('name', flat=True)
    return render(request, 'custom.html', {
        'products': products,
        'category_name': 'Pets',
        'subcategories': subcategories,
        'category_slug': 'pets',
    })

@login_required(login_url='signin')
def tag_search(request):
    query = request.GET.get('q', '')
    products = Product.objects.all()

    if query:
        products = products.filter(
            Q(tags__name__icontains=query) | Q(name__icontains=query)
        ).distinct()

    return render(request, 'tag_search.html', {
        'products': products,
        'query': query,
    })

@login_required(login_url='signin')
def inventory_view(request):
    products = Product.objects.filter(seller=request.user).order_by('-created_at')
    return render(request, 'inventory.html', {
        'products': products
    })

@login_required(login_url='signin')
def delete_product(request, product_id):
    product = get_object_or_404(Product, id=product_id, seller=request.user)
    product.delete()
    return redirect('inventory')

def help(request):
    return render(request, 'help.html')