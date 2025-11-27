import nepali_datetime as nd
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta

def ad_to_bs(ad_date: date) -> str:
    # ...existing code...
    if not ad_date:
        return None
    if isinstance(ad_date, datetime):
        ad_date = ad_date.date()
    bs = nd.date.from_datetime_date(ad_date)
    month_name = bs.strftime('%B')
    return f"{bs.year} {month_name} {bs.day}"

def ad_to_bs_date(ad_date: date) -> nd.date:
    # ...existing code...
    if not ad_date:
        return None
    if isinstance(ad_date, datetime):
        ad_date = ad_date.date()
    return nd.date.from_datetime_date(ad_date)

def add_years_in_bs(ad_date, years=1, hour=5, minute=45) -> datetime:
    # Increment by BS years, handling invalid end-of-month cases.
    if not ad_date:
        return None
    if isinstance(ad_date, datetime):
        ad_date = ad_date.date()

    bs = nd.date.from_datetime_date(ad_date)
    print(f"Original BS date: {bs}")
    target_year = bs.year + years
    month = bs.month
    day = bs.day

    while True:
        try:
            next_bs = nd.date(target_year, month, day)
            break
        except ValueError:
            day -= 1
            if day < 1:
                raise ValueError("No valid day found in target month/year.")
    print(f"Next BS date after adding {years} years: {next_bs}")
    ad_date = next_bs.to_datetime_date()
    return datetime.combine(ad_date, time(hour, minute))

def bs_to_ad(bs_year: int, bs_month: int, bs_day: int) -> date:
    # ...existing code...
    bs = nd.date(bs_year, bs_month, bs_day)
    return bs.to_datetime_date()