import logging

from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.server.tasks import TaskUpdater
from a2a.types import (
    DataPart,
    Part,
    Task,
    TaskState,
    TextPart,
    UnsupportedOperationError,
)
from a2a.utils import (
    new_agent_parts_message,
    new_agent_text_message,
    new_task,
)
from a2a.utils.errors import ServerError
from a2ui.a2a.extension import try_activate_a2ui_extension
from agent import BankAgent

logger = logging.getLogger(__name__)


class BankAgentExecutor(AgentExecutor):

    def __init__(self, agent: BankAgent):
        self._agent = agent

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        query = ""
        ui_event_part = None
        action = None

        active_ui_version = try_activate_a2ui_extension(
            context, self._agent.agent_card
        )

        if active_ui_version:
            logger.info("A2UI extension active — using UI agent.")
        else:
            logger.info("A2UI extension not active — using text agent.")

        use_streaming = True
        if context.message and context.message.parts:
            for part in context.message.parts:
                if isinstance(part.root, DataPart):
                    if "useStreaming" in part.root.data:
                        use_streaming = part.root.data["useStreaming"]

                    if (
                        part.root.data.get("version") == "v0.9"
                        and "action" in part.root.data
                    ):
                        ui_event_part = part.root.data["action"]
                    elif "userAction" in part.root.data:
                        ui_event_part = part.root.data["userAction"]

        if ui_event_part:
            logger.info(f"Received UI event: {ui_event_part}")
            action = ui_event_part.get("name")
            ctx = ui_event_part.get("context", {})

            if action == "view_transactions":
                account_id = ctx.get("accountId", "")
                account_name = ctx.get("accountName", "")
                query = f"Show me recent transactions for account {account_name} ({account_id})"

            elif action == "initiate_transfer":
                account_id = ctx.get("accountId", "")
                account_name = ctx.get("accountName", "")
                balance = ctx.get("balance", "")
                query = (
                    f"USER_WANTS_TO_TRANSFER from account: {account_name} "
                    f"(ID: {account_id}, Balance: {balance})"
                )

            elif action == "submit_transfer":
                from_account = ctx.get("fromAccount", "")
                to_account = ctx.get("toAccount", "")
                amount = ctx.get("amount", "")
                note = ctx.get("note", "")
                query = (
                    f"User submitted a transfer of ${amount} from {from_account} "
                    f"to {to_account}. Note: {note}"
                )

            else:
                query = f"User submitted an event: {action} with data: {ctx}"
        else:
            query = context.get_user_input()

        logger.info(f"Final query: '{query}'")

        task = context.current_task
        if not task:
            task = new_task(context.message)
            await event_queue.enqueue_event(task)
        updater = TaskUpdater(event_queue, task.id, task.context_id)

        async for item in self._agent.stream(
            query, task.context_id, active_ui_version, use_streaming=use_streaming
        ):
            is_task_complete = item["is_task_complete"]
            if not is_task_complete:
                message = None
                if "parts" in item:
                    message = new_agent_parts_message(
                        item["parts"], task.context_id, task.id
                    )
                elif "updates" in item:
                    message = new_agent_text_message(
                        item["updates"], task.context_id, task.id
                    )
                if message:
                    await updater.update_status(TaskState.working, message)
                continue

            final_state = (
                TaskState.completed
                if action == "submit_transfer"
                else TaskState.input_required
            )

            await updater.update_status(
                final_state,
                new_agent_parts_message(item["parts"], task.context_id, task.id),
                final=(final_state == TaskState.completed),
            )
            break

    async def cancel(
        self, request: RequestContext, event_queue: EventQueue
    ) -> Task | None:
        raise ServerError(error=UnsupportedOperationError())
