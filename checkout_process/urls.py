from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^cart/$', views.CartView.as_view()),
    url(r'^review/$', views.CheckoutView.as_view()),
    url(r'^purchase-complete/$', views.PurchaseView.as_view()),

]
