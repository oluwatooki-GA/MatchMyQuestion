from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Body, Depends, FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from qdrant_client.http.exceptions import ResponseHandlingException, UnexpectedResponse
from redis import Redis, RedisError
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address
from starlette.responses import JSONResponse

from app.config.settings import settings
from app.docs.examples import search_response_examples
from app.schemas.search_schema import SearchRequest, SearchResult
from app.services.neural_search_service import NeuralSearcherService
from app.services.search_service import SearchService


def get_client_ip(request: Request) -> str:
    """Real client IP behind Render's proxy; otherwise every user shares one rate limit."""
    cf_ip = request.headers.get("cf-connecting-ip")
    if cf_ip:
        return cf_ip.strip()
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return get_remote_address(request)


limiter = Limiter(key_func=get_client_ip)


def connect_redis() -> Redis | None:
    if not (settings.REDIS_URL or settings.REDIS_HOST):
        logger.info("Redis not configured, caching disabled")
        return None
    kwargs = dict(decode_responses=True, socket_connect_timeout=2, socket_timeout=2)
    try:
        if settings.REDIS_URL:
            client = Redis.from_url(settings.REDIS_URL, **kwargs)
        else:
            client = Redis(host=settings.REDIS_HOST, port=settings.REDIS_PORT,
                           password=settings.REDIS_PASSWORD or None, **kwargs)
        client.ping()  # sync client: ping() returns a bool, it must not be awaited
    except (RedisError, OSError, ValueError) as exc:
        logger.warning(f"Redis not available, caching disabled: {exc}")
        return None
    logger.info("Connected to Redis, caching enabled")
    return client


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.neural_search_service = NeuralSearcherService(settings.QDRANT_COLLECTION_NAME)
    app.state.redis = connect_redis()
    yield
    app.state.neural_search_service.close()
    if app.state.redis:
        app.state.redis.close()


app = FastAPI(lifespan=lifespan)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

origins = [o.strip() for o in settings.CORS_ORIGIN.split(",") if o.strip()] or ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    # No cookies/auth are used; credentials + "*" is also rejected by browsers.
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"{request.method} {request.url.path} -> {response.status_code}")
    return response


def get_search_service(request: Request) -> SearchService:
    return SearchService(
        redis_client=request.app.state.redis,
        neural_search_service=request.app.state.neural_search_service,
    )


@app.exception_handler(ResponseHandlingException)
async def qdrant_connection_exception_handler(request: Request, exc: ResponseHandlingException):
    logger.error(f"Qdrant connection error: {exc}")
    return JSONResponse(status_code=status.HTTP_424_FAILED_DEPENDENCY,
                        content={"message": "Oops! couldn't connect to qdrant -Timeout"})


@app.exception_handler(UnexpectedResponse)
async def qdrant_unexpected_response_handler(request: Request, exc: UnexpectedResponse):
    logger.error(f"Qdrant returned {exc.status_code}: {exc}")
    if exc.status_code in (status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN):
        message = "Oops! couldn't connect to qdrant -Invalid Credentials"
    elif exc.status_code == status.HTTP_404_NOT_FOUND:
        message = "Oops! the questions collection was not found in qdrant"
    else:
        message = "Oops! qdrant returned an unexpected error"
    return JSONResponse(status_code=status.HTTP_424_FAILED_DEPENDENCY, content={"message": message})


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
