from django.db import models
from django.core.exceptions import ValidationError

class Company(models.Model):
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.name} ({self.code})"

class Milestone(models.Model):
    MILESTONE_TYPES = [
        ('BOOKING', 'Booking Date'),
        ('PICKUP', 'Origin Pickup Date'),
        ('CARGO_RECEIVED', 'Cargo Received Date'),
        ('QC', 'QC Date'),
        ('EXPORT_CLEARANCE', 'Export Clearance Date'),
        ('LOADING', 'Loading Date'),
        ('ETD', 'ETD Date'),
        ('ETA', 'ETA Date'),
        ('CAN', 'CAN Date'),
        ('UNLOADING', 'Unloading Date'),
        ('IMPORT_CLEARANCE', 'Import Clearance Date'),
        ('CFS_ETA', 'CFS ETA'),
        ('DO', 'DO Date'),
        ('CARGO_PICKUP', 'Cargo Pickup Date'),
    ]
    
    code = models.CharField(max_length=20, choices=MILESTONE_TYPES, unique=True)
    name = models.CharField(max_length=100)
    description = models.TextField()
    date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.get_code_display()} - {self.name}"

class Container(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    container_number = models.CharField(max_length=20)
    obl_number = models.CharField(max_length=50)
    pol = models.CharField(max_length=100)  # Port of Loading
    pod = models.CharField(max_length=100)  # Port of Discharge
    cargo_details = models.ManyToManyField('CargoDetail', related_name='containers')
    etd = models.DateField()  # Estimated Time of Departure
    eta = models.DateField()  # Estimated Time of Arrival
    vessel = models.CharField(max_length=100)
    voyage = models.CharField(max_length=50)
    cfs = models.CharField(max_length=100, blank=True)  # Container Freight Station
    milestones = models.ManyToManyField(Milestone,blank=True)

    def __str__(self):
        return f"Container {self.container_number} ({self.vessel} {self.voyage})"


class CargoDetail(models.Model):
    hawb_or_hbl = models.CharField(max_length=50)
    description = models.TextField()
    packages = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    container = models.ForeignKey(Container, on_delete=models.CASCADE)

class HBL(models.Model):
    container = models.ForeignKey(Container, on_delete=models.CASCADE, null=True, blank=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    hbl_number = models.CharField(max_length=50, unique=True)
    obl_number = models.CharField(max_length=50, blank=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    packages = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    delivery_place = models.CharField(max_length=100, blank=True)
    delivery_order = models.CharField(max_length=50, blank=True)
    delivery_date = models.DateField(null=True, blank=True)
    shipping_bill = models.CharField(max_length=50, blank=True)
    driver = models.CharField(max_length=100, blank=True)
    truck_number = models.CharField(max_length=20, blank=True)
    pickup_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('BOOKED', 'Booked'),
        ('IN_TRANSIT', 'In Transit'),
        ('ARRIVED', 'Arrived'), 
        ('DELIVERED', 'Delivered')
    ], default='BOOKED')
    remarks = models.TextField(blank=True)
    milestones = models.ManyToManyField(Milestone, blank=True)

    # 1. Booking Date
    def get_booking_date(self):
        """When customer books the shipment (PDF page 6)"""
        return self._get_milestone_date('BOOKING')

    # 2. Origin Pickup Date  
    def get_pickup_date(self):
        """When picked up from shipper's warehouse (PDF page 6)"""
        return self._get_milestone_date('PICKUP') or self.pickup_date

    # 3. Cargo Received Date
    def get_cargo_received_date(self):
        """When received at Container Freight Station (PDF page 6)""" 
        return self._get_milestone_date('CARGO_RECEIVED')

    # 4. QC Date
    def get_qc_date(self):
        """Quality Control completion date (PDF page 6)"""
        return self._get_milestone_date('QC')

    # 5. Export Clearance Date
    def get_export_clearance_date(self):
        """Customs clearance for export (PDF page 6)"""
        return self._get_milestone_date('EXPORT_CLEARANCE')

    # 6. Loading Date
    def get_loading_date(self):
        """Loaded into container (PDF page 6)"""
        if self.container:
            return self._get_milestone_date('LOADING') or self.container.etd
        return None

    # 7. ETD Date
    def get_etd(self):
        """Vessel departure date (PDF page 6)"""
        return self._get_milestone_date('ETD') or (self.container.etd if self.container else None)

    # 8. ETA Date  
    def get_eta(self):
        """Arrival at destination (PDF page 6)"""
        return self._get_milestone_date('ETA') or (self.container.eta if self.container else None)

    # 9. CAN Date
    def get_can_date(self):
        """Cargo Arrival Notice sent (PDF page 6)"""
        return self._get_milestone_date('CAN')

    # 10. Unloading Date
    def get_unloading_date(self):
        """Unloaded from container (PDF page 7)"""
        return self._get_milestone_date('UNLOADING')

    # 11. Import Clearance Date
    def get_import_clearance_date(self):
        """Customs clearance at destination (PDF page 7)"""
        return self._get_milestone_date('IMPORT_CLEARANCE')

    # 12. CFS ETA
    def get_cfs_eta(self):
        """Arrival at Container Freight Station (PDF page 7)"""
        return self._get_milestone_date('CFS_ETA')

    # 13. DO Date
    def get_do_date(self):
        """Delivery Order issued (PDF page 7)"""
        return self.delivery_date or self._get_milestone_date('DO')

    # 14. Cargo Pickup Date
    def get_cargo_pickup_date(self):
        """Consignee picks up shipment (PDF page 7)"""
        return self._get_milestone_date('CARGO_PICKUP')

    def _get_milestone_date(self, code):
        """Helper to get date for a milestone code"""
        milestone = self.milestones.filter(code=code).first()
        return milestone.date if milestone else None

    def get_vessel_info(self):
        """Formats vessel display as 'VESSELNAME/VOYAGE'"""
        if self.container:
            return f"{self.container.vessel}/{self.container.voyage}"
        return "Not Assigned"

    def clean(self):
        """Validation logic"""
        if self.delivery_date and self.pickup_date and self.delivery_date < self.pickup_date:
            raise ValidationError("Delivery date cannot be before pickup date")

    def __str__(self):
        container_ref = f" (Container: {self.container.container_number})" if self.container else ""
        return f"HBL {self.hbl_number} {self.origin}→{self.destination}{container_ref}"

    class Meta:
        verbose_name = "House Bill of Lading"
        verbose_name_plural = "House Bills of Lading"
        ordering = ['-delivery_date']
        indexes = [
            models.Index(fields=['hbl_number']),
            models.Index(fields=['origin', 'destination']),
        ]

class HAWB(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    hawb_number = models.CharField(max_length=50, unique=True)
    mawb_number = models.CharField(max_length=50, blank=True)  # Master Air Waybill
    gross_weight = models.DecimalField(max_digits=10, decimal_places=2)
    volume_weight = models.DecimalField(max_digits=10, decimal_places=2)
    chargeable_weight = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    delivery_order = models.CharField(max_length=50)
    delivery_date = models.DateField(null=True, blank=True)
    shipping_bill = models.CharField(max_length=50)
    packages = models.IntegerField(null=True, blank=True)
    airline = models.CharField(max_length=100, blank=True)  # e.g., "Emirates Airlines"
    flight_number = models.CharField(max_length=20, blank=True)  # e.g., "25362"
    status = models.CharField(max_length=20, choices=[
        ('BOOKED', 'Booked'),
        ('DEPARTED', 'Departed'),
        ('ARRIVED', 'Arrived'),
        ('DELIVERED', 'Delivered')
    ], default='BOOKED')
    remarks = models.TextField(blank=True)
    milestones = models.ManyToManyField(Milestone, blank=True)

    # Date getters for milestones
    def get_booking_date(self):
        return self._get_milestone_date('BOOKING')

    def get_shipment_ready_date(self):
        return self._get_milestone_date('PICKUP')

    def get_etd(self):
        return self._get_milestone_date('ETD')

    def get_eta(self):
        return self._get_milestone_date('ETA')

    def get_do_date(self):
        return self._get_milestone_date('DO')

    def _get_milestone_date(self, code):
        milestone = self.milestones.filter(code=code).first()
        return milestone.date if milestone else None

    def __str__(self):
        return f"HAWB {self.hawb_number} ({self.origin} → {self.destination})"

    class Meta:
        verbose_name = "HAWB"
        verbose_name_plural = "HAWBs"
        ordering = ['-delivery_date']

    def __str__(self):
        return f"HAWB {self.hawb_number} ({self.origin} → {self.destination})"

class ShippingBill(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    shipping_bill_number = models.CharField(max_length=50)
    origin = models.CharField(max_length=100)
    destination = models.CharField(max_length=100)
    packages = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    milestones = models.ManyToManyField(Milestone,blank=True)

    def __str__(self):
        return f"Shipping Bill {self.shipping_bill_number} ({self.origin} → {self.destination})"

class Booking(models.Model):
    company = models.ForeignKey(Company, on_delete=models.CASCADE)
    booking_number = models.CharField(max_length=50)
    obl_mawb = models.CharField(max_length=50)
    hbl_hawb = models.CharField(max_length=50)
    freight = models.CharField(max_length=50)
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    volume = models.DecimalField(max_digits=10, decimal_places=2)
    remarks = models.TextField(blank=True)
    milestones = models.ManyToManyField(Milestone,blank=True)

    def __str__(self):
        return f"Booking {self.booking_number} ({self.obl_mawb}) - {self.freight} freight"