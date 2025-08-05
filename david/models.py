import uuid
from datetime import datetime
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User
from django.db.models import Avg




user = get_user_model()
class Profile(models.Model ):
    user = models.OneToOneField( User, on_delete= models.CASCADE)
    id_user = models.IntegerField(null=True, blank=True)
    bio= models.TextField(blank=True)
    profileimg= models.ImageField( upload_to='profile_images', default='download.png')
    location= models.CharField( max_length=120, blank=True)
    email_verification_code = models.CharField(max_length=6, blank=True, null=True)

    def _str_(self):
        return self.user.username

class Post(models.Model):
    id= models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    caption=models.TextField()
    created_at=models.DateTimeField(default=datetime.now)
    no_of_likes=models.IntegerField(default=0)

    def _str_(self):
        return self.user

class PostMedia(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='media_files')
    media = models.FileField(upload_to='posts_images', blank=True, null=True)



class LikePost(models.Model):
    post_id= models.CharField(max_length=500)
    username= models.CharField(max_length=100)
    def _str_(self):
        return self.username

class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.user.username

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'post')  # Ensure one rating per user per post

    def __str__(self):
        return f'{self.user.username} rated {self.post.id} as {self.rating}'


class Launchpad(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='launchpads',null=True, blank=True)
    product_name = models.CharField(max_length=600)
    company_name = models.CharField(max_length=600)
    date = models.CharField(max_length=600)
    location_point = models.CharField(max_length=600)
    product_description = models.CharField(max_length=600)
    product_image = models.ImageField(upload_to='post_images/', blank=True, null=True)
    product_link=models.CharField(max_length=600)
    def __str__(self):
        return self.product_name

class Followers(models.Model):
    followers = models.ManyToManyField(User, related_name='following', blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    def total_followers(self):
        return self.followers.count()

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    message = models.TextField()
    link = models.URLField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)


from django.db import models

class BlackFridayDeal(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    original_price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=0)  # added to track number of items
    image = models.ImageField(upload_to='black_friday_deals/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    start_time = models.DateTimeField(null=True, blank=True)
    end_time = models.DateTimeField()
    link = models.URLField(blank=True, null=True)
    change = models.IntegerField(help_text="Use negative numbers to subtract or positive to restock",null=True, blank=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    def discount_percentage(self):
        try:
            return round(100 * (self.original_price - self.discount_price) / self.original_price)
        except ZeroDivisionError:
            return 0

    def __str__(self):
        return self.title


SIZE_CHOICES = [
    ('XXS', 'XXS'), ('XS', 'XS'), ('S', 'S'),
    ('M', 'M'), ('L', 'L'), ('XL', 'XL'),
]

COLOR_CHOICES = [
    ('Black', 'Black'),
    ('Gray', 'Gray'),
    ('White', 'White'),
    ('Blue', 'Blue'),
    ('Red', 'Red'),
    ('Green', 'Green'),
    ('Yellow', 'Yellow'),
    ('Purple', 'Purple'),
    ('Orange', 'Orange'),
    ('Brown', 'Brown'),
    ('Pink', 'Pink'),
]

class Color(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name

class Size(models.Model):
    label = models.CharField(max_length=5)

    def __str__(self):
        return self.label

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)


    def __str__(self):
        return self.name

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    categories = models.ManyToManyField(Category, related_name='tags')

    def __str__(self):
        return self.name
class Product(models.Model):
    seller = models.CharField(max_length=200)
    name = models.CharField(max_length=200)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    image = models.ImageField(upload_to='products/')
    colors = models.ManyToManyField('Color', blank=True)
    sizes = models.ManyToManyField('Size', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    link = models.URLField(blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    tags = models.ManyToManyField(Tag, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, blank=True, null=True)
    def __str__(self):
        return self.name

    def get_display_price(self):
        return self.discount_price if self.discount_price else self.price




class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='product_images/')

