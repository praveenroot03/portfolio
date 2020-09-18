from django.urls import path

from mainPage import views

app_name = 'mainPage'

urlpatterns = [
    path('', views.index, name='index'),
    path('getImg/<str:types>', views.serve_image, name='serve_image')
]
