from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
from weasyprint import HTML
from .models import Container, HBL, HAWB, ShippingBill, Booking, Company
from .forms import TrackingForm
import logging

logger = logging.getLogger(__name__)

# ========================
# PDF GENERATION VIEWS
# ========================

def generate_pdf_response(html_string, request, filename_prefix):
    """Helper function for PDF generation"""
    try:
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="{filename_prefix}.pdf"'
        return response
    except Exception as e:
        logger.error(f"PDF generation failed: {str(e)}")
        return HttpResponseServerError("PDF generation failed. Please try again later.")

def hawb_pdf(request, company_code, hawb_number):
    try:
        hawb = get_object_or_404(HAWB, hawb_number=hawb_number, company__code=company_code)
        html_string = render_to_string('shipments/hawb_results_pdf.html', {'hawb': hawb})
        return generate_pdf_response(html_string, request, f"HAWB_{hawb.hawb_number}")
    except Exception as e:
        logger.critical(f"Unexpected error in hawb_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError("An unexpected error occurred.")

def hbl_pdf(request, company_code, hbl_number):
    try:
        hbl = get_object_or_404(HBL, hbl_number=hbl_number, company__code=company_code)
        html_string = render_to_string('shipments/hbl_results_pdf.html', {'hbl': hbl})
        return generate_pdf_response(html_string, request, f"HBL_{hbl.hbl_number}")
    except Exception as e:
        logger.critical(f"Unexpected error in hbl_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError("An unexpected error occurred.")

def container_pdf(request, company_code, container_number):
    try:
        container = get_object_or_404(Container, container_number=container_number, company__code=company_code)
        html_string = render_to_string('shipments/container_results_pdf.html', {'container': container})
        return generate_pdf_response(html_string, request, f"CONTAINER_{container.container_number}")
    except Exception as e:
        logger.critical(f"Unexpected error in container_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError("An unexpected error occurred.")

def shipping_bill_pdf(request, company_code, shipping_bill_number):
    try:
        shipping_bill = get_object_or_404(ShippingBill, shipping_bill_number=shipping_bill_number, company__code=company_code)
        html_string = render_to_string('shipments/shipping_bill_results_pdf.html', {'shipping_bill': shipping_bill})
        return generate_pdf_response(html_string, request, f"SHIPPING_BILL_{shipping_bill.shipping_bill_number}")
    except Exception as e:
        logger.critical(f"Unexpected error in shipping_bill_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError("An unexpected error occurred.")

def booking_pdf(request, company_code, booking_number):
    try:
        booking = get_object_or_404(Booking, booking_number=booking_number, company__code=company_code)
        html_string = render_to_string('shipments/booking_results_pdf.html', {'booking': booking})
        return generate_pdf_response(html_string, request, f"BOOKING_{booking.booking_number}")
    except Exception as e:
        logger.critical(f"Unexpected error in booking_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError("An unexpected error occurred.")

# ========================
# TRACKING VIEWS
# ========================

def track_shipment(request):
    if request.method == 'GET':
        form = TrackingForm(request.GET)
        if form.is_valid():
            tracking_type = form.cleaned_data['tracking_type']
            ref_number = form.cleaned_data['reference_number']
            company_code = request.GET.get('company_code', 'DSM0')
            
            if tracking_type == 'container':
                return container_tracking(request, company_code, ref_number)
            elif tracking_type == 'hbl':
                return hbl_tracking(request, company_code, ref_number)
            elif tracking_type == 'hawb':
                return hawb_tracking(request, company_code, ref_number)
            elif tracking_type == 'shipping_bill':
                return shipping_bill_tracking(request, company_code, ref_number)
            elif tracking_type == 'booking':
                return booking_tracking(request, company_code, ref_number)
    else:
        form = TrackingForm()
    return render(request, 'shipments/track.html', {'form': form})

def container_tracking(request, company_code, container_number):
    container = get_object_or_404(Container, container_number=container_number, company__code=company_code)
    return render(request, 'shipments/container_results.html', {'container': container})

def hbl_tracking(request, company_code, hbl_number):
    hbl = get_object_or_404(HBL, hbl_number=hbl_number, company__code=company_code)
    return render(request, 'shipments/hbl_results.html', {'hbl': hbl})

def hawb_tracking(request, company_code, hawb_number):
    hawb = get_object_or_404(HAWB, hawb_number=hawb_number, company__code=company_code)
    return render(request, 'shipments/hawb_results.html', {'hawb': hawb})

def shipping_bill_tracking(request, company_code, shipping_bill_number):
    shipping_bill = get_object_or_404(ShippingBill, shipping_bill_number=shipping_bill_number, company__code=company_code)
    return render(request, 'shipments/shipping_bill_results.html', {'shipping_bill': shipping_bill})

def booking_tracking(request, company_code, booking_number):
    booking = get_object_or_404(Booking, booking_number=booking_number, company__code=company_code)
    return render(request, 'shipments/booking_results.html', {'booking': booking})