conda install python=3.10

conda create -n env1 python=3.11

conda activate env1

export AZURE_SEARCH_ENDPOINT=""

export AZURE_SEARCH_KEY=""

export AZURE_OPENAI_ENDPOINT=""

export AZURE_OPENAI_API_KEY=""

export AZURE_COSMOSDB_ENDPOINT=""

export AZURE_COSMOSDB_KEY=""

export AZURE_SPEECH_ENDPOINT=""

export AZURE_SPEECH_KEY=""

export AZURE_STORAGE_ACCOUNT_NAME=""

cd infra

az deployment group create --resource-group rg-gpt-call-center --template-file main.bicep --parameters @main.parameters.json

cd ..

cd scripts

pip install -r ./requirements.txt

python call_center.py

cd ..

cd flaskapp

flask run