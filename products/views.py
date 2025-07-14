from django.views.generic import ListView, DetailView, View
from django.shortcuts import render
from .models import Product
from .utils import CartMixin

class ProductListView(ListView):
    model = Product
    template_name = 'products/products.html'
    context_object_name = 'page_obj'
    paginate_by = 18

    def get_queryset(self):
        return Product.objects.all()

class ProductDetailView(DetailView):
    model = Product
    template_name = 'products/product.html'
    context_object_name = 'product'