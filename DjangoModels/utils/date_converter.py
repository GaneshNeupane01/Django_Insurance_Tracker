import nepali_datetime as nd
from datetime import date, datetime

def ad_to_bs(ad_date: date) -> str:
    if not ad_date:
        return None

    if isinstance(ad_date, datetime):
        ad_date = ad_date.date()
    bs = nd.date.from_datetime_date(ad_date)
    return f"{bs.year}-{bs.month:02d}-{bs.day:02d}"

def bs_to_ad(bs_year: int, bs_month: int, bs_day: int) -> date:
    bs = nd.date(bs_year, bs_month, bs_day)
    return bs.to_datetime_date()
