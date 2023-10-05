import os
import re
import time

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import FAISS
from langchain.text_splitter import MarkdownHeaderTextSplitter
import openai
from langchain.docstore.document import Document

from dotenv import load_dotenv
from prompt import GPT_PROMPT_START, GPT_PROMPT_END_METHOD, RSPEC_START_1, RSPEC_START_2, RSPEC_END

load_dotenv()

openai.api_key = os.environ['OPENAI_API_KEY']

PROJECT_PATH = os.environ['PROJECT_PATH']
POLICIES_PATH = f'{PROJECT_PATH}app/policies/admin/'
SPECS_PATH = f'{PROJECT_PATH}spec/policies/admin/'

class_name = ''
methods = {}

def get_class_name(rb):
  return re.search(r'class\s(.*)\s\<.*', rb)[1]

def get_methods(rb):
  return re.findall(r'def\s(.*\?)', rb)

for file_name in os.listdir(POLICIES_PATH):
  spec_file_name = f'{os.path.basename(file_name).split(".")[0]}_spec.rb'
  if os.path.exists(f'{SPECS_PATH}{spec_file_name}'):
    continue
  with open(f'{POLICIES_PATH}{file_name}', 'r') as source_file:
    source = source_file.read()
    class_name = get_class_name(source)
    print(class_name)
    methods = [{'name': name, 'code': ''} for name in get_methods(source)]
    for method in methods:
      print(method['name'])
      messages = [
          {'role': 'system', 'content': GPT_PROMPT_START + source},
          {'role': 'user', 'content': GPT_PROMPT_END_METHOD.format(method_name = method['name'], class_name = class_name)}
      ]
      completion = openai.ChatCompletion.create(
          model = 'gpt-4-0613',
          messages = messages,
          temperature = 0
      )
      answer = completion.choices[0].message.content.splitlines()[1: -1]
      method['code'] = '\n'.join([f'  {line}' for line in answer])
      time.sleep(5)
    body = '\n\n'.join([method['code'] for method in methods])
    result = f'{RSPEC_START_1}{class_name}{RSPEC_START_2}\n{body}\n{RSPEC_END}'
    print(result)
    with open(f'{SPECS_PATH}{spec_file_name}', 'w+') as spec_file:
      spec_file.write(result)
