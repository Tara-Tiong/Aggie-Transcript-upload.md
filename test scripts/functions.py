# from selenium import webdriver
# from selenium.webdriver.chrome.service import Service as ChromeService
# from selenium.webdriver.chrome.options import Options
# from selenium.webdriver.common.by import By
# import json
# import time
# from bs4 import BeautifulSoup
# from datetime import datetime
# import xml.etree.ElementTree as ET


# def convert_date(date_str):
#     # Remove any 'th', 'st', 'nd', 'rd' suffixes from the day
#     date_str = date_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')

#     # Convert to a datetime object
#     date_obj = datetime.strptime(date_str, '%B %d, %Y')

#     # Format as 'MM/DD/YYYY'
#     formatted_date = date_obj.strftime('%m/%d/%Y')

#     return formatted_date

# new = convert_date("April 9th, 2019")

# print(new)

from datetime import datetime

def convert_date(date_str):
    try:
        # Remove any 'th', 'st', 'nd', 'rd' suffixes from the day
        date_str = date_str.replace('th', '').replace('st', '').replace('nd', '').replace('rd', '')

        # Attempt to convert to a datetime object
        date_obj = datetime.strptime(date_str, '%B %d, %Y')

        # Format as 'MM/DD/YYYY'
        formatted_date = date_obj.strftime('%m/%d/%Y')
        return formatted_date

    except ValueError as e:
        # Log the error
        print(f"Error converting date: {e}. Original date string: {date_str}")

        # Attempt to correct common typos, e.g., 'Augu' -> 'August'
        corrections = {
            'Augu': 'August',
            'Sept': 'September',  # Sometimes 'Sept' is used instead of 'September'
            'Octo': 'October',    # Example typo
        }

        # Look for and fix common typos in month names
        for typo, correct in corrections.items():
            if typo in date_str:
                date_str = date_str.replace(typo, correct)
                break  # Apply the first fix we find and try again

        # Try parsing the corrected date
        try:
            date_obj = datetime.strptime(date_str, '%B %d, %Y')
            formatted_date = date_obj.strftime('%m/%d/%Y')
            return formatted_date
        except ValueError as e:
            # Log the failure to convert even after corrections
            print(f"Failed to convert date after correction: {e}. Final date string: {date_str}")
            return "Invalid date"  # Fallback return for badly formatted dates

# Example usage
new_date = convert_date("Augu 29, 2020")
print(new_date)
