import json
import os
from azure.cosmos import CosmosClient
from auth_utils import verify_password

client = CosmosClient(
    os.getenv("COSMOS_URI"),
    os.getenv("COSMOS_KEY")
)
container = client.get_database_client("DietDB").get_container_client("Users")

def main(req):
    body = req.get_json()

    email = body["email"]
    password = body["password"]

    users = list(container.query_items(
        query="SELECT * FROM c WHERE c.email=@email",
        parameters=[{"name": "@email", "value": email}],
        enable_cross_partition_query=True
    ))

    if not users:
        return {"status": 401, "body": "Invalid credentials"}

    user = users[0]

    if verify_password(password, user["passwordHash"]):
        return {
            "status": 200,
            "body": json.dumps({
                "name": user["name"],
                "email": user["email"]
            })
        }

    return {"status": 401, "body": "Invalid credentials"}
