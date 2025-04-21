from django.urls import path
from django.contrib import admin
from . import views

urlpatterns = [
    path('', views.login, name='login'),
    path('logout', views.logout, name='logout'),
    path('audit', views.audit_list, name='audit_list'),
    path('audit/<int:pk>/', views.audit_detail, name='audit_detail'),
    path('audit/new/', views.audit_new, name='audit_new'),
    path('audit/<int:pk>/edit/', views.audit_edit, name='audit_edit'),
    path('audit/<int:pk>/delete/', views.audit_delete, name='audit_delete'),
    path('audit/<int:audit_pk>/inspection/<int:pk>/', views.audit_inspection_detail, name='audit_inspection_detail'),
    path('audit/<int:audit_pk>/inspections/new/', views.audit_inspection_new, name='audit_inspection_new'),
    path('audit/<int:audit_pk>/inspections/<int:pk>/edit/', views.audit_inspection_edit, name='audit_inspection_edit'),
    path('audit/<int:audit_pk>/inspections/<int:pk>/delete/', views.audit_inspection_delete, name='audit_inspection_delete'),
    path('audit/<int:audit_pk>/inspections/<int:pk>/finish/', views.finish_inspection, name='finish_inspection'),
    path('audit/<int:audit_pk>/inspections/<int:pk>/send-report/', views.send_inspection_report, name='send_inspection_report'),

]
