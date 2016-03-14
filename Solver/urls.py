from django.conf.urls import url

from . import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^a_star/', views.a_star, name='a_star'),
    url(r'^uniform_cost/', views.uniform_cost, name='uniform_cost')
]