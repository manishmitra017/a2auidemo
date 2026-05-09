import logging
import os

import click
from a2a.server.apps import A2AStarletteApplication
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.tasks import InMemoryTaskStore
from agent import BankAgent
from agent_executor import BankAgentExecutor
from dotenv import load_dotenv
from starlette.middleware.cors import CORSMiddleware

load_dotenv(".env.local")
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@click.command()
@click.option("--host", default="localhost")
@click.option("--port", default=10002)
def main(host, port):
    if not os.getenv("GOOGLE_GENAI_USE_VERTEXAI") == "TRUE":
        if not os.getenv("GEMINI_API_KEY"):
            logger.error(
                "GEMINI_API_KEY not set. Get one from https://aistudio.google.com/apikey"
            )
            exit(1)

    base_url = f"http://{host}:{port}"
    agent = BankAgent(base_url=base_url)
    agent_executor = BankAgentExecutor(agent)

    request_handler = DefaultRequestHandler(
        agent_executor=agent_executor,
        task_store=InMemoryTaskStore(),
    )
    server = A2AStarletteApplication(
        agent_card=agent.agent_card, http_handler=request_handler
    )

    import uvicorn

    app = server.build()
    app.add_middleware(
        CORSMiddleware,
        allow_origin_regex=r"http://localhost:\d+",
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    logger.info(f"Bank Assistant agent running at {base_url}")
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    main()
