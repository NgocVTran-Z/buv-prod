from datetime import datetime, timedelta
from azure.storage.blob import BlobServiceClient, generate_account_sas, BlobSasPermissions
import pandas as pd
from io import BytesIO, StringIO
import os
from dotenv import load_dotenv
load_dotenv("../application/.env")

# Replace with your connection string, container name, and blob (file) name
CONNECTION_STRING = os.getenv("BLOB_CONN_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER")


def get_the_latest_sheet(prefix_filename: str = "Bus_schedules_for_Chatbot"):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    # Get a client to interact with the container
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # List blobs in the container
    blobs_list = container_client.list_blobs()

    # Find the blob that contains "Bus_schedules_for_Chatbot" in its filename
    for blob in blobs_list:
        if prefix_filename in blob.name and blob.name.endswith(".xlsx"):
            bus_schedule_blob_name = blob.name
            break

    # Get a client to interact with the specific blob
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=bus_schedule_blob_name)

    # Download the blob as a string
    blob_data = blob_client.download_blob().read()

    # Read the Excel file into a pandas ExcelFile object
    excel_file = pd.ExcelFile(BytesIO(blob_data))
    
    latest_sheet = excel_file.sheet_names[-1]
    
    df = pd.read_excel(bus_schedule_blob_name, sheet_name=latest_sheet)
    
    return df, latest_sheet


def get_the_starting_time(filename: str = "StartingTime.csv"):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    # Get a client to interact with the container
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)
    
    # Get a client to interact with the specific blob
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME, blob=filename)
    
    # Download the blob as a string
    blob_data = blob_client.download_blob().read()
    
    # Convert blob_data to string
    blob_data_str = blob_data.decode('utf-8')
    
    # Read CSV data with pandas
    df = pd.read_csv(StringIO(blob_data_str))
    
    return df
    
