#!/usr/bin/env python3

import os
import sys
import subprocess
import re
import argparse

class BinwalkScraper:
    def __init__(self, target_file):
        self.target_file = target_file
        # Binwalk always names its output folder like _filename.extracted
        self.extracted_dir = f"_{os.path.basename(target_file)}.extracted"
        
        # Regex pattern to match standard URLs and Firebase database links
        self.url_pattern = re.compile(rb'https?://[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}[/\w .?&=-]*')

    def run_binwalk(self):
        """Runs the aggressive Binwalk carving command."""
        print(f"[*] Running heavy Binwalk extraction on: {self.target_file}")
        print("[*] This might take a minute depending on the file size...")
        
        try:
            # Running: binwalk -e -M --dd=".*" <file>
            subprocess.run(
                ["binwalk", "-e", "-M", "--dd=.*", self.target_file], 
                stdout=subprocess.DEVNULL, # Hides the massive wall of text binwalk outputs
                stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            print("[-] Error: 'binwalk' command not found. Is it installed?")
            sys.exit(1)

        if os.path.exists(self.extracted_dir):
            print(f"[+] Extraction complete! Files saved to: {self.extracted_dir}")
            return True
        else:
            print("[-] Binwalk finished, but no files were extracted.")
            return False

    def scrape_for_urls(self):
        """Scans every extracted file for hardcoded URLs."""
        print(f"[*] Scraping all extracted files for URLs and Firebase links...")
        
        results = {}
        total_urls = 0

        for root, dirs, files in os.walk(self.extracted_dir):
            for file in files:
                file_path = os.path.join(root, file)
                
                try:
                    with open(file_path, 'rb') as f:
                        content = f.read()
                        
                        # Find all matching URLs in the raw binary data
                        matches = self.url_pattern.findall(content)
                        
                        if matches:
                            # Decode bytes to strings and remove duplicates using set()
                            clean_urls = list(set([m.decode('utf-8', errors='ignore') for m in matches]))
                            results[file_path] = clean_urls
                            total_urls += len(clean_urls)
                except Exception:
                    # Skip files that can't be read
                    pass

        return results, total_urls

    def generate_report(self, results, total_urls):
        """Prints out the findings in a clean format to the terminal."""
        print("\n" + "="*50)
        print(f"🎯 EXTRACTION REPORT: {total_urls} URLs Found")
        print("="*50)
        
        if not results:
            print("[-] No URLs were found in the extracted files.")
            return

        for file_path, urls in results.items():
            # Now printing the full file_path instead of os.path.basename
            print(f"\n📄 Found in: {file_path}")
            for url in urls:
                if "firebaseio.com" in url or "firebase" in url:
                    print(f" 🔥 [FIREBASE] {url}")
                else:
                    print(f" 🔗 {url}")

    def generate_html_report(self, results, total_urls, output_filename="extraction_report.html"):
        """Generates an HTML report of the findings."""
        print(f"\n[*] Generating HTML report: {output_filename}")
        
        html = f"""<!DOCTYPE html> <html lang="en"> <head> <meta charset="UTF-8"> <title>Extraction Report - {os.path.basename(self.target_file)}</title> <style> body {{ font-family: Arial, sans-serif; background-color: #f4f4f9; color: #333; margin: 20px; }} h1 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }} h2 {{ color: #e74c3c; }} .file-section {{ background: #fff; padding: 15px; margin-bottom: 20px; border-radius: 5px; box-shadow: 0 2px 5px rgba(0,0,0,0.1); }} .file-name {{ font-weight: bold; font-size: 1.2em; color: #2980b9; margin-bottom: 10px; word-break: break-all; }} .url-list {{ list-style-type: none; padding: 0; }} .url-item {{ background: #ecf0f1; margin: 5px 0; padding: 8px; border-left: 4px solid #3498db; word-break: break-all; }} .firebase {{ border-left-color: #e74c3c; font-weight: bold; color: #c0392b; }} </style> </head> <body> <h1>🎯 EXTRACTION REPORT</h1> <h2>Target: {os.path.basename(self.target_file)} | Total URLs Found: {total_urls}</h2> """
        if not results:
            html += "<p>No URLs were found in the extracted files.</p>\n"
        else:
            for file_path, urls in results.items():
                # Now inserting the full file_path into the HTML
                html += f' <div class="file-section">\n'
                html += f' <div class="file-name">📄 Found in: {file_path}</div>\n'
                html += f' <ul class="url-list">\n'
                
                for url in urls:
                    if "firebaseio.com" in url or "firebase" in url:
                        html += f' <li class="url-item firebase">🔥 [FIREBASE] {url}</li>\n'
                    else:
                        html += f' <li class="url-item">🔗 {url}</li>\n'
                
                html += f' </ul>\n </div>\n'

        html += "</body>\n</html>"

        try:
            # Maintained errors='replace' to prevent crashing on malformed characters
            with open(output_filename, 'w', encoding='utf-8', errors='replace') as f:
                f.write(html)
            print(f"[+] Successfully saved HTML report to {output_filename}")
        except Exception as e:
            print(f"[-] Error saving HTML report: {e}")

def main():
    parser = argparse.ArgumentParser(description="Automated Binwalk Carver & URL Scraper")
    parser.add_argument("file", help="The target file to carve (e.g., target.apk)")
    parser.add_argument("--html", action="store_true", help="Output findings to an HTML file")
    
    args = parser.parse_args()

    if not os.path.isfile(args.file):
        print(f"[-] Error: Target file '{args.file}' not found.")
        sys.exit(1)

    scraper = BinwalkScraper(args.file)
    
    if scraper.run_binwalk():
        results, total_urls = scraper.scrape_for_urls()
        
        if args.html:
            scraper.generate_html_report(results, total_urls)
        else:
            scraper.generate_report(results, total_urls)

if __name__ == '__main__':
    main()