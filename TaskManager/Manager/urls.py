from django.conf.urls import url
from Manager import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.task_form, name='add_task'),
]
