

from django.db import migrations

def create_initial_companies_and_plans(apps, schema_editor):
    InsuranceCompany = apps.get_model('insurance', 'InsuranceCompany')
    InsurancePlan = apps.get_model('insurance', 'InsurancePlan')

    # Create some predefined companies
    companies_data = [
        "Nepal Life Insurance",
        "Shikhar Insurance",
        "Sagarmatha Insurance",
    ]

    companies = {}

    for name in companies_data:
        company, created = InsuranceCompany.objects.get_or_create(name=name)
        companies[name] = company

    # Define plans for each company
    plans = [
        # Nepal Life Insurance
        {"company": companies["Nepal Life Insurance"], "vehicle_type": "Car", "payment_mode": "yearly", "amount": 12000},
  {"company": companies["Nepal Life Insurance"], "vehicle_type": "Car", "payment_mode": "monthly", "amount": 1000},
        {"company": companies["Nepal Life Insurance"], "vehicle_type": "Motorcycle", "payment_mode": "yearly", "amount": 3000},
        {"company": companies["Nepal Life Insurance"], "vehicle_type": "Bus", "payment_mode": "monthly", "amount": 2500},

        # Shikhar Insurance
        {"company": companies["Shikhar Insurance"], "vehicle_type": "Car", "payment_mode": "monthly", "amount": 1500},
 {"company": companies["Shikhar Insurance"], "vehicle_type": "Car", "payment_mode": "yearly", "amount": 15000},
 {"company": companies["Shikhar Insurance"], "vehicle_type": "Motorcycle", "payment_mode": "yearly", "amount": 10000},
 {"company": companies["Shikhar Insurance"], "vehicle_type": "Motorcycle", "payment_mode": "monthly", "amount": 1000},
        {"company": companies["Shikhar Insurance"], "vehicle_type": "Truck", "payment_mode": "yearly", "amount": 18000},

        # Sagarmatha Insurance
        {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Motorcycle", "payment_mode": "monthly", "amount": 400},
   {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Motorcycle", "payment_mode": "yearly", "amount": 4000},
   {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Car", "payment_mode": "monthly", "amount": 1200},
   {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Car", "payment_mode": "yearly", "amount": 11000},
        {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Truck", "payment_mode": "monthly", "amount": 2200},
        {"company": companies["Sagarmatha Insurance"], "vehicle_type": "Bus", "payment_mode": "yearly", "amount": 15000},
    ]

    for plan in plans:
        InsurancePlan.objects.get_or_create(
            company=plan["company"],
            vehicle_type=plan["vehicle_type"],
            payment_mode=plan["payment_mode"],
            defaults={"amount": plan["amount"]}
        )


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0005_alter_insuranceplan_vehicle_type'),  # Adjust if needed
    ]

    operations = [
        migrations.RunPython(create_initial_companies_and_plans),
    ]