import logging
import uuid
from pathlib import Path

CLIENT_ID_FILE = Path(__file__).resolve().parents[1] / "client_id.txt"


def get_client_identifier(client_id_file: Path = CLIENT_ID_FILE) -> uuid.UUID:
    "Generate CLIENT_ID for a new client if it does not exist in client_id_file"

    def write_uuid_to_file(client_id_file: Path, client_id: uuid.UUID) -> None:
        with open(client_id_file, "w") as file:
            file.write(str(client_id))
            logging.info("Generate CLIENT_ID and added it %s", client_id_file)

    client_id_file.touch(exist_ok=True)
    client_id = uuid.uuid4()
    # File is empty
    if not (content := client_id_file.read_text()):
        write_uuid_to_file(client_id_file, client_id)
        return client_id
    try:
        return uuid.UUID(content)
    except ValueError:
        # File content is not in valid uuid format
        write_uuid_to_file(client_id_file, client_id)
        return client_id
