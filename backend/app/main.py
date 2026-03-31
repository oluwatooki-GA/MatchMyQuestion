from typing import Annotated
from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, status, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from app.schemas.search_schema import SearchRequest, SearchResult
from app.services.neural_search_service import NeuralSearcherService
from app.config.settings import settings
from app.services.search_service import SearchService
from app.docs.examples import search_response_examples
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from redis import Redis
from loguru import logger
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.neural_search_service = NeuralSearcherService(settings.QDRANT_COLLECTION_NAME)
    app.state.redis = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT, decode_responses=True)
    yield
    app.state.neural_search_service.close()
    app.state.redis.close()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = settings.CORS_ORIGIN.strip().split(",") if settings.CORS_ORIGIN else ["*"]
origins = [origin for origin in origins if origin]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Request: {request.url}")
    logger.info(f"Request client: {request.client}")
    response = await call_next(request)
    return response


def get_search_service() -> SearchService:
    return SearchService(
        redis_client=app.state.redis,
        neural_search_service=app.state.neural_search_service,
    )


@app.exception_handler(ResponseHandlingException)
async def qdrant_connection_exception_handler(request: Request, exc: ResponseHandlingException):
    return JSONResponse(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                        content={"message": f"Oops! couldn't connect to qdrant -Timeout"}, )


@app.exception_handler(UnexpectedResponse)
async def qdrant_login_exception_handler(request: Request, exc: UnexpectedResponse):
    if exc.status_code == status.HTTP_403_FORBIDDEN:
        return JSONResponse(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                            content={"message": f"Oops! couldn't connect to qdrant -Invalid Credentials"}, )


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post(
    "/api/v1/search",
    response_model=SearchResult,
    status_code=status.HTTP_200_OK,
    summary='Search for questions',
    description="Search results based on the input criteria.",
    responses=search_response_examples
)
@limiter.limit("20/minute;5/second")
def search(
    request: Request,
    search_service: Annotated[SearchService, Depends(get_search_service)],
    search_request: Annotated[SearchRequest, Body()]
):
    return search_service.search(search_request)
