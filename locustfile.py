import random
import os
from locust import HttpUser, task, between
from urllib.parse import urljoin
from os import path as os_path
HF_CPU_ONLY_SERVER = "https://thesanogoeffect-grobid-papercheck.hf.space:8070"
DIGITAL_OCEAN_SERVER = "https://144.126.230.137:8070"
LOCALHOST_SERVER = "http://localhost:8070"
CALL = "/api/processFulltextDocument"
CONFIG_PATH = '/home/jakub/Projects/paper_testing/config.json'
def load_config():
    """Load configuration from the config file."""
    import json
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)
config = load_config()
if not config:
    raise ValueError("Configuration file is empty or not found.")
PARAMS  = {
                    'consolidateHeader': '0',
                    'consolidateCitations': '0',
                    'consolidateFunders': '0',
                    'includeRawCitations': 1,
                    'teiCoordinates': ",".join(config.get('coordinates', []))
                }
GROBID_SERVER_URL = urljoin(DIGITAL_OCEAN_SERVER, CALL)
print(f"Using GROBID server URL: {GROBID_SERVER_URL}")
DOCS_FOLDER = "/home/jakub/Projects/paper_testing/documents_to_test/locust"
pdf_files = [f for f in os.listdir(DOCS_FOLDER) if f.endswith('.pdf')]
if not pdf_files:
    raise ValueError(f"No PDF files found in {DOCS_FOLDER}")
print(f"Found {len(pdf_files)} PDF files to test with: {pdf_files}")


class GrobidUser(HttpUser):
    wait_time = between(10, 40)

    @task
    def process_pdf(self):
        chosen_pdf = random.choice(pdf_files)
        file_path = os_path.join(DOCS_FOLDER, chosen_pdf)
        with open(file_path, "rb") as pdf_file:
            pdf_data = pdf_file.read()
            files = {"input": (chosen_pdf, pdf_data, "application/pdf")}
        
        self.client.post(GROBID_SERVER_URL, files=files, data=PARAMS)