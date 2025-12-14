import json
import uuid
import os
from azure.cosmos import CosmosClient
from auth_utils import hash_password

client = CosmosClient(
    os.getenv("COSMOS_URI"),
    os.getenv("COSMOS_KEY")
)
container = client.get_database_client("DietDB").get_container_client("Users")

def main(req):
    body = req.get_json()

    user = {
        "id": str(uuid.uuid4()),
        "name": body["name"],
        "email": body["email"],
        "passwordHash": hash_password(body["password"]),
        "provider": "local"
    }

    container.create_item(user)

    return {
        "status": 201,
        "body": json.dumps({"message": "User registered successfully"})
    }
