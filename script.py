import pyperclip
import time
import webbrowser
import xml.etree.ElementTree as ET

# Predefined URL to open
predefined_url = "http://google.com"

# XML structure to match
required_xml = "<root><element>value</element></root>"


def is_valid_xml(content):
    try:
        # Try to parse the clipboard content as XML
        tree = ET.ElementTree(ET.fromstring(content))
        # You can extend this to check specific elements, attributes, etc.
        return ET.tostring(tree.getroot(), encoding='unicode') == required_xml
    except ET.ParseError:
        return False


def monitor_clipboard():
    last_clipboard = ""
    while True:
        # Get the current content of the clipboard
        clipboard_content = pyperclip.paste()

        if clipboard_content != last_clipboard:
            last_clipboard = clipboard_content

            if is_valid_xml(clipboard_content):
                print("Valid XML detected, opening the browser...")
                webbrowser.open(predefined_url)

        # Sleep for a short period to avoid high CPU usage
        time.sleep(1)


if __name__ == "__main__":
    monitor_clipboard()