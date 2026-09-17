# APK Analyzer – Automated URL & Network Indicator Extractor

A Python-based static analysis utility designed to automate the extraction of hidden HTTP/HTTPS URLs and Firebase endpoints from APKs and firmware binaries.

## Overview

Analyzing suspicious APKs and firmware files can involve manually extracting files and searching through large amounts of raw binary data for network indicators.

This project automates that initial triage process by combining Binwalk-based extraction with recursive binary scanning and pattern matching.

## How It Works

1. The user provides an APK or firmware file.
2. Binwalk recursively extracts embedded files and artifacts.
3. The tool scans the extracted directory recursively.
4. Binary files are read directly in binary mode.
5. Regular expressions identify HTTP/HTTPS URLs and Firebase-related endpoints.
6. Duplicate indicators are removed.
7. A structured HTML report is generated.

## Key Features

- Automated Binwalk extraction
- Recursive artifact scanning
- Binary-level URL extraction
- HTTP/HTTPS endpoint detection
- Firebase endpoint detection
- Duplicate URL removal
- HTML report generation
- Command-line interface

## Technologies Used

- Python 3
- Binwalk
- Regular Expressions
- Linux
- HTML

## Usage

```bash
python3 apk_analyzer.py -f target.apk