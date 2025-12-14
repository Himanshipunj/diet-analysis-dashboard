import json
import pandas as pd
import os
from azure.storage.blob import BlobServiceClient
from io import StringIO

CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
CONTAINER_NAME = "diet-data"

def main(req):
    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container = blob_service.get_container_client(CONTAINER_NAME)

    # Loads CLEANED cached data
    blob = container.get_blob_client("Cleaned_Diets.csv")
    data = blob.download_blob().readall()
    df = pd.read_csv(StringIO(data.decode("utf-8")))

    # Query params
    diet = req.params.get("diet")
    keyword = req.params.get("q")
    page = int(req.params.get("page", 1))
    page_size = 10

    if diet:
        df = df[df["Diet_type"] == diet]

    if keyword:
        df = df[df["Recipe_name"].str.contains(keyword, case=False, na=False)]

    total = len(df)
    start = (page - 1) * page_size
    end = start + page_size

    results = df.iloc[start:end].to_dict(orient="records")

    return {
        "status": 200,
        "headers": {"Content-Type": "application/json"},
        "body": json.dumps({
            "total": total,
            "page": page,
            "pageSize": page_size,
            "data": results
        })
    }
