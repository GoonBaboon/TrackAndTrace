from django.urls import path
from . import views

urlpatterns = [
    # Main tracking form
    path('track/', views.track_shipment, name='track'),
    
    # HAWB URLs
    path('hawb/<str:company_code>/<str:hawb_number>/', 
        views.hawb_tracking, name='hawb_tracking'),
    path('hawb/<str:company_code>/<str:hawb_number>/pdf/', 
        views.hawb_pdf, name='hawb_pdf'),
    
    # HBL URLs
    path('hbl/<str:company_code>/<str:hbl_number>/', 
        views.hbl_tracking, name='hbl_tracking'),
    path('hbl/<str:company_code>/<str:hbl_number>/pdf/', 
        views.hbl_pdf, name='hbl_pdf'),
    
    # Container URLs
    path('container/<str:company_code>/<str:container_number>/', 
        views.container_tracking, name='container_tracking'),
    path('container/<str:company_code>/<str:container_number>/pdf/', 
        views.container_pdf, name='container_pdf'),
    
    # Shipping Bill URLs
    path('shipping-bill/<str:company_code>/<str:shipping_bill_number>/', 
        views.shipping_bill_tracking, name='shipping_bill_tracking'),
    path('shipping-bill/<str:company_code>/<str:shipping_bill_number>/pdf/', 
        views.shipping_bill_pdf, name='shipping_bill_pdf'),
    
    # Booking URLs
    path('booking/<str:company_code>/<str:booking_number>/', 
        views.booking_tracking, name='booking_tracking'),
    path('booking/<str:company_code>/<str:booking_number>/pdf/', 
        views.booking_pdf, name='booking_pdf'),
]