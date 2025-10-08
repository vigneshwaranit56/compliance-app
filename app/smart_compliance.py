import os
import requests
import json
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
TOKEN = os.getenv("ASKBODHI_API_TOKEN")

class AskBodhiAPI:
    def __init__(self, token, container_name="askbodhi-test"):
        self.base_url = "https://askbodhi-api.sandbox.psbodhi.live/api/v2/collections/demo"
        self.headers = {
            "Authorization": f"Bearer {token}",
            "accept": "application/json"
        }
        self.container_name = container_name

    def ingest(self, pdf_path):
        url = f"{self.base_url}/ingest?database=milvus&execution_mode=sync"
        files = {
            'spacy_model': (None, 'en_core_web_sm'),
            'container_name': (None, self.container_name),
            'tokenization': (None, 'word'),
            'chunk_size': (None, '1000'),
            'temperature': (None, '0'),
            'parser_backend': (None, 'pypdf'),
            'chunk_overlap': (None, '200'),
            'max_tokens': (None, '8000'),
            'generative_model_name': (None, 'gpt-4o'),
            'file': (pdf_path, open(pdf_path, 'rb'), 'application/pdf'),
            'image_weight': (None, '0.5'),
            'chunking_strategy': (None, 'recursive'),
            'generative_model_provider': (None, 'openai'),
            'programming_language': (None, 'python'),
        }
        response = requests.post(url, headers=self.headers, files=files)
        print("Ingestion:", response.status_code)
        try:
            print(response.json())
        except Exception:
            print("Could not parse ingestion response.")
        return response

    def search(self, query):
        url = f"{self.base_url}/search?database=milvus&execution_mode=sync"
        json_payload = {
            "query": query,
            "param": {
                "size": 5,
                "output_fields": ["chunk"],
                "search_params": {
                    "target_vectors": ["chunk_vector"],
                    "similarity_range": [0, 0],
                    "reranker_config": {"reranker_type": "rrf-ranker", "ranker_value": 60}
                }
            },
            "search_type": "vector",
            "generative_model_provider": "openai",
            "generative_model_name": "gpt-4o",
            "temperature": 0,
            "max_tokens": 8000,
            "container_name": self.container_name
        }
        headers = dict(self.headers)
        headers["Content-Type"] = "application/json"
        response = requests.post(url, headers=headers, json=json_payload)
        return response


def clean_and_pretty_print_response(raw_response):
    try:
        if isinstance(raw_response, str):
            raw_response = json.loads(raw_response.replace("'", '"'))
        output_raw = raw_response.get("results", {}).get("output", "")
        output_clean = json.loads(output_raw)
        return output_clean
    except Exception as e:
        print("Error parsing response:", e)
        return None


def validate_csv(api, csv_path, output_path="compliance_validation_results.json"):
    df = pd.read_csv(csv_path)
    all_results = {}

    base_prompt = """
You are a data compliance validator.
Given a single row from a medical diagnosis CSV file, validate each column against HIPAA compliance rules.
Identify any violations related to direct or indirect identifiers and return your findings in structured JSON format.
If a row is compliant, exclude it from the output. If all rows are compliant, return an empty JSON object.

Output Format (strictly follow this structure):
{
  "1": {
    "Row #": <row_number>,
    "Rule Violated": "<short description of violation>",
    "Compliance Reference": "<specific compliance rule or section>",
    "Flagged Column": "<column_name>",
    "Recommended Action": "<action to take>",
    "Confidence Score": <confidence score>,
    "Risk Score": <risk score 0-6>
  }
}
"""

    for idx, row in df.iterrows():
        row_dict = row.to_dict()
        row_text = ", ".join([f"{k}:{v}" for k, v in row_dict.items() if pd.notna(v)])
        full_prompt = f"{base_prompt}\nNow validate the following row:\nRow #{idx+1} → {{{row_text}}}"

        print(f"\n🔍 Processing Row {idx+1}...")
        response = api.search(full_prompt)

        if response.status_code == 200:
            parsed_json = clean_and_pretty_print_response(response.json())
            all_results[f"Row_{idx+1}"] = parsed_json
        else:
            all_results[f"Row_{idx+1}"] = {"error": f"Request failed with {response.status_code}"}

    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2)

    print(f"\nAll results saved to: {output_path}")
    return all_results


def validate_file(compliance_file_path, input_file_path):
    api = AskBodhiAPI(token=TOKEN)
    api.ingest(compliance_file_path)
    results = validate_csv(api, input_file_path)
    return(json.dumps(results, indent=2))

