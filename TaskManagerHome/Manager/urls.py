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
    url(r'^hot$', views.get_hot_tasks, name='hot'),
    url(r'^stat/(?P<roadmap_id>.*)/$', views.stat, name='roadmap_stat'),
    url(r'^signup$', views.sign_up, name='signup'),
    url(r'^signin$', views.sign_in, name='signin'),
    url(r'^logout$', views.log_out, name='logout'),
    url(r'^profile$', views.profile, name='profile'),
    url(r'^edit_profile$', views.edit_profile, name='edit_profile'),
    url(r'^change_password$', views.change_password, name='change_password')
]
