from django.shortcuts import render,redirect

from django.views.generic import View

from shop.forms import RegistrationForm,LoginForm

from django.contrib.auth import authenticate,login,logout

from shop.models import Product,BasketItem,Order

class SignUpView(View):

    def get(self,request,*args,**kwargs):

        form_instance=RegistrationForm()

        return render(request,"registration.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=RegistrationForm(request.POST)

        if form_instance.is_valid():

            form_instance.save()

            # print("Account Created")

            return redirect("register")

        return render(request,"registration.html",{"form":form_instance})


class SignInView(View):

    def get(self,request,*args,**kwargs):

        form_instance=LoginForm()

        return render(request,"login.html",{"form":form_instance})
    
    def post(self,request,*args,**kwargs):

        form_instance=LoginForm(request.POST)

        if form_instance.is_valid():

            data=form_instance.cleaned_data

            uname=data.get("username")

            pwd=data.get("password")

            user_object=authenticate(request,username=uname,password=pwd)

            # print(user_object)

            if user_object:

                login(request,user_object)

                print("session started")

                return redirect("index")
            
        print("failed to login")

        return render(request,"login.html",{"form":form_instance})  
    

class IndexView(View):

    def get(self,request,*args,**kwargs):

         qs=Product.objects.all()

         return render(request,"index.html",{"data":qs})  
    

class ProductDetailView(View):

    def get(self,request,*args,**kwargs): 

        id=kwargs.get("pk")

        qs=Product.objects.get(id=id)

        return render(request,"product_deatail.html",{"data":qs})    


class AddToCartView(View):

    def post(self,request,*args,**kwargs): 

        id=kwargs.get("pk") 

        product_obj=Product.objects.get(id=id) 

        basket_obj=request.user.cart

        qty=request.POST.get("qty") 

        basket_item_obj=BasketItem.objects.filter(product_object=product_obj,basket_object=basket_obj,is_order_placed=False)

        if basket_item_obj:

            basket_item_obj[0].quantity+int(qty)

            basket_item_obj[0].save()

        else:

          BasketItem.objects.create(

                product_object=product_obj,

                basket_object=basket_obj,

                quantity=qty

            ) 

        return redirect("index")
    

class CartListView(View):

    def get(self,request,*args,**kwargs):  

        qs=request.user.cart.cartitems.filter(is_order_placed=False).order_by("-created_date")

        return render(request,"cart_list.html",{"data":qs})    
    

class RemoveCartView(View):

    def get(self,request,*args,**kwargs): 

        id=kwargs.get("pk")

        BasketItem.objects.get(id=id).delete()

        return redirect("cart-list")  


class SignOutView(View):

    def get(self,request,*args,**kwargs):   

        logout(request)

        return redirect("login")       
    

class CartQuantityUpdateView(View):

    def post(self,request,*args,**kwargs): 

        id=kwargs.get("pk")   

        basket_item=BasketItem.objects.get(id=id)

        action=request.POST.get("action")

        if action=="increment":

            basket_item.quantity +=1

        else:

            basket_item.quantity -=1   

        basket_item.save()

        return redirect("cart-list")      

    
class PlaceOrderView(View):

    def get(self,request,*args,**kwargs):

        return render(request,"place_order.html")
    
    def post(self,request,*args,**kwargs):

        email=request.POST.get("email")

        phone=request.POST.get("phone")

        address=request.POST.get("address")

        payment_mode=request.POST.get("payment_mode")

        pin=request.POST.get("pin")

        cart_item_objects=request.user.cart.cartitems.filter(is_order_placed=False)

        if payment_mode=="cod":

            order_obj=Order.objects.create(

             user_object=request.user,

             delivery_address=address,

             phone=phone,

             pin=pin,

             email=email,

             payment_mode=payment_mode

            )

            for bi in cart_item_objects:

                order_obj.basket_item_objects.add(bi)

                bi.is_order_placed=True

                bi.save()

            order_obj.save()    

        return redirect("index")       
    

class OrderSummaryView(View):

    def get(self,request,*args,**kwargs):

        qs=Order.objects.filter(user_object=request.user).order_by("-created_date")    

        return render(request,"orders.html",{"data":qs})    
    