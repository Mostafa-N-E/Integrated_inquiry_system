from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

DEVICE_TYPE = [
    ('phone','phone'),
    ('car','car'),
]
OPERATORS = [
    ('Irancell','Irancell'),
    ('Hamrahavval','Hamrahavval'),
    ('Rightel','Rightel'),
]
TYPELINE = [
    ('Mobile','Mobile'),
    ('FixedLine','FixedLine'),
]

class Device(models.Model):
    owner = models.ForeignKey(
        User, 
        on_delete=models.CASCADE,
        related_name='owner', 
        blank=True, null=True
    )
    name = models.CharField(
        max_length=50, 
        verbose_name='name', 
        blank=True, null=True
    )
    is_active = models.BooleanField(
        verbose_name='is_active', 
        blank=True, null=True
    )
    description = models.CharField(
        max_length=250, 
        verbose_name='description', 
        blank=True, null=True
    )
    last_inquiry = models.DateField(
        auto_now_add=True, 
        verbose_name='last inquiry', 
        blank=True, null=True
    )
    device_type = models.CharField(
        max_length=50, 
        verbose_name='device_type',
        choices=DEVICE_TYPE, 
        blank=True, null=True
    )

    # phone
    Number = models.CharField(
        max_length=50, 
        blank=True, null=True
    )
    Operator = models.CharField(
        max_length=50, 
        verbose_name='Operator',
        choices=OPERATORS, 
        blank=True, null=True
    )
    TypeLine = models.CharField(
        max_length=50, 
        verbose_name='TypeLine',
        choices=TYPELINE, 
        blank=True, null=True
    )
    # car
    BarCode = models.CharField(
        max_length=100, 
        blank=True, null=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'


class Inquiry(models.Model):
    device = models.ForeignKey(
        Device, 
        on_delete=models.CASCADE,
        related_name='device',
        blank=True, null=True
     )

    Code = models.CharField(
        max_length=100, 
        verbose_name='Code', 
        blank=True, null=True
    )
    Description = models.CharField(
        max_length=50, 
        verbose_name='Description', 
        blank=True, null=True
    )

    Amount = models.IntegerField(
        verbose_name='Amount', 
        blank=True, null=True   
    )
    BillID = models.CharField(
        max_length=50,
        verbose_name='BillID', 
        blank=True, null=True
    )
    PaymentID = models.CharField(
        max_length=50,
        verbose_name='PaymentID', 
        blank=True, null=True
    )
    # Phone
    PreviousDate = models.CharField(
        max_length=50,
        verbose_name='PreviousDate', 
        blank=True, null=True
    )
    CurrentDate = models.CharField(
        max_length=50,
        verbose_name='CurrentDate', 
        blank=True, null=True
    )
    PaymentDate = models.CharField(
        max_length=50,
        verbose_name='PaymentDate', 
        blank=True, null=True
    )
    FullName = models.CharField(
        max_length=50,
        verbose_name='FullName', 
        blank=True, null=True
    )
    Cycle = models.CharField(
        max_length=50, 
        verbose_name='Cycle', 
        blank=True, null=True
    )
    TraceNumber = models.CharField(
        max_length=100, 
        blank=True, null=True
    )

    MidTerm_Amount = models.CharField(
        max_length=50,
        verbose_name='MidTerm_Amount', 
        blank=True, null=True
    )
    MidTerm_BillID = models.CharField(
        max_length=50,
        verbose_name='MidTerm_BillID', 
        blank=True, null=True
    )
    MidTerm_PaymentID = models.CharField(
        max_length=50, 
        verbose_name='MidTerm_PaymentID', 
        blank=True, null=True
    )
    FinalTerm_Amount = models.CharField(
        max_length=50,
        verbose_name='FinalTerm_Amount', 
        blank=True, null=True
    )
    FinalTerm_BillID = models.CharField(
        max_length=50,
        verbose_name='FinalTerm_BillID', 
        blank=True, null=True
    )
    FinalTerm_PaymentID = models.CharField(
        max_length=50, 
        verbose_name='FinalTerm_PaymentID', 
        blank=True, null=True
    )
    # Car
    PlateNumber = models.CharField(
        max_length=50,
        verbose_name='PlateNumber', 
        blank=True, null=True
    )
    TotalAmount = models.CharField(
        max_length=50,
        verbose_name='TotalAmount', 
        blank=True, null=True
    )
    Details = models.CharField(
        max_length=50, 
        verbose_name='Details', 
        blank=True, null=True
    )
    City = models.CharField(
        max_length=50,
        verbose_name='City', 
        blank=True, null=True
    )
    Location = models.CharField(
        max_length=50,
        verbose_name='Location', 
        blank=True, null=True
    )
    Type = models.CharField(
        max_length=50, 
        verbose_name='Type', 
        blank=True, null=True
    )
    DateTime = models.CharField(
        max_length=50, 
        verbose_name='DateTime', 
        blank=True, null=True
    )
    Delivery = models.CharField(
        max_length=50,
        verbose_name='Delivery', 
        blank=True, null=True
    )
    SerialNumber = models.CharField(
        max_length=50,
        verbose_name='SerialNumber', 
        blank=True, null=True
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Inquiry'
        verbose_name_plural = 'Inquiries'

    def __str__(self):
        return self.device.name

