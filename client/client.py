import base64

import uvicorn
from fastapi import FastAPI
from schema import Command, Message, StatusType

app = FastAPI()


@app.post("/is_up", response_model=Message)
async def is_up(command: Command) -> Message:
    # Need to check that it the identifier is not in the que
    return Message(
        identifier=command.identifier,
        status=StatusType.BEACON.value,
        result=base64.encodebytes(b"Hello"),
    )


@app.post("/", response_model=None)
async def get_beacon(msg: Message) -> None:
    print(msg)


if __name__ == "__main__":
    uvicorn.run(
        app,
        host="0.0.0.0",  # noqa: S104
        port=8080,
        # ssl_keyfile=str(Path("../keys/key.pem")),
        # ssl_certfile=Path("../keys/cert.pem"),
    )
