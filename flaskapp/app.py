from flask import Flask, render_template, jsonify, request
from azure.cosmos import CosmosClient, PartitionKey
from jinja2 import Environment, PackageLoader
import os
import json
import re
import openai

app = Flask(__name__,
            template_folder="./templates")

env = Environment(loader=PackageLoader(__name__, 'templates'))

def offset_to_time(offset):
    # Extract the numeric part of the offset
    seconds = float(re.search(r'(\d+(\.\d+)?)', offset).group())

    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    seconds = int(seconds % 60)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

@app.template_filter('offsetToTime')
def offset_to_time_filter(offset):
    return offset_to_time(offset)


@app.route('/get_answer', methods=['POST'])
def get_answer():
    prompt = request.form.get('prompt') 
    context = request.form.get('context')
    
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    content = "You are an enterprise Call Center chatbot whose primary goal is to help users extract insights from calls bewteen agents and customers. \n•\tProvide concise replies that are polite and professional. \n•\tAnswer questions truthfully based on provided below context. \n•\tDo not answer questions that are not related to conversations and respond with \"I can only help with any call center questions you may have.\". \n•\tIf you do not know the answer to a question, respond by saying “I do not know the answer to your question in the prodvided context”\n•\t"

    response = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages = [{"role":"system","content":content+context}
                            ,{"role":"user","content": prompt}],
                temperature=0.7,
                max_tokens=800,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
                
    answer = response.choices[0].message.content
    
    # Return a JSON response if needed
    return jsonify({'message': answer})

@app.route('/')
def index():
    # Retrieve data from your Cosmos DB container
    # Initialize the Cosmos DB client
    client = CosmosClient(url = os.environ.get("AZURE_COSMOSDB_ENDPOINT")
                        , credential = os.environ.get("AZURE_COSMOSDB_KEY"))


    # Get a reference to the container where you want to write data
    database = client.get_database_client("callCenterDB")
    postCallContainer = database.get_container_client("postCallData")
    transcriptionContainer = database.get_container_client("transcriptionData")

    postCallQuery = "SELECT * FROM c WHERE c.id = 'e9adeb6e-242b-4024-9ada-1bb7cd0c4167'"
    postCallData = postCallContainer.query_items(postCallQuery, enable_cross_partition_query=True)

    transcriptionQuery = "SELECT * FROM c WHERE c.id = 'e9adeb6e-242b-4024-9ada-1bb7cd0c4167'"
    transcriptionData = transcriptionContainer.query_items(transcriptionQuery, enable_cross_partition_query=True)

    #items = postCallData    
    #items.extend(transcriptionData)
    
    # Render a template with the data
    return render_template('app.html', postCallData=postCallData, transcriptionData=transcriptionData)

if __name__ == '__main__':
    app.run()
