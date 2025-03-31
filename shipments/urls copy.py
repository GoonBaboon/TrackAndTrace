from django.urls import path
from . import views

urlpatterns = [
    path('track/', views.track_shipment, name='track'),
    path('container/<str:company_code>/<str:container_number>/', views.container_tracking, name='container_tracking'),
    path('hbl/<str:company_code>/<str:hbl_number>/', views.hbl_tracking, name='hbl_tracking'),
    path('hawb/<str:company_code>/<str:hawb_number>/pdf/', views.hawb_pdf, name='hawb_pdf'),
    path('hawb/<str:company_code>/<str:hawb_number>/', views.hawb_tracking, name='hawb_tracking'),
    path('shipping-bill/<str:company_code>/<str:shipping_bill_number>/', views.shipping_bill_tracking, name='shipping_bill_tracking'),
    path('booking/<str:company_code>/<str:booking_number>/', views.booking_tracking, name='booking_tracking'),
]