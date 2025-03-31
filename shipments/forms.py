from django import forms

TRACKING_CHOICES = [
    ('container', 'Container Number'),
    ('hbl', 'HBL Number'),
    ('hawb', 'HAWB Number'),
    ('shipping_bill', 'Shipping Bill Number'),
    ('booking', 'Booking Number'),
]

class TrackingForm(forms.Form):
    tracking_type = forms.ChoiceField(choices=TRACKING_CHOICES)
    reference_number = forms.CharField(max_length=50)