from django.urls import path
from django.views.generic import TemplateView
from . import views
urlpatterns=[
    path('',views.home_page,name='home_page'),
    path('home',views.home_page,name='home'),
    path('home_dashboard',views.home_view_dashboard,name='home_dashboard'),
    path('signup', views.signup_view, name='signup'),
    path('login', views.login_view, name='login'),
    path('logout', views.logout_view, name='logout'),
    path('expenses', views.expenses_view, name='expenses'),
    path('bike_expenses', views.bike_expenses_view, name='bike_expenses'),
    path("bike_expenses/report/", views.bike_report_view, name="bike_report"),
    path("bike_expenses/report/download/", views.bike_report_download, name="bike_report_download"),
    path('report_expense', views.expense_report, name='report_expense'),
    path('payment_method', views.payment_method, name='payment_method'),
    path('get-bank-total/', views.get_bank_total, name='get_bank_total'),
    path('self-transfer/', views.self_transfer, name='self_transfer'),
    path('manifest.json', TemplateView.as_view(
        template_name='manifest.json',
        content_type='application/json'
    ), name='manifest'),

]