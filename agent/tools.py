import json
import logging
import os
import urllib.request

from google.adk.tools.tool_context import ToolContext

logger = logging.getLogger(__name__)

MOCK_API_URL = os.getenv("MOCK_API_URL", "http://localhost:8001")


def _api_get(path: str) -> dict:
    url = f"{MOCK_API_URL}{path}"
    logger.info(f"  -> GET {url}")
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def _api_post(path: str, data: dict) -> dict:
    url = f"{MOCK_API_URL}{path}"
    logger.info(f"  -> POST {url}")
    body = json.dumps(data).encode()
    req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read())


def get_accounts(customer_id: str, tool_context: ToolContext, account_type: str = "") -> str:
    """Get all bank accounts for a customer. Optionally filter by account_type (Savings, Checking, Credit Card, Term Deposit, Debit Card)."""
    logger.info(f"--- TOOL: get_accounts (customer_id={customer_id}, type={account_type}) ---")
    params = f"?account_type={account_type}" if account_type else ""
    result = _api_get(f"/api/customers/{customer_id}/accounts{params}")
    return json.dumps(result)


def get_transactions(
    customer_id: str,
    tool_context: ToolContext,
    account_id: str = "",
    category: str = "",
    sort_by: str = "",
    count: int = 10,
) -> str:
    """Get transactions. Optionally filter by account_id or category. Use sort_by for sorting: 'amount_desc' for highest first, 'amount_asc' for lowest first, 'date_desc' for newest first, 'date_asc' for oldest first. Returns up to 'count' transactions."""
    logger.info(f"--- TOOL: get_transactions (customer={customer_id}, account={account_id}, category={category}, sort={sort_by}, count={count}) ---")
    params = f"?count={count}"
    if account_id:
        params += f"&account_id={account_id}"
    if category:
        params += f"&category={category}"
    if sort_by:
        params += f"&sort_by={sort_by}"
    result = _api_get(f"/api/customers/{customer_id}/transactions{params}")
    return json.dumps(result)


def get_spending_analytics(customer_id: str, tool_context: ToolContext) -> str:
    """Get spending analytics with category breakdown, top merchants, and month-over-month comparison."""
    logger.info(f"--- TOOL: get_spending_analytics (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}/spending-analytics")
    return json.dumps(result)


def get_loans(customer_id: str, tool_context: ToolContext) -> str:
    """Get all business loans and finance products (BetterBusiness Loan, Car & Equipment Finance, Business Overdraft)."""
    logger.info(f"--- TOOL: get_loans (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}/loans")
    return json.dumps(result)


def get_cards(customer_id: str, tool_context: ToolContext) -> str:
    """Get all business cards (credit cards and debit cards) for a customer."""
    logger.info(f"--- TOOL: get_cards (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}/cards")
    return json.dumps(result)


def get_merchant_services(customer_id: str, tool_context: ToolContext) -> str:
    """Get merchant services info: EFTPOS terminals, online payments, and monthly summary."""
    logger.info(f"--- TOOL: get_merchant_services (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}/merchant-services")
    return json.dumps(result)


def get_international_payments(customer_id: str, tool_context: ToolContext) -> str:
    """Get international payment history and details."""
    logger.info(f"--- TOOL: get_international_payments (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}/international-payments")
    return json.dumps(result)


def get_fx_rates(tool_context: ToolContext, currency: str = "") -> str:
    """Get current foreign exchange rates. Optionally specify a currency code (GBP, EUR, AUD, JPY, etc.)."""
    logger.info(f"--- TOOL: get_fx_rates (currency={currency}) ---")
    params = f"?currency={currency}" if currency else ""
    result = _api_get(f"/api/fx-rates{params}")
    return json.dumps(result)


def get_customer_info(customer_id: str, tool_context: ToolContext) -> str:
    """Get customer profile information."""
    logger.info(f"--- TOOL: get_customer_info (customer={customer_id}) ---")
    result = _api_get(f"/api/customers/{customer_id}")
    return json.dumps(result)


def get_products(tool_context: ToolContext, category: str = "") -> str:
    """Get available banking products. Optionally filter by category (Bank Accounts, Merchant Services, Business Loans, Business Cards, International Payments)."""
    logger.info(f"--- TOOL: get_products (category={category}) ---")
    params = f"?category={category}" if category else ""
    result = _api_get(f"/api/products{params}")
    return json.dumps(result)
