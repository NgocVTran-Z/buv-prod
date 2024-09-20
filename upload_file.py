import streamlit as st
from azure.storage.blob import BlobServiceClient

from azure.storage.blob import BlobServiceClient
import pandas as pd
from io import BytesIO
from urllib.parse import quote

import os
from dotenv import load_dotenv, find_dotenv
load_dotenv(find_dotenv("./application/.env"))

# setup connect with Blob storage
CONNECTION_STRING = os.getenv("BLOB_CONN_STRING")
CONTAINER_NAME = os.getenv("BLOB_CONTAINER")


def upload_to_blob_storage(file_name, uploaded_file):
    # read file content
    file_contents = uploaded_file.read()

    # create BlobClient
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)
    blob_client = blob_service_client.get_blob_client(container=CONTAINER_NAME,
                                                      blob=file_name)

    container_client = blob_service_client.get_container_client(container=CONTAINER_NAME)
    blob_list = container_client.list_blobs()
    # delete all files in container before upload new file
    for blob in blob_list:
        container_client.delete_blob(blob.name)

    # Upload file on Azure Blob Storage
    blob_client.upload_blob(file_contents, overwrite=True)
    # time.sleep(10)  # wait 60s - cheating
    st.sidebar.success(f"File '{file_name}' uploaded successfully to container!")

    # delete all files in container before upload new file
    for blob in blob_list:
        print(blob.name)


    # return


def processing_uploaded_file(blob_name):
    # Create a BlobServiceClient object
    blob_service_client = BlobServiceClient.from_connection_string(CONNECTION_STRING)

    # Get a container client
    container_client = blob_service_client.get_container_client(CONTAINER_NAME)

    # Download the blob (Excel file) as a stream
    blob_client = container_client.get_blob_client(blob_name)
    blob_data = blob_client.download_blob()

    # convert to .csv
    sheet_name = "Cau Giay"
    # Load the Excel file into a pandas DataFrame
    excel_data = pd.read_excel(BytesIO(blob_data.readall()),
                               sheet_name=sheet_name,
                               engine='openpyxl')

    print(excel_data)

    # update data row in postgresql


    return





