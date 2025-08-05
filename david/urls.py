from operator import indexOf

from django.urls import path
from david import views
from david.views import inventory_view

urlpatterns=[
    path('',views.index,name='index'),
    path('settings',views.settings,name='settings'),
    path('explore', views.explore, name='explore'),
    path('get-tags/', views.get_tags_for_category, name='get_tags_for_category'),
    path('upload', views.upload, name='upload'),
    path('terms', views.terms, name='terms'),
    path('about', views.about, name='about'),
    path('help', views.help, name='help'),
    path('question', views.question, name='question'),
    path('signup', views.signup, name='signup'),
    path('signin', views.signin, name='signin'),
    path('forgot-password/', views.forgot_password_request, name='forgot_password'),
    path('verify-code/<str:username>/', views.verify_code, name='verify_code'),
    path('reset-password/<str:username>/', views.reset_password, name='reset_password'),
    path('logout', views.logout, name='logout'),
    path('like-post', views.like_post, name='like-post'),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('post/<uuid:post_id>/', views.post_detail, name='post_detail'),
    path('launchpad', views.launchpad, name='launchpad'),
    path('launchpad/<int:pk>/', views.launchpad, name='launchpad'),
    path('launchpad/upload/', views.upload_launchpad, name='upload_launchpad'),
    path('follow/<str:username>/', views.follow, name='follow'),
    path('notifications/', views.notifications, name='notification'),
    path('post/<uuid:post_id>/share/', views.share_post, name='share_post'),
    path('post/<uuid:post_id>/delete/', views.delete_post, name='delete_post'),
    path('black-friday', views.black_friday, name='black_friday'),
    path('black-friday/upload/', views.upload_deal, name='upload_deal'),
    path('search/', views.search_user, name='search_user'),
    path('market-place', views.market_place, name='market_place'),
    path('product/<int:product_id>/', views.product_detail, name='product_detail'),
    path('products/similar/<int:product_id>/', views.tagged_products, name='tagged_products'),
    path('fashion/', views.fashion_custom_view, name='fashion_custom'),
    path('fashion/men/', views.men_view, name='men_category'),
    path('fashion/women/', views.women_view, name='women_category'),
    path('fashion/baby/', views.baby_view, name='baby_category'),
    path('fashion/pets/', views.pets_view, name='pets_category'),
    path('category/<slug:slug>/', views.category_detail, name='category_detail'),
    path('market-place/search/', views.tag_search, name='tag_search'),
    path('inventory/', inventory_view, name='inventory'),
    path('product/<int:product_id>/delete/', views.delete_product, name='delete_product'),




]
