Databroker Reporting Tool

An automation tool designed to help users report data broker websites that display and sell personal information. By collectively reporting these sites to Google Safe Browsing, we can help protect our privacy without relying on costly services that can still be prone to leaks.
Overview

This Python tool helps automate the process of reporting data broker websites to Google Safe Browsing, aiming to protect user privacy. By reporting these websites, users can reduce the unauthorized sale of personal data without relying on expensive data removal services.
How it Works

    The tool automatically submits URLs to the Google Safe Browsing report form.
    Users can solve CAPTCHA challenges manually or use the Buster CAPTCHA solver for automation.

Setup Instructions

    Install Firefox and the Buster CAPTCHA Solver add-on.
    Install dependencies (selenium and twocaptcha).
    Download or clone this repository.

Usage

    Update the URLs in the captcha_report_tool_full.py file as needed.
    Run the script using the following command:

bash

python3 captcha_report_tool_full.py

    When prompted, solve the CAPTCHA manually, or let Buster solve it for you.

Why Use This Tool?

By reporting these data broker sites, you help reduce the exposure of personal data. Using this tool collectively can provide a stronger response than relying solely on paid services, which are still vulnerable to data leaks.
License

This project is licensed under the MIT License. See the LICENSE file for details.
