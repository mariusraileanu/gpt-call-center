import re
from typing import Any, Dict, List

import os
import openai

def get_answer(query, context):
    openai.api_type = "azure"
    openai.api_base = os.environ.get("AZURE_OPENAI_ENDPOINT")
    openai.api_version = "2023-03-15-preview"
    openai.api_key = os.environ.get("AZURE_OPENAI_API_KEY")

    content = "You are an enterprise Call Center chatbot whose primary goal is to help users extract insights from calls bewteen agents and customers. \n•\tProvide concise replies that are polite and professional. \n•\tAnswer questions truthfully based on provided below context. \n•\tDo not answer questions that are not related to conversations and respond with \"I can only help with any call center questions you may have.\". \n•\tIf you do not know the answer to a question, respond by saying “I do not know the answer to your question in the prodvided context”\n•\t"

    response = openai.ChatCompletion.create(
                engine="gpt-4-32k",
                messages = [{"role":"system","content":content+context}
                            ,{"role":"user","content": query}],
                temperature=0.3,
                max_tokens=4000,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None)
                
    return response.choices[0].message.content