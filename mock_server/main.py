"""
Mock Banking API Server
Simulates downstream banking services for the A2UI Bank Assistant agent.

Domains:
  - Bank Accounts (savings, checking, term deposits)
  - Merchant Services & Business Payments
  - Business Loans & Finance
  - Business Cards (credit/debit)
  - International Business Payments
  - Spending Analytics
  - Fund Transfers
"""

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="Mock Banking API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ──────────────────────────────────────────────
# DATA
# ──────────────────────────────────────────────

CUSTOMERS = {
    "C001": {
        "customerId": "C001",
        "name": "Manish Mitra",
        "email": "manish@example.com",
        "phone": "+1-555-0101",
        "segment": "Business",
        "relationship_since": "2019-03-15",
    }
}

ACCOUNTS = {
    "ACC-1001": {
        "accountId": "ACC-1001",
        "customerId": "C001",
        "type": "Savings",
        "product": "Business Online Saver",
        "name": "Primary Savings",
        "balance": 24850.75,
        "availableBalance": 24850.75,
        "currency": "USD",
        "status": "Active",
        "interestRate": 4.5,
        "openedDate": "2019-03-15",
        "bsb": "062-000",
    },
    "ACC-1002": {
        "accountId": "ACC-1002",
        "customerId": "C001",
        "type": "Checking",
        "product": "Business Transaction Account",
        "name": "Daily Checking",
        "balance": 5230.40,
        "availableBalance": 5230.40,
        "currency": "USD",
        "status": "Active",
        "interestRate": 0.5,
        "openedDate": "2019-03-15",
        "bsb": "062-000",
    },
    "ACC-1003": {
        "accountId": "ACC-1003",
        "customerId": "C001",
        "type": "Credit Card",
        "product": "Business Awards Credit Card",
        "name": "Platinum Rewards",
        "balance": -1245.60,
        "availableBalance": 13754.40,
        "currency": "USD",
        "status": "Active",
        "creditLimit": 15000.00,
        "interestRate": 19.99,
        "openedDate": "2020-06-01",
        "cardNumber": "****-****-****-4521",
        "expiryDate": "2028-12",
    },
    "ACC-1004": {
        "accountId": "ACC-1004",
        "customerId": "C001",
        "type": "Term Deposit",
        "product": "Savings & Term Deposits",
        "name": "12-Month Term Deposit",
        "balance": 50000.00,
        "availableBalance": 0.00,
        "currency": "USD",
        "status": "Active",
        "interestRate": 5.25,
        "openedDate": "2025-11-01",
        "maturityDate": "2026-11-01",
        "termMonths": 12,
    },
    "ACC-1005": {
        "accountId": "ACC-1005",
        "customerId": "C001",
        "type": "Debit Card",
        "product": "Business Visa Debit Card",
        "name": "Business Debit",
        "balance": 5230.40,
        "availableBalance": 5230.40,
        "currency": "USD",
        "status": "Active",
        "linkedAccount": "ACC-1002",
        "cardNumber": "****-****-****-7832",
        "expiryDate": "2027-09",
    },
}

TRANSACTIONS = [
    {"id": "TXN-001", "date": "2026-05-07", "description": "Salary Deposit", "amount": 8500.00, "type": "credit", "account": "ACC-1002", "category": "Income", "merchant": "Acme Corp", "reference": "PAY-MAY-2026"},
    {"id": "TXN-002", "date": "2026-05-06", "description": "Amazon Purchase", "amount": -129.99, "type": "debit", "account": "ACC-1003", "category": "Shopping", "merchant": "Amazon.com", "reference": "AMZ-9928371"},
    {"id": "TXN-003", "date": "2026-05-05", "description": "Whole Foods Market", "amount": -87.32, "type": "debit", "account": "ACC-1002", "category": "Groceries", "merchant": "Whole Foods", "reference": "WF-20260505"},
    {"id": "TXN-004", "date": "2026-05-04", "description": "Netflix Subscription", "amount": -15.99, "type": "debit", "account": "ACC-1003", "category": "Entertainment", "merchant": "Netflix", "reference": "NFLX-MAY"},
    {"id": "TXN-005", "date": "2026-05-03", "description": "Transfer to Savings", "amount": -2000.00, "type": "debit", "account": "ACC-1002", "category": "Transfer", "merchant": "Internal", "reference": "INT-TRF-001"},
    {"id": "TXN-006", "date": "2026-05-03", "description": "Transfer from Checking", "amount": 2000.00, "type": "credit", "account": "ACC-1001", "category": "Transfer", "merchant": "Internal", "reference": "INT-TRF-001"},
    {"id": "TXN-007", "date": "2026-05-02", "description": "Uber Ride", "amount": -24.50, "type": "debit", "account": "ACC-1002", "category": "Transport", "merchant": "Uber", "reference": "UBER-20260502"},
    {"id": "TXN-008", "date": "2026-05-01", "description": "Rent Payment", "amount": -2200.00, "type": "debit", "account": "ACC-1002", "category": "Housing", "merchant": "Landlord LLC", "reference": "RENT-MAY-2026"},
    {"id": "TXN-009", "date": "2026-04-30", "description": "Interest Credit", "amount": 93.19, "type": "credit", "account": "ACC-1001", "category": "Interest", "merchant": "Bank", "reference": "INT-APR-2026"},
    {"id": "TXN-010", "date": "2026-04-29", "description": "Starbucks", "amount": -6.75, "type": "debit", "account": "ACC-1002", "category": "Food & Drink", "merchant": "Starbucks", "reference": "SBUX-20260429"},
    {"id": "TXN-011", "date": "2026-04-28", "description": "Office Supplies", "amount": -342.00, "type": "debit", "account": "ACC-1003", "category": "Business", "merchant": "Staples", "reference": "STPL-20260428"},
    {"id": "TXN-012", "date": "2026-04-27", "description": "Client Payment Received", "amount": 4500.00, "type": "credit", "account": "ACC-1002", "category": "Income", "merchant": "Beta Industries", "reference": "INV-2026-042"},
    {"id": "TXN-013", "date": "2026-04-26", "description": "EFTPOS Terminal Fee", "amount": -29.95, "type": "debit", "account": "ACC-1002", "category": "Business", "merchant": "CommBank Merchant", "reference": "EFTPOS-APR"},
    {"id": "TXN-014", "date": "2026-04-25", "description": "International Wire - GBP", "amount": -1520.00, "type": "debit", "account": "ACC-1002", "category": "International", "merchant": "FX Transfer", "reference": "FX-GBP-001"},
    {"id": "TXN-015", "date": "2026-04-24", "description": "Fuel - Shell", "amount": -65.40, "type": "debit", "account": "ACC-1005", "category": "Transport", "merchant": "Shell", "reference": "SHELL-20260424"},
]

LOANS = [
    {
        "loanId": "LN-5001",
        "customerId": "C001",
        "product": "BetterBusiness Loan",
        "type": "Business Loan",
        "originalAmount": 150000.00,
        "outstandingBalance": 98750.00,
        "interestRate": 6.49,
        "monthlyRepayment": 2850.00,
        "nextPaymentDate": "2026-06-01",
        "term": "5 years",
        "startDate": "2024-06-01",
        "endDate": "2029-06-01",
        "status": "Active",
    },
    {
        "loanId": "LN-5002",
        "customerId": "C001",
        "product": "Car & Equipment Finance",
        "type": "Equipment Loan",
        "originalAmount": 45000.00,
        "outstandingBalance": 32100.00,
        "interestRate": 7.25,
        "monthlyRepayment": 890.00,
        "nextPaymentDate": "2026-06-01",
        "term": "4 years",
        "startDate": "2025-01-15",
        "endDate": "2029-01-15",
        "status": "Active",
        "assetDescription": "2025 Toyota HiLux SR5",
    },
    {
        "loanId": "LN-5003",
        "customerId": "C001",
        "product": "Business Overdraft",
        "type": "Overdraft",
        "limit": 25000.00,
        "usedAmount": 3200.00,
        "availableAmount": 21800.00,
        "interestRate": 10.75,
        "linkedAccount": "ACC-1002",
        "status": "Active",
    },
]

MERCHANT_SERVICES = {
    "customerId": "C001",
    "merchantId": "MERCH-9001",
    "businessName": "Mitra Consulting Pty Ltd",
    "abn": "12 345 678 901",
    "terminals": [
        {
            "terminalId": "T-001",
            "type": "EFTPOS",
            "model": "Albert",
            "location": "Main Office - Front Desk",
            "status": "Active",
            "monthlyFee": 29.95,
            "lastTransaction": "2026-05-07T14:32:00Z",
        },
        {
            "terminalId": "T-002",
            "type": "Mobile",
            "model": "Smart Mini",
            "location": "Field Operations",
            "status": "Active",
            "monthlyFee": 19.95,
            "lastTransaction": "2026-05-06T10:15:00Z",
        },
    ],
    "onlinePayments": {
        "enabled": True,
        "gateway": "CommBank Gateway",
        "monthlyVolume": 12450.00,
        "monthlyTransactions": 87,
        "settlementAccount": "ACC-1002",
    },
    "monthlyMerchantSummary": {
        "totalVolume": 18920.00,
        "totalTransactions": 142,
        "averageTransactionSize": 133.24,
        "chargebackCount": 0,
    },
}

INTERNATIONAL_PAYMENTS = [
    {
        "paymentId": "INTL-001",
        "customerId": "C001",
        "type": "International Wire",
        "fromAccount": "ACC-1002",
        "toCurrency": "GBP",
        "toAmount": 1200.00,
        "fromAmount": 1520.00,
        "exchangeRate": 0.7895,
        "beneficiary": "London Office Supplies Ltd",
        "beneficiaryCountry": "United Kingdom",
        "status": "Completed",
        "date": "2026-04-25",
        "fee": 22.00,
        "reference": "FX-GBP-001",
    },
    {
        "paymentId": "INTL-002",
        "customerId": "C001",
        "type": "International Wire",
        "fromAccount": "ACC-1002",
        "toCurrency": "EUR",
        "toAmount": 3500.00,
        "fromAmount": 3850.00,
        "exchangeRate": 0.9091,
        "beneficiary": "EuroTech GmbH",
        "beneficiaryCountry": "Germany",
        "status": "Completed",
        "date": "2026-04-10",
        "fee": 22.00,
        "reference": "FX-EUR-002",
    },
]

FX_RATES = {
    "baseCurrency": "USD",
    "rates": {
        "GBP": {"buy": 0.7895, "sell": 0.7720, "mid": 0.7808},
        "EUR": {"buy": 0.9091, "sell": 0.8910, "mid": 0.9001},
        "AUD": {"buy": 1.5230, "sell": 1.4920, "mid": 1.5075},
        "JPY": {"buy": 149.50, "sell": 146.20, "mid": 147.85},
        "SGD": {"buy": 1.3250, "sell": 1.2980, "mid": 1.3115},
        "INR": {"buy": 83.50, "sell": 81.80, "mid": 82.65},
        "CAD": {"buy": 1.3650, "sell": 1.3380, "mid": 1.3515},
    },
    "lastUpdated": "2026-05-07T14:00:00Z",
}

SPENDING_ANALYTICS = {
    "customerId": "C001",
    "period": "2026-04-01 to 2026-05-07",
    "totalSpend": 6447.90,
    "totalIncome": 13093.19,
    "netCashflow": 6645.29,
    "categoryBreakdown": [
        {"category": "Housing", "amount": 2200.00, "percentage": 34.1, "transactions": 1},
        {"category": "Transfer", "amount": 2000.00, "percentage": 31.0, "transactions": 1},
        {"category": "International", "amount": 1520.00, "percentage": 23.6, "transactions": 1},
        {"category": "Business", "amount": 371.95, "percentage": 5.8, "transactions": 2},
        {"category": "Shopping", "amount": 129.99, "percentage": 2.0, "transactions": 1},
        {"category": "Groceries", "amount": 87.32, "percentage": 1.4, "transactions": 1},
        {"category": "Transport", "amount": 89.90, "percentage": 1.4, "transactions": 2},
        {"category": "Entertainment", "amount": 15.99, "percentage": 0.2, "transactions": 1},
        {"category": "Food & Drink", "amount": 6.75, "percentage": 0.1, "transactions": 1},
    ],
    "topMerchants": [
        {"merchant": "Landlord LLC", "amount": 2200.00, "count": 1},
        {"merchant": "FX Transfer", "amount": 1520.00, "count": 1},
        {"merchant": "Staples", "amount": 342.00, "count": 1},
        {"merchant": "Amazon.com", "amount": 129.99, "count": 1},
        {"merchant": "Whole Foods", "amount": 87.32, "count": 1},
    ],
    "monthOverMonth": {
        "currentMonth": 6447.90,
        "previousMonth": 5890.20,
        "changePercent": 9.5,
    },
}


# ──────────────────────────────────────────────
# ENDPOINTS: Customer
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}")
def get_customer(customer_id: str):
    customer = CUSTOMERS.get(customer_id)
    if not customer:
        return {"error": "Customer not found"}
    return customer


# ──────────────────────────────────────────────
# ENDPOINTS: Bank Accounts
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/accounts")
def get_accounts(customer_id: str, account_type: str = ""):
    accounts = [a for a in ACCOUNTS.values() if a["customerId"] == customer_id]
    if account_type:
        accounts = [a for a in accounts if a["type"].lower() == account_type.lower()]
    return {"accounts": accounts, "totalAccounts": len(accounts)}


@app.get("/api/accounts/{account_id}")
def get_account(account_id: str):
    account = ACCOUNTS.get(account_id)
    if not account:
        return {"error": "Account not found"}
    return account


@app.get("/api/accounts/{account_id}/balance")
def get_balance(account_id: str):
    account = ACCOUNTS.get(account_id)
    if not account:
        return {"error": "Account not found"}
    return {
        "accountId": account_id,
        "balance": account["balance"],
        "availableBalance": account["availableBalance"],
        "currency": account["currency"],
    }


# ──────────────────────────────────────────────
# ENDPOINTS: Transactions
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/transactions")
def get_transactions(
    customer_id: str,
    account_id: str = "",
    category: str = "",
    count: int = Query(default=10, le=50),
):
    txns = [t for t in TRANSACTIONS if ACCOUNTS.get(t["account"], {}).get("customerId") == customer_id]
    if account_id:
        txns = [t for t in txns if t["account"] == account_id]
    if category:
        txns = [t for t in txns if t["category"].lower() == category.lower()]
    return {"transactions": txns[:count], "totalCount": len(txns)}


# ──────────────────────────────────────────────
# ENDPOINTS: Spending Analytics
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/spending-analytics")
def get_spending_analytics(customer_id: str):
    if customer_id not in CUSTOMERS:
        return {"error": "Customer not found"}
    return SPENDING_ANALYTICS


# ──────────────────────────────────────────────
# ENDPOINTS: Business Loans & Finance
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/loans")
def get_loans(customer_id: str):
    customer_loans = [ln for ln in LOANS if ln["customerId"] == customer_id]
    return {"loans": customer_loans, "totalLoans": len(customer_loans)}


@app.get("/api/loans/{loan_id}")
def get_loan(loan_id: str):
    for ln in LOANS:
        if ln["loanId"] == loan_id:
            return ln
    return {"error": "Loan not found"}


# ──────────────────────────────────────────────
# ENDPOINTS: Business Cards
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/cards")
def get_cards(customer_id: str):
    cards = [
        a for a in ACCOUNTS.values()
        if a["customerId"] == customer_id and a["type"] in ("Credit Card", "Debit Card")
    ]
    return {"cards": cards, "totalCards": len(cards)}


# ──────────────────────────────────────────────
# ENDPOINTS: Merchant Services & Business Payments
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/merchant-services")
def get_merchant_services(customer_id: str):
    if customer_id not in CUSTOMERS:
        return {"error": "Customer not found"}
    return MERCHANT_SERVICES


# ──────────────────────────────────────────────
# ENDPOINTS: International Business Payments
# ──────────────────────────────────────────────

@app.get("/api/customers/{customer_id}/international-payments")
def get_international_payments(customer_id: str):
    payments = [p for p in INTERNATIONAL_PAYMENTS if p["customerId"] == customer_id]
    return {"payments": payments, "totalPayments": len(payments)}


@app.get("/api/fx-rates")
def get_fx_rates(currency: str = ""):
    if currency:
        rate = FX_RATES["rates"].get(currency.upper())
        if not rate:
            return {"error": f"Currency {currency} not found"}
        return {"baseCurrency": "USD", "currency": currency.upper(), "rate": rate}
    return FX_RATES


# ──────────────────────────────────────────────
# ENDPOINTS: Fund Transfers
# ──────────────────────────────────────────────

@app.post("/api/transfers")
def create_transfer(transfer: dict):
    from_acc = ACCOUNTS.get(transfer.get("fromAccount", ""))
    to_acc = ACCOUNTS.get(transfer.get("toAccount", ""))
    amount = transfer.get("amount", 0)

    if not from_acc:
        return {"error": "Source account not found"}
    if not to_acc:
        return {"error": "Destination account not found"}

    return {
        "transferId": "TRF-" + str(hash(str(transfer)))[-6:],
        "status": "Completed",
        "fromAccount": from_acc["accountId"],
        "fromAccountName": from_acc["name"],
        "toAccount": to_acc["accountId"],
        "toAccountName": to_acc["name"],
        "amount": amount,
        "currency": "USD",
        "timestamp": "2026-05-07T15:30:00Z",
        "reference": transfer.get("note", ""),
    }


# ──────────────────────────────────────────────
# ENDPOINTS: Products Catalog
# ──────────────────────────────────────────────

@app.get("/api/products")
def get_products(category: str = ""):
    products = {
        "Bank Accounts": [
            {"name": "Business Transaction Account", "description": "Everyday business banking with unlimited transactions", "monthlyFee": 10.00},
            {"name": "Business Online Saver", "description": "High-interest savings for business funds", "interestRate": 4.50},
            {"name": "Savings & Term Deposits", "description": "Lock in a competitive rate for a fixed term", "interestRate": 5.25},
        ],
        "Merchant Services": [
            {"name": "EFTPOS Terminals", "description": "Accept card payments in-store", "monthlyFee": 29.95},
            {"name": "Take Payments Online", "description": "Online payment gateway for e-commerce", "monthlyFee": 0.00, "transactionFee": "1.1%"},
            {"name": "Merchant Support Hub", "description": "24/7 merchant support and reporting"},
        ],
        "Business Loans & Finance": [
            {"name": "BetterBusiness Loan", "description": "Flexible business loan up to $1M", "interestRate": 6.49},
            {"name": "Car & Equipment Finance", "description": "Finance vehicles and equipment", "interestRate": 7.25},
            {"name": "Business Overdraft", "description": "Flexible credit line linked to your account", "interestRate": 10.75},
        ],
        "Business Cards": [
            {"name": "Low Rate Credit Card", "description": "Low ongoing rate for everyday purchases", "interestRate": 12.99},
            {"name": "Business Awards Credit Card", "description": "Earn points on business spending", "interestRate": 19.99, "annualFee": 150.00},
            {"name": "Business Visa Debit Card", "description": "Spend directly from your transaction account", "monthlyFee": 0.00},
        ],
        "International Payments": [
            {"name": "International Money Transfers", "description": "Send money overseas in 40+ currencies"},
            {"name": "Foreign Currency Account", "description": "Hold and manage foreign currencies"},
            {"name": "CommBiz International Payments", "description": "Bulk international payment processing"},
        ],
    }

    if category:
        for key, items in products.items():
            if category.lower() in key.lower():
                return {"category": key, "products": items}
        return {"error": f"Category '{category}' not found"}

    return {"categories": products}


# ──────────────────────────────────────────────
# Health check
# ──────────────────────────────────────────────

@app.get("/health")
def health():
    return {"status": "ok", "service": "Mock Banking API", "version": "1.0.0"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="localhost", port=8001)
