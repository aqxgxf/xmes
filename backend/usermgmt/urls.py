from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register),
    path('login/', views.user_login),
    path('userinfo/', views.user_info),
    path('users/', views.user_list),
    path('groups/', views.group_list),
    path('user/<int:user_id>/update/', views.update_user),
    path('group/<str:group_name>/update/', views.update_group),
    path('group/add/', views.add_group),
    path('group/<str:group_name>/delete/', views.delete_group),
    path('csrf/', views.get_csrf),
    path('menus/', views.menu_list),
    path('menu/save/', views.menu_save),
    path('menu/<int:menu_id>/delete/', views.menu_delete),
]
