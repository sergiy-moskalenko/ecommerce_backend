from django.db import models
from django.utils.text import slugify
from mptt.fields import TreeForeignKey
from mptt.models import MPTTModel
from unidecode import unidecode

from accounts.models import User


class Category(MPTTModel):
    name = models.CharField(max_length=100, unique=True)
    parent = TreeForeignKey('self', blank=True, null=True, on_delete=models.CASCADE, related_name='children',
                            db_index=True)
    slug = models.SlugField(max_length=100, unique=True)
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    hide = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super(Category, self).save(*args, **kwargs)

    class MPTTMeta:
        order_insertion_by = ['name']

    class Meta:
        verbose_name = 'Category'
        verbose_name_plural = 'Categories'

    def __str__(self):
        return self.name


class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products')
    image = models.ImageField(blank=True, null=True, upload_to='images/')
    name = models.CharField(max_length=250, )
    slug = models.SlugField(max_length=100, unique=True)
    price = models.DecimalField(max_digits=7, decimal_places=2)
    description = models.TextField()
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(unidecode(self.name))
        super(Product, self).save(*args, **kwargs)

    def __str__(self):
        return self.name


class Option(models.Model):
    name = models.CharField(max_length=150)

    def __str__(self):
        return self.name


class Value(models.Model):
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='values')
    name = models.CharField(max_length=250)

    def __str__(self):
        return f'{self.option.name}: {self.name}'


class ProductOptionValue(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='options_values')
    option = models.ForeignKey(Option, on_delete=models.CASCADE, related_name='products_options')
    value = models.ForeignKey(Value, on_delete=models.CASCADE, related_name='products_values')

    def __str__(self):
        return f'{self.id}: {self.product.name[:15]} : {self.option.name}'


class Favorite(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='favorites')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products_favorites')

    def __str__(self):
        return f'{self.user.username} - {self.product.name[:15]}'


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(blank=True, null=True, upload_to='images/', )
