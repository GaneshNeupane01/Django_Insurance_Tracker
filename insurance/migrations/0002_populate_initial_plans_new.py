from django.db import migrations

def create_initial_companies_and_plans(apps, schema_editor):
    InsuranceCompany = apps.get_model('insurance', 'InsuranceCompany')
    # 🛑 Get the newly created VehicleTier model
    VehicleTier = apps.get_model('insurance', 'VehicleTier')
    InsurancePlan = apps.get_model('insurance', 'InsurancePlan')

    companies_data = [
        "Sagarmatha Lumbini Insurance Company Ltd.",
        "Shikhar Insurance Co. Ltd.",
        "Neco Insurance Ltd.",
        "Himalayan Everest Insurance Limited",
        "NLG Insurance Company Ltd.",
        "Prabhu Insurance Ltd.",
        "IGI Prudential Insurance Limited",
    ]

    companies = {}
    for name in companies_data:
        company, _ = InsuranceCompany.objects.get_or_create(name=name)
        companies[name] = company

    # 2. Define all plan tiers (This data structure remains correct)
    plan_tiers_data = [
        # --- Private Vehicle (5 seater-EV) ---
        {
            "vehicle_type": "Private Vehicle (5 seater-EV)",
            "min_engine_wattage": 0, "max_engine_wattage": 19999,
            "amount": 7355.00,
        },
        {
            "vehicle_type": "Private Vehicle (5 seater-EV)",
            "min_engine_wattage": 20000, "max_engine_wattage": 999999,
            "amount": 8485.00,
        },

        # --- Motorcycles (Non-EV) ---
        {
            "vehicle_type": "Motorcycles",
            "min_engine_cc": 0, "max_engine_cc": 149,
            "amount": 1705.00,
        },
        {
            "vehicle_type": "Motorcycles",
            "min_engine_cc": 150, "max_engine_cc": 250,
            "amount": 1931.00,
        },
        {
            "vehicle_type": "Motorcycles",
            "min_engine_cc": 251, "max_engine_cc": 999999,
            "amount": 2157.00,
        },

        # --- Motorcycles (EV) ---
        {
            "vehicle_type": "Motorcycles (EV)",
            "min_engine_wattage": 0, "max_engine_wattage": 799,
            "amount": 1706.30,
        },
        {
            "vehicle_type": "Motorcycles (EV)",
            "min_engine_wattage": 800, "max_engine_wattage": 1199,
            "amount": 1932.30,
        },
        {
            "vehicle_type": "Motorcycles (EV)",
            "min_engine_wattage": 1200, "max_engine_wattage": 999999,
            "amount": 2158.30,
        },

        # --- Private Vehicle (5 seater) (CC) ---
        {
            "vehicle_type": "Private Vehicle (5 seater)",
            "min_engine_cc": 0, "max_engine_cc": 999,
            "amount": 7355.00,
        },
        {
            "vehicle_type": "Private Vehicle (5 seater)",
            "min_engine_cc": 1000, "max_engine_cc": 1600,
            "amount": 8485.00,
        },
        {
            "vehicle_type": "Private Vehicle (5 seater)",
            "min_engine_cc": 1601, "max_engine_cc": 999999,
            "amount": 10745.00,
        },
    ]

    # 3. Create unique VehicleTier objects and store them
    vehicle_tiers = {}

    for tier_data in plan_tiers_data:
        # Define the unique key for the tier (used to avoid duplicate tier creation)
        tier_key = (tier_data["vehicle_type"],
                    tier_data.get("min_engine_cc"), tier_data.get("max_engine_cc"),
                    tier_data.get("min_engine_wattage"), tier_data.get("max_engine_wattage"))

        if tier_key not in vehicle_tiers:
            # Create the unique VehicleTier object
            vehicle_tier, _ = VehicleTier.objects.get_or_create(
                vehicle_type=tier_data["vehicle_type"],
                min_engine_cc=tier_data.get("min_engine_cc"),
                max_engine_cc=tier_data.get("max_engine_cc"),
                min_engine_wattage=tier_data.get("min_engine_wattage"),
                max_engine_wattage=tier_data.get("max_engine_wattage"),
            )
            vehicle_tiers[tier_key] = vehicle_tier

        # 4. Create the InsurancePlan for every company, referencing the tier
        for company_name, company_obj in companies.items():
            InsurancePlan.objects.get_or_create(
                company=company_obj,
                # 🛑 Link using the Foreign Key: vehicle_tier
                vehicle_tier=vehicle_tiers[tier_key],

                # The only value in defaults is the amount
                defaults={
                    "amount": tier_data["amount"]
                }
            )


class Migration(migrations.Migration):

    dependencies = [
        ('insurance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_companies_and_plans),
    ]