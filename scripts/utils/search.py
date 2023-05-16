from azure.core.credentials import AzureKeyCredential
from azure.search.documents.indexes import SearchIndexerClient, SearchIndexClient
from azure.search.documents.indexes.models import (
    SearchIndexerDataContainer,
    SearchIndexerDataSourceConnection,
    SearchIndex,
    SearchIndexer,
    SimpleField,
    SearchFieldDataType,
    ComplexField,
    CorsOptions,
    FieldMappingFunction,
    FieldMapping,
    SearchableField
)

def create_index(service_endpoint, key, index_name):
    # create an index
    fields = [
        SimpleField(name="metadata_storage_path", type=SearchFieldDataType.String, key=True),
        ComplexField(name="content", fields=[
            SearchableField(name="source", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
            SearchableField(name="transcription_id", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
            SearchableField(name="transcription_url", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
            SearchableField(name="conversationDuration", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
            SearchableField(name="conversation", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
            SearchableField(name="phrases", type=SearchFieldDataType.String, facetable=True, filterable=True, sortable=False),
        ])
    ]
    cors_options = CorsOptions(allowed_origins=["*"], max_age_in_seconds=60)
    scoring_profiles = []
    index = SearchIndex(name=index_name
                        , fields=fields
                        , scoring_profiles=scoring_profiles
                        , cors_options=cors_options)

    client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    return client.create_index(index)    

def get_index(service_endpoint, key, index_name):        
    client = SearchIndexClient(service_endpoint, AzureKeyCredential(key))
    
    try: 
        result = client.get_index(index_name)
    except: 
        result = None
    return result    

def create_indexer(service_endpoint, key, index_name, data_source_name, indexer_name):
    # [START create_indexer]    
    source_field = "metadata_storage_path"
    target_field = "metadata_storage_path"
    function = FieldMappingFunction(name="base64Encode")
    field_mapping = FieldMapping(
        source_field_name=source_field,
        target_field_name=target_field,
        mapping_function=function
    )

    
    # create an indexer
    indexer = SearchIndexer(
        name=indexer_name,
        data_source_name=data_source_name,
        target_index_name=index_name,
        field_mappings=[field_mapping]
    )

    client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    return client.create_indexer(indexer)    

def get_indexer(service_endpoint, key, indexer_name):
    client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    try: 
        result = client.get_indexer(indexer_name)
    except: 
        result = None
    return result    

def create_data_source_connection(service_endpoint, key, data_source_name, connection_type, connection_string, container_name):
    # Create a SearchIndexerDataContainer object for the data source container.
    container = SearchIndexerDataContainer(name=container_name)
    
    # Create a SearchIndexerDataSourceConnection object for the data source connection.
    data_source_connection = SearchIndexerDataSourceConnection(
        name=data_source_name,
        type=connection_type,
        connection_string=connection_string,
        container=container
    )
    
    # Create the data source connection using the SearchIndexerClient object.
    client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))
    return client.create_data_source_connection(data_source_connection)    

def get_data_source_connection(service_endpoint, key, data_source_name):
    # Get the specified data source connection using the SearchIndexerClient object.
    client = SearchIndexerClient(service_endpoint, AzureKeyCredential(key))

    try: 
        result = client.get_data_source_connection(data_source_name)
    except: 
        result = None
    return result