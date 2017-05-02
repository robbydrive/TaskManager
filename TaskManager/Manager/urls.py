from django.conf.urls import url
from Manager import views

urlpatterns = [
    url(r'^$', views.index, name='index'),
    url(r'^tasks/(?:(?P<roadmap_id>.*)/)?$', views.tasks, name='tasks'),
    url(r'^add_task/(?:(?P<roadmap_id>.*)/)?$', views.add_task, name='add_task'),
    url(r'^edit_task/(?P<task_id>.+)/$', views.edit_task, name='edit_task'),
    url(r'^delete_task/(?P<task_id>.+)/$', views.delete_task, name='delete_task'),
    url(r'^roadmaps/$', views.roadmaps, name='roadmaps'),
    url(r'^add_roadmap/$', views.add_roadmap, name='add_roadmap'),
    url(r'^delete_roadmap/(?P<roadmap_id>.+)/$', views.delete_roadmap, name='delete_roadmap'),
]
