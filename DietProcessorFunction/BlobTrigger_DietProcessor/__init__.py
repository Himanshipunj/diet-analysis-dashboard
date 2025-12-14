import logging
import pandas as pd
import json
import os
from azure.storage.blob import BlobServiceClient
from io import StringIO

CONNECTION_STRING = os.getenv("AzureWebJobsStorage")
CONTAINER_NAME = "diet-data"

def main(blob: bytes):
    logging.info("All_Diets.csv updated. Running cleaning & calculations.")

    blob_service = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    container = blob_service.get_container_client(CONTAINER_NAME)

    # Reads CSV data
    df = pd.read_csv(StringIO(blob.decode("utf-8")))

    # Data Cleaning 
    df.drop_duplicates(inplace=True)
    df.fillna("Unknown", inplace=True)

    # Saves cleaned CSV
    container.upload_blob(
        name="Cleaned_Diets.csv",
        data=df.to_csv(index=False),
        overwrite=True
    )

    # Calculations
    diet_summary = df["Diet_type"].value_counts().to_dict()

    macro_averages = df[
        ["Calories", "Protein", "Carbs", "Fat"]
    ].mean().to_dict()

    container.upload_blob(
        name="diet_summary.json",
        data=json.dumps(diet_summary),
        overwrite=True
    )

    container.upload_blob(
        name="macro_averages.json",
        data=json.dumps(macro_averages),
        overwrite=True
    )

    logging.info("Cached cleaned data and results successfully.")
