from json import dumps
import glob
import os
import time
import pandas as pd

from utils import speech, blobs, search, cosmosdb, openai_postcall


def process_files(audio_files, storage_account_name, source_container_name, target_container_name):
    """
    Process audio files in the specified directory.
    Uploads each file to Azure Blob Storage and transcribes it using Azure Speech Services.
    Saves the transcription as a JSON file in another Azure Blob Storage container.

    Args:
        audio_files (str): Path to directory containing audio files to be processed.
        storage_account_name (str): Name of Azure Blob Storage account.
        source_container_name (str): Name of Azure Blob Storage container for input files.
        target_container_name (str): Name of Azure Blob Storage container for output files.
    """
    
    # Set up reusable variables for speech-related values
    speech_endpoint = os.environ.get("AZURE_SPEECH_ENDPOINT")
    speech_subscription_key = os.environ.get("AZURE_SPEECH_KEY")
    cosmosdb_endpoint = os.environ.get("AZURE_COSMOSDB_ENDPOINT")
    cosmosdb_key = os.environ.get("AZURE_COSMOSDB_KEY")
    locale = "en-US"
    
    for audio_file_path in glob.glob(audio_files):
        print(f"Processing '{audio_file_path}'")
        
        # Upload audio file to Azure Blob Storage        
        blobs.upload_audio_file_to_container(audio_file_path = audio_file_path
                                            , storage_account_name = storage_account_name
                                            , container_name = source_container_name)

        # Get SAS URL for uploaded audio file
        input_audio_url = blobs.create_sas_token_for_audio(storage_account_name = storage_account_name
                                                            , container_name = source_container_name
                                                            , audio_file_path = audio_file_path)

        # Create transcription job using Azure Speech Services
        transcription_id = speech.create_transcription(speech_endpoint = speech_endpoint
                                                        , speech_subscription_key = speech_subscription_key
                                                        , input_audio_url = input_audio_url
                                                        , use_stereo_audio = None
                                                        , locale = locale)
        print(f"Transcription ID: {transcription_id}")

        # Wait for transcription job to complete
        speech.wait_for_transcription(transcription_id = transcription_id
                                      , speech_endpoint = speech_endpoint
                                      , speech_subscription_key = speech_subscription_key)

        # Get URLs for transcription results from Azure Speech Services
        transcription_files = speech.get_transcription_files(transcription_id = transcription_id
                                                            , speech_endpoint = speech_endpoint
                                                            , speech_subscription_key = speech_subscription_key)

        # Get URL for JSON-formatted transcription result from Azure Speech Services
        transcription_url = speech.get_transcription_url(transcription_files = transcription_files)
        
        print(f"Transcription URI: {transcription_url}")

        # Download and parse JSON-formatted transcription result from Azure Blob Storage
        transcription = speech.get_transcription(transcription_url = transcription_url)

        transcription["id"] = transcription_id

        print(cosmosdb.insert_item_in_container(cosmosdb_endpoint = cosmosdb_endpoint, cosmosdb_key = cosmosdb_key, database_name = "callCenterDB",
                         container_name = "transcriptionData", json_document = transcription))
        
        # Extract conversation items from parsed transcript 
        phrases = speech.get_transcription_phrases(transcription = transcription)
        
        conversation_items = speech.transcription_phrases_to_conversation_items(phrases)

        # Save conversation items as a JSON file in another Azure Blob Storage container
        blob_name = f"{os.path.basename(audio_file_path)}.json"
        json_data = dumps(conversation_items)

        conversation = ""

        for conversation_item in conversation_items:
            conversation += f"{conversation_item['role']}: {conversation_item['display']} \n"

        json_data_final = {
            "source": transcription["source"]
            , "transcription_id": transcription_id
            , "transcription_url": transcription_url
            , "conversationDuration": transcription["duration"]
            , "conversation": conversation
            , "phrases": json_data   
        }    

        blobs.upload_json_to_container(blob_name = blob_name
                                       , json_data = dumps(json_data_final)
                                       , storage_account_name = storage_account_name
                                       , container_name = target_container_name)
        
        postCall = {}

        postCall["id"] = transcription_id

        df = pd.read_csv('../config/postCallConfig.csv', header = 0)

        for index, row in df.iterrows():
            attribute = row['attribute']
            question = row['question']
            print(attribute)
            print(question)

            postCall[attribute] = openai_postcall.get_answer(question, conversation)
            print(postCall)
            time.sleep(60)                 

        print(cosmosdb.insert_item_in_container(cosmosdb_endpoint = cosmosdb_endpoint, cosmosdb_key = cosmosdb_key, database_name = "callCenterDB",
                         container_name = "postCallData", json_document = postCall))

if __name__ == "__main__":
    storage_account_name = os.environ.get("AZURE_STORAGE_ACCOUNT_NAME") #"saccgpt0001"
    source_container_name = "landing"
    target_container_name = "transcription"
    audio_files = "../data/*"        

    service_endpoint = os.getenv("AZURE_SEARCH_ENDPOINT")
    search_subscription_key = os.getenv("AZURE_SEARCH_KEY")
    connection_string = os.getenv("AZURE_STORAGE_CONNECTION_STRING")

    connection_type = "azureblob"
    container_name = "transcription"
    data_source_name = "transcription"
    index_name = "transcription-index"
    indexer_name = "transcription-indexer"

    print(f"Processing files...")

    # Call function to process audio files 
    process_files(audio_files = audio_files
                , storage_account_name = storage_account_name
                , source_container_name = source_container_name
                , target_container_name = target_container_name)
    
    if not search.get_data_source_connection(service_endpoint, search_subscription_key, data_source_name):
        search.create_data_source_connection(service_endpoint, search_subscription_key, data_source_name, connection_type, connection_string, container_name)

    if not search.get_index(service_endpoint, search_subscription_key, index_name):
        search.create_index(service_endpoint, search_subscription_key, index_name)

    if not search.get_indexer(service_endpoint, search_subscription_key, indexer_name):
        search.create_indexer(service_endpoint, search_subscription_key, index_name, data_source_name, indexer_name)