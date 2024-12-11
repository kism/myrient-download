import os
from zipfile import ZipFile
import requests
from tqdm import tqdm
from urllib.parse import quote  # Add this for URL encoding

MYRIENT_URL = 'https://myrient.erista.me/files/No-Intro/'
DOWNLOAD_DIR = r'\\TUCKER-DESKTOP\Shared S Drive'
EXTRACT_ZIP = False
SKIP_EXISTING = True
SYSTEMS = ["Nintendo - Nintendo Entertainment System (Headered)", "Nintendo - Super Nintendo Entertainment System"]
SYSTEM_WHITELIST = []
SYSTEM_BLACKLIST = []
GAME_WHITELIST = ["(USA)"]
GAME_BLACKLIST = ["Demo", "BIOS", "(Proto)", "(Beta)", "(Program)"]

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

def get_files_list(url):
    print(f'Getting file list from: {url}')
    try:
        # Encode URL properly
        encoded_url = quote(url, safe=':/')
        response = requests.get(encoded_url, headers=HEADERS)
        response.raise_for_status()
        
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.text, 'html.parser')
        files = []
        # Look for links in the table with id='list'
        table = soup.find('table', id='list')
        if table:
            for link in table.find_all('a'):
                href = link.get('title')  # Use title instead of href
                if href and href.endswith('.zip'):
                    files.append(href)
        return files
    except Exception as e:
        print(f"Error getting file list: {e}")
        return []

def download_file(url, destination):
    try:
        encoded_url = quote(url, safe=':/')
        response = requests.get(encoded_url, headers=HEADERS, stream=True)
        response.raise_for_status()
        total_size = int(response.headers.get('content-length', 0))
        
        with open(destination, 'wb') as f:
            with tqdm(total=total_size, unit='iB', unit_scale=True) as pbar:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        size = f.write(chunk)
                        pbar.update(size)
        return True
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        return False

def download_files(filtered_files, base_url, download_dir, system):
    # Create system-specific directory
    system_dir = os.path.join(download_dir, system)
    os.makedirs(system_dir, exist_ok=True)
    
    for file_name in tqdm(filtered_files, desc="Processing files", unit="file"):
        # Put files in their system directory
        zip_file = os.path.join(system_dir, file_name)
        
        if SKIP_EXISTING and os.path.exists(zip_file):
            print(f"Skipping {file_name} - already exists")
            continue
        
        # Download the file
        file_url = f"{base_url}{file_name}"
        print(f"Downloading: {file_name}")
        if download_file(file_url, zip_file):
            print(f"Successfully downloaded: {file_name}")

def main():
    # Process each system
    for system in SYSTEMS:
        system_url = f'{MYRIENT_URL}{system}/'
        files_list = get_files_list(system_url)
        
        # Apply filters
        filtered_files = [f for f in files_list
                         if any(term in f for term in GAME_WHITELIST)
                         and not any(term in f for term in GAME_BLACKLIST)]
        
        if filtered_files:
            print(f"\nFound {len(filtered_files)} matching files for {system}")
            # Pass the system name to download_files
            download_files(filtered_files, system_url, DOWNLOAD_DIR, system)
        else:
            print(f"No matching files found for {system}")

if __name__ == "__main__":
    # Make sure base download directory exists
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)
    main()
