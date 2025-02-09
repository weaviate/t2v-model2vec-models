import os
from typing import Optional, List
from logging import getLogger
from fastapi import FastAPI, Depends, Response, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from vectorizer import Vectorizer, VectorInput
from meta import Meta


logger = getLogger("uvicorn")

vec: Vectorizer
meta_config: Meta

get_bearer_token = HTTPBearer(auto_error=False)
allowed_tokens: List[str] = None


def get_allowed_tokens() -> List[str] | None:
    if (
        tokens := os.getenv("AUTHENTICATION_ALLOWED_TOKENS", "").strip()
    ) and tokens != "":
        return tokens.strip().split(",")


def is_authorized(auth: Optional[HTTPAuthorizationCredentials]) -> bool:
    if allowed_tokens is not None and (
        auth is None or auth.credentials not in allowed_tokens
    ):
        return False
    return True


async def lifespan(app: FastAPI):
    global vec
    global meta_config
    global allowed_tokens

    allowed_tokens = get_allowed_tokens()
    model_path = "./models"

    meta_config = Meta(model_path)
    vec = Vectorizer(model_path)

    yield


app = FastAPI(lifespan=lifespan)


@app.get("/.well-known/live", response_class=Response)
@app.get("/.well-known/ready", response_class=Response)
async def live_and_ready(response: Response):
    response.status_code = status.HTTP_204_NO_CONTENT


@app.get("/meta")
def meta(
    response: Response,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    if is_authorized(auth):
        return meta_config.get()
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}


@app.post("/vectors")
@app.post("/vectors/")
async def vectorize(
    item: VectorInput,
    response: Response,
    auth: Optional[HTTPAuthorizationCredentials] = Depends(get_bearer_token),
):
    if is_authorized(auth):
        try:
            vector = await vec.vectorize(item.text, item.config)
            return {"text": item.text, "vector": vector.tolist(), "dim": len(vector)}
        except Exception as e:
            logger.exception("Something went wrong while vectorizing data.")
            response.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
            return {"error": str(e)}
    else:
        response.status_code = status.HTTP_401_UNAUTHORIZED
        return {"error": "Unauthorized"}
