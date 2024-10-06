# Databroker-Reporting-Tool
"An automation tool designed to help users report data broker websites that display and sell personal information. By collectively reporting these sites to Google Safe Browsing, we can help protect our privacy without relying on costly services that can still be prone to leaks."


# Databroker Reporting Tool

This Python tool helps automate the process of reporting data broker websites to Google Safe Browsing, aiming to protect user privacy. By reporting these websites, users can reduce the unauthorized sale of personal data without relying on costly data removal services.

## How it Works
1. The tool automatically submits URLs to the Google Safe Browsing report form.
2. Users can solve CAPTCHA challenges manually, or use the Buster CAPTCHA solver for automation.

## Setup Instructions
- Requires Firefox and the [Buster CAPTCHA Solver](https://addons.mozilla.org/en-US/firefox/addon/buster-captcha-solver/) add-on.
- Install dependencies and run the script.

## Usage
Run the script using:
```bash
python3 captcha_report_tool_full.py
