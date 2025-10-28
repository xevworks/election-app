from django.db import migrations
from django.utils import timezone
from datetime import datetime, time


def convert_dates_to_datetimes(apps, schema_editor):
    """Convert existing date fields to datetime fields"""
    Election = apps.get_model('core', 'Election')
    
    for election in Election.objects.all():
        # Check if start_date is a date object (not datetime)
        if hasattr(election.start_date, 'year') and not hasattr(election.start_date, 'hour'):
            # It's a date object, convert to datetime
            start_datetime = timezone.make_aware(
                datetime.combine(election.start_date, time(0, 0))  # 00:00
            )
            election.start_date = start_datetime
        
        # Check if end_date is a date object (not datetime)
        if hasattr(election.end_date, 'year') and not hasattr(election.end_date, 'hour'):
            # It's a date object, convert to datetime
            end_datetime = timezone.make_aware(
                datetime.combine(election.end_date, time(23, 59))  # 23:59
            )
            election.end_date = end_datetime
        
        election.save()


def reverse_conversion(apps, schema_editor):
    """Reverse migration - convert datetime back to date"""
    Election = apps.get_model('core', 'Election')
    
    for election in Election.objects.all():
        if hasattr(election.start_date, 'date'):
            election.start_date = election.start_date.date()
        if hasattr(election.end_date, 'date'):
            election.end_date = election.end_date.date()
        election.save()


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0005_alter_election_end_date_alter_election_start_date'),
    ]

    operations = [
        migrations.RunPython(convert_dates_to_datetimes, reverse_conversion),
    ]