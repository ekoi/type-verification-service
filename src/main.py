import importlib.metadata
import logging
from io import BytesIO

import puremagic
import uvicorn
from dynaconf import Dynaconf
from fastapi import FastAPI, Request, Depends, HTTPException

__version__ = importlib.metadata.metadata("type-verification-service")["version"]

from fastapi.security import OAuth2PasswordBearer
from starlette import status


settings = Dynaconf(settings_files=["conf/settings.toml", "conf/.secrets.toml"],
                    environments=True)
logging.basicConfig(filename=settings.LOG_FILE, level=settings.LOG_LEVEL,
                    format=settings.LOG_FORMAT)

api_keys = [
    settings.DANS_TYPE_VERIFICATION_SERVICE_API_KEY
]  #

#Authorization Form: It doesn't matter what you type in the form, it won't work yet. But we'll get there.
#See: https://fastapi.tiangolo.com/tutorial/security/first-steps/
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")  # use token authentication


def api_key_auth(api_key: str = Depends(oauth2_scheme)):
    if api_key not in api_keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Forbidden"
        )


app = FastAPI(title=settings.FASTAPI_TITLE, description=settings.FASTAPI_DESCRIPTION,
              version=__version__)

app = FastAPI(title=settings.FASTAPI_TITLE, description=settings.FASTAPI_DESCRIPTION,
              version=__version__)


@app.get('/')
async def info():
    logging.info("Type verification service")
    logging.debug("info")
    return {"name": "Type verification service", "version": __version__}


@app.post('/type/{filetype}', dependencies=[Depends(api_key_auth)])
async def check_type_verification(filetype: str, request: Request):
    logging.info("Type verification service")
    logging.info("Checking MIME type format...")
    data: bytes = await request.body()
    length_of_posted_data = len(data)
    logging.info(f"File type defined by user: {filetype}")
    # TODO: problem with ms files because of the same signatures,
    #  see more details https://en.wikipedia.org/wiki/List_of_file_signatures and search on e.g. "pptx"

    for actual_file_type in puremagic.magic_string(bytearray(data)):
        logging.debug(actual_file_type)
        if actual_file_type.extension == f".{filetype}":
            return {"checked": filetype, "accepted": True, "length": length_of_posted_data}

    return {"checked": filetype, "accepted": False, "length": length_of_posted_data}


if __name__ == "__main__":
    logging.info("Start")
    uvicorn.run("src.main:app", host="0.0.0.0", port=2903, reload=False)
