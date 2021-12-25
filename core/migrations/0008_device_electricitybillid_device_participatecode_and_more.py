# Generated by Django 4.0 on 2021-12-25 07:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0007_device_bill_type_inquiry_abonman_inquiry_address_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='device',
            name='ElectricityBillID',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='ElectricityBillID'),
        ),
        migrations.AddField(
            model_name='device',
            name='ParticipateCode',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='ParticipateCode'),
        ),
        migrations.AddField(
            model_name='device',
            name='WaterBillID',
            field=models.CharField(blank=True, max_length=50, null=True, verbose_name='WaterBillID'),
        ),
    ]