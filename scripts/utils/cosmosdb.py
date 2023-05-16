from azure.cosmos import CosmosClient, PartitionKey
import os
import json

def insert_item_in_container(cosmosdb_endpoint: str, cosmosdb_key: str, database_name: str,
                         container_name: str, json_document: json) -> str:

    # Initialize the Cosmos DB client
    client = CosmosClient(url = cosmosdb_endpoint, credential=cosmosdb_key)

    # Get a reference to the container where you want to write data
    database = client.get_database_client(database_name)
    container = database.get_container_client(container_name)

    # Insert the data into the container
    try:
        return container.create_item(body=json_document)["id"]
    except ValueError:
        raise Exception(f"Unable to create the item")
