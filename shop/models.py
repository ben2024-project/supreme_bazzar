from django.db import models

from django.contrib.auth.models import User

from django.db.models.signals import post_save

class Category(models.Model):

    name = models.CharField(max_length=200, unique=True)

    description = models.CharField(max_length=200)

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    
    def __str__(self):

        return self.name


class Product(models.Model):

    product = models.CharField(max_length=200)

    description = models.TextField(null=True, blank=True)

    price = models.PositiveIntegerField()

    category_object = models.ForeignKey(Category, on_delete=models.CASCADE)

    image = models.ImageField(upload_to='product_images', null=True,   blank=True,default='product_images/default.jpg') 

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    
    def __str__(self):

        return self.product
    


class Basket(models.Model):

    owner = models.OneToOneField(User, on_delete=models.CASCADE,related_name="cart")

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    
    def __str__(self):

        return self.owner.username
    
    @property
    def cart_item_count(self):

        return self.cartitems.filter(is_order_placed=False).count()
    

    @property
    def cart_total(self):

        basket_items=self.cartitems.filter(is_order_placed=False)

        total_price=0

        if basket_items:

            for bi in basket_items:

                total_price+=bi.total_amount

        return total_price    
    
    
    
    
   

class BasketItem(models.Model):

    basket_object = models.ForeignKey(Basket, on_delete=models.CASCADE,related_name="cartitems")

    product_object = models.ForeignKey(Product, on_delete=models.CASCADE)

    quantity = models.PositiveIntegerField(default=1)

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    is_order_placed=models.BooleanField(default=False)

    @property 
    def total_amount(self):

        return self.product_object.price*self.quantity



class Order(models.Model):

    user_object = models.ForeignKey(User,on_delete=models.CASCADE, related_name='myorders')
                                    
    basket_item_objects = models.ManyToManyField(BasketItem)

    delivery_address = models.CharField(max_length=250)

    phone = models.CharField(max_length=12)

    pin=models.CharField(max_length=10,null=True)

    email = models.CharField(max_length=100)

    pay_options = (
        ('online', 'online'),
        ('cod', 'cod')
    )

    payment_mode = models.CharField(max_length=100,choices=pay_options, default='cod')                             

    order_id = models.CharField(max_length=200, null=True)

    is_paid = models.BooleanField(default=False)

    order_status = (
        ('order_confirmed', 'Order confirmed'),
        ('dispatched', 'Dispatched'),
        ('in_transit', 'In transit'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),

    )

    status = models.CharField(
                                max_length=200, 
                                choices=order_status, 
                                default='order_confirmed'
                            )

    created_date = models.DateTimeField(auto_now_add=True)

    updated_date = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)

    @property
    def sub_total(self):

        basket_items=self.basket_item_objects.all()

        total=0

        if basket_items:

            for bi in basket_items:

                total+=bi.total_amount

        return total 


def create_basket(sender,instance,created,**kwargs):

    if created:

        Basket.objects.create(owner=instance)

post_save.connect(sender=User,receiver=create_basket)
