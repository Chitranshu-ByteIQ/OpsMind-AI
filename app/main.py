import logging
from typing import Any

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config import settings
from app.graph.workflow import workflow
from app.schemas.api import ChatRequest, ChatResponse, ErrorResponse, HealthResponse
from app.routes.dashboard import router as dashboard_router
from app.routes.tools import router as tools_router


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


app = FastAPI(
    title="OpsMind AI API",
    description="Backend API for the OpsMind multi-agent workflow.",
    version="1.0.0",
)


# Allow Streamlit/frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=[origin.strip() for origin in settings.cors_origins.split(",")],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
app.include_router(tools_router)
app.include_router(dashboard_router)


@app.exception_handler(Exception)
async def application_exception_handler(
    request: Request,
    exc: Exception,
) -> JSONResponse:
    logger.exception("Unhandled request failure: %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            message="The request could not be completed.",
            error="An internal workflow error occurred.",
        ).model_dump(),
    )


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {
        "application": "OpsMind AI API",
        "status": "running",
        "version": app.version,
        "docs": "/docs",
    }


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health() -> HealthResponse:
    return HealthResponse(status="healthy", environment=settings.environment)


@app.post(
    "/chat",
    response_model=ChatResponse,
    responses={502: {"model": ErrorResponse}},
    tags=["workflow"],
)
def chat(request: ChatRequest) -> ChatResponse:
    logger.info("Request received: /chat")
    logger.info("Workflow started")

    try:
        result: dict[str, Any] = workflow.invoke(
            {"user_request": request.message}
        )
        agent = result.get("agent") or result.get("next_agent")
        logger.info("Workflow completed; agent=%s", agent)
        return ChatResponse(
            success=True,
            message=result.get("final_response", "Workflow completed."),
            agent=agent,
            data={
                "plan": result.get("plan", []),
                "agent_results": result.get("agent_results", {}),
            },
        )
    except Exception:
        logger.exception("Workflow failed")
        return JSONResponse(
            status_code=status.HTTP_502_BAD_GATEWAY,
            content=ErrorResponse(
                message="The workflow could not complete this request.",
                error="A configured service or workflow step failed.",
            ).model_dump(),
        )

