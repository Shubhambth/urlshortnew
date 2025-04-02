from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    path('', views.landing_page, name='landing_page'),
    path('shorten/', views.shorten_url, name='shorten_url'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('analytics/<int:url_id>/', views.url_analytics, name='url_analytics'),
    path('toggle/<int:url_id>/', views.toggle_url, name='toggle_url'),
    path('signup/', views.signup, name='signup'),
    path('login/', auth_views.LoginView.as_view(template_name='shortener/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('withdraw/', views.withdraw_payment, name='withdraw_payment'),
    path('<str:short_code>/', views.redirect_to_original, name='redirect'),
] 