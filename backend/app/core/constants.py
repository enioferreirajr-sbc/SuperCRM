from decimal import Decimal
from datetime import datetime
from typing import Any, Optional

def parse_currency(v: Any) -> Decimal:
    if pd.isna(v) or v == "":
        return Decimal(0)
    if isinstance(v, (int, float, Decimal)):
        return Decimal(v)
    if isinstance(v, str):
        clean = v.replace("R$", "").replace(" ", "").replace(".", "").replace(",", ".")
        if not clean:
            return Decimal(0)
        try:
            return Decimal(clean)
        except:
            return Decimal(0)
    return Decimal(0)

def parse_date(v: Any) -> Optional[datetime]:
    if pd.isna(v) or v == "" or str(v).strip() == "":
        return None
    if isinstance(v, datetime):
        return v
    # Try parsing common formats if needed, or rely on Pandas parsing
    return None

import pandas as pd

PROPOSAL_IMPORT_SCHEMA = {
    "Business Proposal ID": {"field": "business_proposal_id", "type": "int"},
    "Customer Reference": {"field": "customer_reference", "type": "str"},
    "Business Proposal Date": {"field": "business_proposal_date", "type": "date"},
    "Last Status Date": {"field": "last_status_date", "type": "date"},
    "Funnel Percentage": {"field": "funnel_percentage", "type": "str"},
    "Business Proposal Name": {"field": "business_proposal_name", "type": "str"},
    "Business Proposal Status": {"field": "business_proposal_status", "type": "str"},
    "Last Note": {"field": "last_note", "type": "str"},
    "Recipient Name": {"field": "recipient_name", "type": "str"},
    "Recipient E-mail": {"field": "recipient_e_mail", "type": "str"},
    "Funnel Percentage ID": {"field": "funnel_percentage_id", "type": "str"},
    "Aging Business Proposal": {"field": "aging_business_proposal", "type": "str"},
    "Aging Status": {"field": "aging_status", "type": "str"},
    
    # Check if these are Item fields or Header fields?
    # Based on previous file, these vary per item:
    "Product Name": {"field": "product_name", "type": "str"},
    "Proposal Type Name": {"field": "proposal_type_name", "type": "str"},
    "Team Name": {"field": "team_name", "type": "str"},
    "Owner": {"field": "owner", "type": "str"},
    
    # Metrics
    "R$ License of Use": {"field": "license_of_use", "type": "currency"},
    "R$ Training": {"field": "training", "type": "currency"},
    "R$ Monthly Fee": {"field": "monthly_fee", "type": "currency"},
    "R$ Professional Services": {"field": "professional_services", "type": "currency"},
    "Monthly Fee (Annualized)": {"field": "monthly_fee_annualized", "type": "currency"},
    "R$ Total Sales": {"field": "total_sales", "type": "currency"},
}
