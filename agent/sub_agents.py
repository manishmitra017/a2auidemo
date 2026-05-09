"""
8 specialized sub-agents, each responsible for one banking domain.
All data comes exclusively from the mock server via tools.py.
"""

from google.adk.agents.llm_agent import LlmAgent
from google.adk.models.google_llm import Gemini

from tools import (
    get_accounts,
    get_transactions,
    get_spending_analytics,
    get_loans,
    get_cards,
    get_merchant_services,
    get_international_payments,
    get_fx_rates,
    get_customer_info,
    get_products,
)

GEMINI_MODEL = "gemini-2.5-flash"


def create_sub_agents() -> list[LlmAgent]:
    """Creates a fresh set of 8 sub-agents. Call this for each runner to avoid shared parent conflicts."""

    def _model():
        return Gemini(model=GEMINI_MODEL)

    return [
        # 1. Bank Accounts Agent
        LlmAgent(
            model=_model(),
            name="account_agent",
            description="Handles bank account queries: balances, account details, account types (Business Transaction Account, Business Online Saver, Savings & Term Deposits).",
            instruction=(
                "You are the Account Agent. You help customers view their bank accounts "
                "and balances. Always use customer_id 'C001'. "
                "Call get_accounts to retrieve account data. "
                "You can filter by account_type if the user asks about a specific type."
            ),
            tools=[get_accounts, get_customer_info],
        ),

        # 2. Transaction Agent
        LlmAgent(
            model=_model(),
            name="transaction_agent",
            description="Handles transaction history queries: recent transactions, filtering by account or category.",
            instruction=(
                "You are the Transaction Agent. You help customers view their transaction history. "
                "Always use customer_id 'C001'. "
                "Call get_transactions to retrieve transactions. "
                "You can filter by account_id or category. Default count is 10."
            ),
            tools=[get_transactions],
        ),

        # 3. Spending Analytics Agent
        LlmAgent(
            model=_model(),
            name="analytics_agent",
            description="Handles spending analysis: category breakdown, top merchants, month-over-month trends, where the customer spends the most.",
            instruction=(
                "You are the Spending Analytics Agent. You help customers understand their spending patterns. "
                "Always use customer_id 'C001'. "
                "Call get_spending_analytics for category breakdown, top merchants, and trends."
            ),
            tools=[get_spending_analytics],
        ),

        # 4. Business Loans & Finance Agent
        LlmAgent(
            model=_model(),
            name="loans_agent",
            description="Handles business loans and finance: BetterBusiness Loan, Car & Equipment Finance, Business Overdraft.",
            instruction=(
                "You are the Loans & Finance Agent. You help customers view their business loans, "
                "equipment finance, and overdraft facilities. "
                "Always use customer_id 'C001'. "
                "Call get_loans to retrieve loan information."
            ),
            tools=[get_loans],
        ),

        # 5. Business Cards Agent
        LlmAgent(
            model=_model(),
            name="cards_agent",
            description="Handles business card queries: Low Rate Credit Card, Business Awards Credit Card, Business Visa Debit Card.",
            instruction=(
                "You are the Cards Agent. You help customers view their business credit cards "
                "and debit cards. Always use customer_id 'C001'. "
                "Call get_cards to retrieve card information."
            ),
            tools=[get_cards],
        ),

        # 6. Merchant Services & Business Payments Agent
        LlmAgent(
            model=_model(),
            name="merchant_agent",
            description="Handles merchant services: EFTPOS terminals, Take payments online, Merchant support hub, monthly merchant summary.",
            instruction=(
                "You are the Merchant Services Agent. You help customers manage their merchant services "
                "including EFTPOS terminals, online payment gateway, and monthly merchant summaries. "
                "Always use customer_id 'C001'. "
                "Call get_merchant_services for merchant info."
            ),
            tools=[get_merchant_services],
        ),

        # 7. International Business Payments Agent
        LlmAgent(
            model=_model(),
            name="international_agent",
            description="Handles international payments: International Money Transfers, Foreign Currency Account, CommBiz international payments, FX rates.",
            instruction=(
                "You are the International Payments Agent. You help customers with international "
                "money transfers and foreign exchange rates. "
                "Always use customer_id 'C001'. "
                "Call get_international_payments for transfer history. "
                "Call get_fx_rates for current exchange rates."
            ),
            tools=[get_international_payments, get_fx_rates],
        ),

        # 8. Products & Industry Agent
        LlmAgent(
            model=_model(),
            name="products_agent",
            description="Handles product catalog: available banking products across Bank Accounts, Merchant Services, Business Loans, Business Cards, International Payments, and industry-specific solutions (Agribusiness, Health, Brighter Perspectives).",
            instruction=(
                "You are the Products Agent. You help customers discover available banking products "
                "across all categories: Bank Accounts, Merchant Services, Business Loans, "
                "Business Cards, International Payments, and industry-specific solutions. "
                "Call get_products to retrieve the product catalog. "
                "You can filter by category if the user asks about a specific area."
            ),
            tools=[get_products],
        ),
    ]
