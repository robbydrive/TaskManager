from django.conf.urls import url
from Manager import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^add/$', views.add_task, name='add_task'),
    url(r'^edit/(?P<task_title>.+)/$', views.edit_task, name='edit_task')
]
