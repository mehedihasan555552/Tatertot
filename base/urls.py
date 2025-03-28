from django.urls import path, re_path
from . import views
from django.urls import path


from .views import FireTVFeedAPI, RokuFeedAPI





urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.userlogout, name='logout'),

    # Show management
    path('shows/add/', views.add_show, name='add_show'),
    path('shows/<int:pk>/edit/', views.edit_show, name='edit_show'),
    path('shows/<int:pk>/delete/', views.delete_show, name='delete_show'),
    re_path(r'^shows/(?P<pk>\d+)/move/(?P<direction>-?\d+)/$', views.move_show, name='move_show'),

    # Episode management
    path('shows/<int:show_id>/episodes/add/', views.add_episode, name='add_episode'),
    path('episodes/<int:pk>/edit/', views.edit_episode, name='edit_episode'),
    path('episodes/<int:pk>/delete/', views.delete_episode, name='delete_episode'),
    re_path(r'^episodes/(?P<pk>\d+)/move/(?P<direction>-?\d+)/$', views.move_episode, name='move_episode'),

    # Settings and publishing
    path('settings/', views.settings, name='settings'),
    path('settings/update/', views.update_settings, name='update_settings'),
    path('publish/', views.publish, name='publish'),


    path('firetv/feed/', FireTVFeedAPI.as_view(), name='firetv-feed'),
    path('roku/feed/', RokuFeedAPI.as_view(), name='roku-feed'),
]
