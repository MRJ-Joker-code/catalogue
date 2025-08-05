from django.contrib import admin
from .models import Profile, Post, LikePost, Comment, Rating, Launchpad, Followers, Notification, BlackFridayDeal, \
    Product, ProductImage, Tag, Category

admin.site.register( Profile)
admin.site.register(Tag)
admin.site.register(Category)
admin.site.register(Comment)
admin.site.register(Launchpad)
admin.site.register(Followers)
admin.site.register(Rating)
admin.site.register(Notification)
admin.site.register(BlackFridayDeal)
admin.site.register(Product)
admin.site.register(ProductImage)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user',)
admin.site.register( Post, PostAdmin)

class LikePostAdmin(admin.ModelAdmin):
    list_display = ('username', 'post_id')
admin.site.register(LikePost, LikePostAdmin)