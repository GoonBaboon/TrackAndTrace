from django.shortcuts import render, get_object_or_404
from .models import Container, HBL, HAWB, ShippingBill, Booking, Company
from .forms import TrackingForm
from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, HttpResponseServerError
from django.template.loader import render_to_string
from weasyprint import HTML
import logging

logger = logging.getLogger(__name__)

def hawb_pdf(request, company_code, hawb_number):
    try:
        # 1. Get HAWB object (404 if not found)
        hawb = get_object_or_404(
            HAWB,
            hawb_number=hawb_number,
            company__code=company_code
        )
        
        # 2. Render HTML template
        context = {'hawb': hawb}
        html_string = render_to_string(
            'shipments/hawb_results_pdf.html', 
            context
        )
        
        # 3. Generate PDF with WeasyPrint
        try:
            html = HTML(
                string=html_string,
                base_url=request.build_absolute_uri()
            )
            pdf = html.write_pdf()
        except Exception as pdf_error:
            logger.error(f"PDF generation failed: {str(pdf_error)}")
            return HttpResponseServerError(
                "PDF generation failed. Please try again later."
            )
        
        # 4. Return PDF response
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"HAWB_{hawb.hawb_number}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response

    except Exception as e:
        logger.critical(f"Unexpected error in hawb_pdf: {str(e)}", exc_info=True)
        return HttpResponseServerError(
            "An unexpected error occurred. Our team has been notified."
        )


def track_shipment(request):
    if request.method == 'GET':
        form = TrackingForm(request.GET)
        if form.is_valid():
            tracking_type = form.cleaned_data['tracking_type']
            ref_number = form.cleaned_data['reference_number']
            company_code = request.GET.get('company_code', 'DSM0')  # Default example
            
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
    container = get_object_or_404(
        Container,
        container_number=container_number,
        company__code=company_code
    )
    return render(request, 'shipments/container_results.html', {'container': container})

def hbl_tracking(request, company_code, hbl_number):
    hbl = get_object_or_404(
        HBL,
        hbl_number=hbl_number,
        company__code=company_code
    )
    return render(request, 'shipments/hbl_results.html', {'hbl': hbl})

def hawb_tracking(request, company_code, hawb_number):
    hawb = get_object_or_404(
        HAWB,
        hawb_number=hawb_number,
        company__code=company_code
    )
    return render(request, 'shipments/hawb_results.html', {'hawb': hawb})

def shipping_bill_tracking(request, company_code, shipping_bill_number):
    shipping_bill = get_object_or_404(
        ShippingBill,
        shipping_bill_number=shipping_bill_number,
        company__code=company_code
    )
    return render(request, 'shipments/shipping_bill_results.html', {'shipping_bill': shipping_bill})

def booking_tracking(request, company_code, booking_number):
    booking = get_object_or_404(
        Booking,
        booking_number=booking_number,
        company__code=company_code
    )
    return render(request, 'shipments/booking_results.html', {'booking': booking})