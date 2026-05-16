from django.urls import path
from . import views
urlpatterns=[
    path('',views.home_view,name='home'),
    path('home',views.home_view,name='home'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('expenses', views.expenses_view, name='expenses'),
    path('bike_expenses', views.bike_expenses_view, name='bike_expenses'),
    path('report_expense', views.expense_report, name='report_expense'),
    path('get-bank-total/', views.get_bank_total, name='get_bank_total'),

]