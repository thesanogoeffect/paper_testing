import os
import time
import requests
import glob
import json

# --- Configuration ---
PDF_SOURCE_DIR = '/home/jakub/Projects/paper_testing/documents_to_test/psych_science_pdf_oa'
OUTPUT_DIR = '/home/jakub/Projects/paper_testing/output'
CONFIG_PATH = '/home/jakub/Projects/paper_testing/config.json'
MAX_RETRIES = 3
TIMEOUT_SECONDS = 300  # 5 minutes
NTFY_URL = 'http://unraid:8021/papercheck'
CORRIGENDUM_PAPERS_START_DICT = { # maps for which papers we have to specify start=X
    "0956797617710785.pdf": 6,
    "0956797618795679.pdf": 2,
    "0956797618815482.pdf": 2,
    "0956797619830329.pdf": 2,
    "0956797620959594.pdf": 4,
    #"09567976231217508.pdf": 2, # these are just corrigendum papers, which is probably ok
    #"09567976221139496.pdf": 2,
}

# --- Helper Functions ---

def get_config():
    """Loads the configuration from config.json."""
    with open(CONFIG_PATH, 'r') as f:
        return json.load(f)

def send_ntfy_notification(message, title, priority='default'):
    """Sends a notification to the ntfy server."""
    try:
        requests.post(
            NTFY_URL,
            data=message.encode('utf-8'),
            headers={
                'Title': title,
                'Priority': priority,
                'Tags': 'robot'
            }
        )
    except requests.exceptions.RequestException as e:
        print(f"Failed to send ntfy notification: {e}")

def get_pdf_files():
    """Get a list of all PDF files in the source directory."""
    return glob.glob(os.path.join(PDF_SOURCE_DIR, '*.pdf'))

def get_processed_files():
    """Get a list of already processed XML files."""
    return glob.glob(os.path.join(OUTPUT_DIR, '*.grobid.tei.xml'))

def get_unprocessed_pdfs(all_pdfs, processed_xmls):
    """Filter out PDFs that have already been processed."""
    processed_basenames = {os.path.basename(xml).replace('.grobid.tei.xml', '') for xml in processed_xmls}
    unprocessed = [pdf for pdf in all_pdfs if os.path.basename(pdf).replace('.pdf', '') not in processed_basenames]
    return unprocessed

def process_pdf(pdf_path, config, pdf_num, total_pdfs):
    """Processes a single PDF using the GROBID API."""
    pdf_name = os.path.basename(pdf_path)
    output_filename = os.path.basename(pdf_path).replace('.pdf', '.grobid.tei.xml')
    output_path = os.path.join(OUTPUT_DIR, output_filename)
    
    send_ntfy_notification(
        f"Processing PDF {pdf_num}/{total_pdfs}: {pdf_name}",
        "GROBID PDF Start"
    )

    for attempt in range(MAX_RETRIES):
        try:
            with open(pdf_path, 'rb') as f:
                files = {'input': f}
                
                params = {
                    'consolidateHeader': '1',
                    'consolidateCitations': '1',
                    'consolidateFunders': '1',
                    'includeRawCitations': 1,
                    'teiCoordinates': ",".join(config.get('coordinates', []))
                }

                if pdf_name in CORRIGENDUM_PAPERS_START_DICT:
                    params['start'] = CORRIGENDUM_PAPERS_START_DICT[pdf_name]

                response = requests.post(
                    f"{config['grobid_server']}/api/processFulltextDocument",
                    files=files,
                    data=params,
                    timeout=TIMEOUT_SECONDS
                )
                response.raise_for_status()

                with open(output_path, 'w', encoding='utf-8') as out_f:
                    out_f.write(response.text)

                send_ntfy_notification(
                    f"Successfully processed {pdf_name} ({pdf_num}/{total_pdfs}).",
                    "GROBID PDF Success",
                    'high'
                )
                print(f"Successfully processed {pdf_name} to {output_path}")
                return True

        except requests.exceptions.Timeout:
            message = f"Timeout processing {pdf_name} on attempt {attempt + 1}/{MAX_RETRIES}."
            print(message)
            send_ntfy_notification(message, "GROBID PDF Timeout", 'urgent')
            time.sleep(10)

        except requests.exceptions.RequestException as e:
            message = f"Error processing {pdf_name} on attempt {attempt + 1}/{MAX_RETRIES}.\nError: {e}"
            print(message)
            send_ntfy_notification(message, "GROBID PDF Error", 'urgent')
            time.sleep(10)

    final_error_message = f"Failed to process {pdf_name} after {MAX_RETRIES} attempts."
    print(final_error_message)
    send_ntfy_notification(final_error_message, "GROBID PDF Failed", 'urgent')
    return False


# --- Main Execution ---

def main():
    """Main function to run the PDF processing script."""
    send_ntfy_notification("Starting robust PDF processing script.", "Script Started")
    
    config = get_config()
    all_pdfs = get_pdf_files()
    processed_xmls = get_processed_files()
    unprocessed_pdfs = get_unprocessed_pdfs(all_pdfs, processed_xmls)

    if not unprocessed_pdfs:
        message = "All PDFs have already been processed."
        print(message)
        send_ntfy_notification(message, "Script Finished")
        return

    message = f"Found {len(unprocessed_pdfs)} PDFs to process out of {len(all_pdfs)} total."
    print(message)
    send_ntfy_notification(message, "Processing Status")

    total_pdfs = len(unprocessed_pdfs)
    for i, pdf_path in enumerate(unprocessed_pdfs):
        process_pdf(pdf_path, config, i + 1, total_pdfs)

    final_message = "Robust PDF processing script has finished."
    print(final_message)
    send_ntfy_notification(final_message, "Script Finished", 'high')

if __name__ == '__main__':
    main()
