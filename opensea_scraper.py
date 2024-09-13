import os
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import csv
import logging
import time

# Configure logging
logging.basicConfig(
    filename='opensea_scraper.log',
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s:%(message)s'
)

class OpenSeaScraperApp:
    def __init__(self, master):
        self.master = master
        master.title("OpenSea NFT Image Scraper")

        # Initialize API Key
        self.api_key = ""

        # Main Frame
        self.main_frame = ttk.Frame(master, padding="10")
        self.main_frame.grid(row=0, column=0, sticky=(tk.N, tk.W, tk.E, tk.S))

        # Collection Slug Input
        self.label = ttk.Label(self.main_frame, text="Enter Collection Slug:")
        self.label.grid(row=0, column=0, sticky=tk.W)

        self.slug_entry = ttk.Entry(self.main_frame, width=50)
        self.slug_entry.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E))

        # Fetch Data Button
        self.fetch_button = ttk.Button(self.main_frame, text="Fetch Data", command=self.fetch_data)
        self.fetch_button.grid(row=2, column=0, pady=5)

        # Progress Bar
        self.progress = ttk.Progressbar(self.main_frame, orient=tk.HORIZONTAL, length=400, mode='determinate')
        self.progress.grid(row=3, column=0, columnspan=2, pady=5)

        # Export Metadata Button
        self.export_button = ttk.Button(self.main_frame, text="Export Metadata", command=self.export_metadata)
        self.export_button.grid(row=4, column=0, columnspan=2, pady=5)
        self.export_button.config(state=tk.DISABLED)

        # Initialize assets list
        self.assets = []
        self.total_assets = 0

        # Add a status label
        self.status_label = ttk.Label(self.main_frame, text="Ready")
        self.status_label.grid(row=5, column=0, columnspan=2, pady=5)

        # Add a download path entry
        self.download_label = ttk.Label(self.main_frame, text="Download Path:")
        self.download_label.grid(row=6, column=0, sticky=tk.W)
        self.download_path_entry = ttk.Entry(self.main_frame, width=50)
        self.download_path_entry.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E))
        self.browse_button = ttk.Button(self.main_frame, text="Browse", command=self.browse_download_path)
        self.browse_button.grid(row=7, column=2, pady=5)

    def browse_download_path(self):
        directory = filedialog.askdirectory()
        if directory:
            self.download_path_entry.delete(0, tk.END)
            self.download_path_entry.insert(0, directory)

    def fetch_data(self):
        slug = self.slug_entry.get().strip()
        download_path = self.download_path_entry.get().strip()
        if not slug:
            messagebox.showerror("Input Error", "Please enter a collection slug.")
            return
        if not download_path:
            messagebox.showerror("Input Error", "Please specify a download path.")
            return
        if not self.api_key:
            messagebox.showerror("API Key Error", "Please set your OpenSea API key in the settings.")
            return

        logging.info(f"Starting fetch for collection: {slug}")

        # Disable buttons during fetch
        self.fetch_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)

        threading.Thread(target=self.get_and_download_assets, args=(slug, download_path)).start()

    def get_and_download_assets(self, slug, download_path):
        self.assets = []
        self.total_assets = 0
        self.progress['value'] = 0
        self.progress['maximum'] = 7777  # Set to expected total

        headers = {
            "Accept": "application/json",
            "X-API-KEY": self.api_key
        }

        # First, get the contract address
        try:
            collection_url = f"https://api.opensea.io/api/v2/collections/{slug}"
            response = requests.get(collection_url, headers=headers)
            response.raise_for_status()
            collection_data = response.json()
            contract_address = collection_data['contracts'][0]['address']
            chain = collection_data['contracts'][0]['chain']
        except Exception as e:
            logging.error(f"Failed to get collection info: {e}")
            self.update_status(f"Error: Failed to get collection info")
            messagebox.showerror("Error", f"Failed to get collection info: {e}")
            self.fetch_button.config(state=tk.NORMAL)
            return

        for token_id in range(7777):  # Assuming token IDs start from 0
            if self.total_assets >= 7777:
                break

            try:
                self.update_status(f"Fetching and downloading asset {token_id + 1} of 7777...")
                url = f"https://api.opensea.io/api/v2/chain/{chain}/contract/{contract_address}/nfts/{token_id}"
                response = requests.get(url, headers=headers)
                
                if response.status_code == 404:
                    logging.info(f"Asset {token_id} not found, skipping.")
                    continue
                
                response.raise_for_status()
                asset = response.json()['nft']

                self.assets.append(asset)
                self.download_asset(asset, download_path)

                self.total_assets += 1
                self.progress['value'] = self.total_assets
                self.update_status(f"Fetched and downloaded {self.total_assets} assets so far...")

                time.sleep(0.1)  # Delay to avoid rate limiting

            except requests.exceptions.RequestException as e:
                logging.error(f"Request Error for asset {token_id}: {e}")
                self.update_status(f"Error fetching asset {token_id}: {e}")
            except Exception as e:
                logging.error(f"Unexpected Error for asset {token_id}: {e}")
                self.update_status(f"Error processing asset {token_id}: {e}")

        if self.assets:
            self.update_status(f"Fetch and download complete. Total assets: {len(self.assets)}")
            messagebox.showinfo("Success", f"Fetched and downloaded {len(self.assets)} assets.")
            self.export_button.config(state=tk.NORMAL)
        else:
            self.update_status("No assets found for this collection.")
            messagebox.showwarning("No Assets Found", "No assets were found for this collection.")

        self.fetch_button.config(state=tk.NORMAL)
        logging.info(f"Fetch and download completed. Total assets: {len(self.assets)}")

    def download_asset(self, asset, directory):
        image_url = asset.get('image_url')
        if image_url:
            if image_url.startswith('ipfs://'):
                image_url = image_url.replace('ipfs://', 'https://ipfs.io/ipfs/')

            token_id = asset.get('identifier')
            name = asset.get('name') or f"Token_{token_id}"
            file_extension = os.path.splitext(image_url)[-1]
            if not file_extension or len(file_extension) > 5:
                file_extension = '.png'
            safe_name = "".join(x if x.isalnum() else "_" for x in name)
            filename = f"{safe_name}{file_extension}"
            filepath = os.path.join(directory, filename)

            try:
                img_response = requests.get(image_url, stream=True, timeout=30)
                img_response.raise_for_status()
                with open(filepath, 'wb') as handler:
                    for chunk in img_response.iter_content(chunk_size=8192):
                        handler.write(chunk)
                logging.debug(f"Downloaded image: {filepath}")
            except Exception as e:
                logging.error(f"Failed to download {name}: {e}")

    def export_metadata(self):
        file = filedialog.asksaveasfilename(defaultextension=".csv",
                                            filetypes=[("CSV files", "*.csv"), ("All files", "*.*")])
        if not file:
            return

        # Disable buttons during export
        self.fetch_button.config(state=tk.DISABLED)
        self.export_button.config(state=tk.DISABLED)

        threading.Thread(target=self.save_metadata, args=(file,)).start()

    def save_metadata(self, file):
        # Collect all keys from the metadata
        keys = set()
        for asset in self.assets:
            keys.update(asset.keys())

        keys = list(keys)
        total_assets = len(self.assets)
        self.progress['maximum'] = total_assets
        self.progress['value'] = 0

        with open(file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=keys)
            writer.writeheader()
            for i, asset in enumerate(self.assets, 1):
                writer.writerow(asset)
                self.progress['value'] = i
                self.update_status(f"Exporting metadata: {i}/{total_assets}")

        self.update_status("Metadata export complete")
        messagebox.showinfo("Export Complete", "Metadata has been exported to CSV.")
        # Re-enable buttons after export
        self.fetch_button.config(state=tk.NORMAL)
        self.export_button.config(state=tk.NORMAL)

    def update_status(self, message):
        self.status_label.config(text=message)
        self.master.update_idletasks()  # Force update of the GUI

    def set_api_key(self):
        # Create a new window to input the API key
        self.api_key_window = tk.Toplevel(self.master)
        self.api_key_window.title("Set API Key")

        label = ttk.Label(self.api_key_window, text="Enter your OpenSea API Key:")
        label.pack(pady=5)

        self.api_key_entry = ttk.Entry(self.api_key_window, width=50, show="*")
        self.api_key_entry.pack(pady=5)

        save_button = ttk.Button(self.api_key_window, text="Save", command=self.save_api_key)
        save_button.pack(pady=5)

    def save_api_key(self):
        self.api_key = self.api_key_entry.get().strip()
        if self.api_key:
            messagebox.showinfo("API Key Set", "Your API key has been set.")
            self.api_key_window.destroy()
        else:
            messagebox.showerror("API Key Error", "API key cannot be empty.")

def main():
    root = tk.Tk()
    app = OpenSeaScraperApp(root)

    # Create Menu
    menubar = tk.Menu(root)
    root.config(menu=menubar)

    # Add API Key Menu
    settings_menu = tk.Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Settings", menu=settings_menu)
    settings_menu.add_command(label="Set API Key", command=app.set_api_key)

    root.mainloop()

if __name__ == "__main__":
    main()
