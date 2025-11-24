from django.urls import path
from django.contrib.auth.views import LogoutView
from .views import (
    signup_view, login_view, role_selection_view, 
    profile_creation_view, dashboard_view, home_view
)

urlpatterns = [
    path('signup/', signup_view, name='signup'),
    path('login/', login_view, name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('role-selection/', role_selection_view, name='role_selection'),
    path('profile-creation/', profile_creation_view, name='profile_creation'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('', home_view, name='home'),
]
