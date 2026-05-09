import json
import logging
import os
from collections import OrderedDict
from collections.abc import AsyncIterable
from typing import Any, Optional, Dict

import jsonschema
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentSkill,
    Part,
    TextPart,
)
from google.adk.agents import run_config
from google.adk.agents.llm_agent import LlmAgent
from google.adk.artifacts import InMemoryArtifactService
from google.adk.memory.in_memory_memory_service import InMemoryMemoryService
from google.adk.models.google_llm import Gemini
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai import types
from prompt_builder import (
    get_text_prompt,
    ROLE_DESCRIPTION,
    UI_DESCRIPTION,
)
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
from a2ui.schema.constants import (
    VERSION_0_9,
    A2UI_OPEN_TAG,
    A2UI_CLOSE_TAG,
)
from a2ui.schema.manager import A2uiSchemaManager
from a2ui.parser.parser import parse_response
from a2ui.basic_catalog.provider import BasicCatalog
from a2ui.schema.common_modifiers import remove_strict_validation
from a2ui.a2a.extension import get_a2ui_agent_extension
from a2ui.a2a.parts import parse_response_to_parts, stream_response_to_parts

logger = logging.getLogger(__name__)


class BankAgent:
    SUPPORTED_CONTENT_TYPES = ["text", "text/plain"]

    def __init__(self, base_url: str):
        self.base_url = base_url
        self._agent_name = "Bank Assistant"
        self._user_id = "remote_agent"
        self._text_runner = self._build_runner(self._build_llm_agent())

        self._schema_managers: Dict[str, A2uiSchemaManager] = {}
        self._ui_runners: Dict[str, Runner] = {}
        self._parsers = OrderedDict()
        self._max_parsers = 1000

        for version in [VERSION_0_9]:
            schema_manager = self._build_schema_manager(version)
            self._schema_managers[version] = schema_manager
            agent = self._build_llm_agent(schema_manager)
            self._ui_runners[version] = self._build_runner(agent)

        self._agent_card = self._build_agent_card()

    @property
    def agent_card(self) -> AgentCard:
        return self._agent_card

    def _build_schema_manager(self, version: str) -> A2uiSchemaManager:
        return A2uiSchemaManager(
            version=version,
            catalogs=[
                BasicCatalog.get_config(
                    version=version, examples_path=f"examples/{version}"
                )
            ],
            schema_modifiers=[remove_strict_validation],
        )

    def _build_agent_card(self) -> AgentCard:
        extensions = []
        for version, sm in self._schema_managers.items():
            ext = get_a2ui_agent_extension(
                version,
                sm.accepts_inline_catalogs,
                sm.supported_catalog_ids,
            )
            extensions.append(ext)

        capabilities = AgentCapabilities(
            streaming=True,
            extensions=extensions,
        )

        skills = [
            AgentSkill(id="accounts", name="Bank Accounts", description="Business Transaction Account, Business Online Saver, Savings & Term Deposits", tags=["accounts", "balances"], examples=["Show my account balances"]),
            AgentSkill(id="transactions", name="Transactions", description="View transaction history, filter by account or category", tags=["transactions"], examples=["Show my recent transactions"]),
            AgentSkill(id="analytics", name="Spending Analytics", description="Spending breakdown, top merchants, trends", tags=["spending", "analytics"], examples=["Where do I spend the most?"]),
            AgentSkill(id="loans", name="Business Loans & Finance", description="BetterBusiness Loan, Car & Equipment Finance, Business Overdraft", tags=["loans", "finance"], examples=["Show my business loans"]),
            AgentSkill(id="cards", name="Business Cards", description="Low Rate Credit Card, Business Awards Credit Card, Business Visa Debit Card", tags=["cards", "credit"], examples=["Show my business cards"]),
            AgentSkill(id="merchant", name="Merchant Services & Business Payments", description="EFTPOS terminals, online payments, merchant summary", tags=["merchant", "eftpos"], examples=["Show my merchant services"]),
            AgentSkill(id="international", name="International Business Payments", description="International Money Transfers, Foreign Currency Account, FX rates", tags=["international", "fx"], examples=["Show FX rates"]),
            AgentSkill(id="products", name="Product Catalog", description="Browse all available banking products", tags=["products"], examples=["What products do you offer?"]),
        ]

        return AgentCard(
            name="Bank Assistant",
            description="A multi-agent business banking assistant with 8 specialized agents.",
            url=self.base_url,
            version="1.0.0",
            default_input_modes=self.SUPPORTED_CONTENT_TYPES,
            default_output_modes=self.SUPPORTED_CONTENT_TYPES,
            capabilities=capabilities,
            skills=skills,
        )

    def _build_runner(self, agent: LlmAgent) -> Runner:
        return Runner(
            app_name=self._agent_name,
            agent=agent,
            artifact_service=InMemoryArtifactService(),
            session_service=InMemorySessionService(),
            memory_service=InMemoryMemoryService(),
        )

    def _build_llm_agent(
        self, schema_manager: Optional[A2uiSchemaManager] = None
    ) -> LlmAgent:
        GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

        instruction = (
            schema_manager.generate_system_prompt(
                role_description=ROLE_DESCRIPTION,
                ui_description=UI_DESCRIPTION,
                include_schema=True,
                include_examples=True,
                validate_examples=True,
            )
            if schema_manager
            else get_text_prompt()
        )

        return LlmAgent(
            model=Gemini(model=GEMINI_MODEL),
            name="bank_orchestrator",
            description="Orchestrator that routes to 8 domain agents via their tools.",
            instruction=instruction,
            tools=[
                get_accounts,       # -> Account Agent
                get_transactions,   # -> Transaction Agent
                get_spending_analytics,  # -> Analytics Agent
                get_loans,          # -> Loans Agent
                get_cards,          # -> Cards Agent
                get_merchant_services,   # -> Merchant Agent
                get_international_payments,  # -> International Agent
                get_fx_rates,       # -> International Agent
                get_customer_info,  # -> Account Agent
                get_products,       # -> Products Agent
            ],
        )

    async def stream(
        self,
        query,
        session_id,
        ui_version: Optional[str] = None,
        use_streaming: bool = True,
    ) -> AsyncIterable[dict[str, Any]]:
        session_state = {"base_url": self.base_url, "expression": "{expression}"}

        if ui_version:
            runner = self._ui_runners[ui_version]
            schema_manager = self._schema_managers[ui_version]
            selected_catalog = (
                schema_manager.get_selected_catalog() if schema_manager else None
            )
        else:
            runner = self._text_runner
            schema_manager = None
            selected_catalog = None

        session = await runner.session_service.get_session(
            app_name=self._agent_name,
            user_id=self._user_id,
            session_id=session_id,
        )
        if session is None:
            session = await runner.session_service.create_session(
                app_name=self._agent_name,
                user_id=self._user_id,
                state=session_state,
                session_id=session_id,
            )

        if ui_version and (not selected_catalog or not selected_catalog.catalog_schema):
            logger.error("A2UI schema not loaded.")
            yield {
                "is_task_complete": True,
                "parts": [
                    Part(
                        root=TextPart(
                            text="Internal configuration error with UI components."
                        )
                    )
                ],
            }
            return

        max_retries = 1
        attempt = 0
        current_query_text = query

        while attempt <= max_retries:
            attempt += 1
            logger.info(f"Attempt {attempt}/{max_retries + 1} for session {session_id}")

            current_message = types.Content(
                role="user", parts=[types.Part.from_text(text=current_query_text)]
            )

            full_content_list = []
            parts_streamed = False

            async def token_stream():
                async for event in runner.run_async(
                    user_id=self._user_id,
                    session_id=session.id,
                    run_config=run_config.RunConfig(
                        streaming_mode=(
                            run_config.StreamingMode.SSE
                            if use_streaming
                            else run_config.StreamingMode.NONE
                        )
                    ),
                    new_message=current_message,
                ):
                    if event.content and event.content.parts:
                        for p in event.content.parts:
                            if p.text:
                                full_content_list.append(p.text)
                                yield p.text

            if selected_catalog and use_streaming:
                from a2ui.parser.streaming import A2uiStreamParser

                if session_id in self._parsers:
                    self._parsers.move_to_end(session_id)
                else:
                    self._parsers[session_id] = A2uiStreamParser(
                        catalog=selected_catalog
                    )
                    if len(self._parsers) > self._max_parsers:
                        self._parsers.popitem(last=False)

                async for part in stream_response_to_parts(
                    self._parsers[session_id],
                    token_stream(),
                ):
                    parts_streamed = True
                    yield {
                        "is_task_complete": False,
                        "parts": [part],
                    }
            else:
                async for token in token_stream():
                    if not selected_catalog:
                        yield {
                            "is_task_complete": False,
                            "updates": token,
                        }

            final_response_content = "".join(full_content_list)
            is_valid = False
            error_message = ""

            if ui_version:
                try:
                    response_parts = parse_response(final_response_content)
                    for part in response_parts:
                        if not part.a2ui_json:
                            continue
                        selected_catalog.validator.validate(part.a2ui_json)
                        is_valid = True
                except (
                    ValueError,
                    json.JSONDecodeError,
                    jsonschema.exceptions.ValidationError,
                ) as e:
                    logger.warning(f"A2UI validation failed: {e} (Attempt {attempt})")
                    error_message = f"Validation failed: {e}."
            else:
                is_valid = True

            if is_valid:
                final_parts = parse_response_to_parts(
                    final_response_content, fallback_text="OK."
                )
                yield {
                    "is_task_complete": True,
                    "parts": [] if (use_streaming and parts_streamed) else final_parts,
                }
                return

            if attempt <= max_retries:
                current_query_text = (
                    f"Your previous response was invalid. {error_message} You MUST generate a"
                    " valid response that strictly follows the A2UI JSON SCHEMA. The response"
                    " MUST be a JSON list of A2UI messages. Ensure each JSON part is wrapped in"
                    f" '{A2UI_OPEN_TAG}' and '{A2UI_CLOSE_TAG}' tags. Please retry the"
                    f" original request: '{query}'"
                )

        yield {
            "is_task_complete": True,
            "parts": [
                Part(
                    root=TextPart(
                        text="Having trouble generating the interface. Please try again."
                    )
                )
            ],
        }
