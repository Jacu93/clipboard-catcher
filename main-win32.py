import logging
import os
import sys
import tempfile

import servicemanager
import win32serviceutil
import win32service
import win32event
import win32clipboard
import time
import webbrowser
import xml.etree.ElementTree as ET


class ClipboardMonitorService(win32serviceutil.ServiceFramework):
    _svc_name_ = "ClipboardMonitorService"
    _svc_display_name_ = "Clipboard Monitoring Service"
    _svc_description_ = "Monitors the clipboard for specific XML content and opens a URL."

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        log_file_path = os.path.join(tempfile.gettempdir(), 'clipboard_service.log')
        logging.basicConfig(
            filename=log_file_path,  # Logs to the system's temp directory
            level=logging.DEBUG,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.is_running = True
        logging.info("Service Initialized")

    def SvcStop(self):
        logging.info("Service is stopping...")
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        self.is_running = False
        win32event.SetEvent(self.hWaitStop)

    def SvcDoRun(self):
        self.is_running = True
        logging.info("Service is starting...")
        self.ReportServiceStatus(win32service.SERVICE_RUNNING)

        try:
            self.monitor_clipboard()
        except Exception as e:
            logging.error(f"Error in monitor_clipboard: {e}")
            self.SvcStop()

    def monitor_clipboard(self):
        logging.info("monitor_clipboard start")
        last_clipboard = ""
        predefined_url = "http://google.com"

        while self.is_running:
            try:
                logging.info("get clipboard content")
                clipboard_content = self.get_clipboard_content()
                logging.info(f"Clipboard content: {clipboard_content}")
            except Exception as e:
                logging.error(f"Error accessing clipboard: {e}")
                time.sleep(1)  # If clipboard fails, wait a second and retry
                continue

            if clipboard_content and clipboard_content != last_clipboard:
                logging.info("new clipboard content detected")
                last_clipboard = clipboard_content
                if self.is_valid_xml(clipboard_content):
                    webbrowser.open(predefined_url)
                    logging.info("Valid XML detected, browser opened.")
            time.sleep(1)

    def get_clipboard_content(self):
        try:
            win32clipboard.OpenClipboard()
            if win32clipboard.IsClipboardFormatAvailable(win32clipboard.CF_UNICODETEXT):
                data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
                return data
            return ""
        except Exception as e:
            logging.error(f"Error in get_clipboard_content: {e}")
            return ""
        finally:
            win32clipboard.CloseClipboard()

    def is_valid_xml(self, content):
        logging.info("is_valid_xml")
        required_xml = "<root><element>value</element></root>"
        try:
            tree = ET.ElementTree(ET.fromstring(content))
            return ET.tostring(tree.getroot(), encoding='unicode') == required_xml
        except ET.ParseError as e:
            logging.error(f"Invalid XML format: {e}")
            return False


if __name__ == '__main__':
    try:
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(ClipboardMonitorService)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(ClipboardMonitorService)
    except Exception as e:
        logging.error(f"Error while starting service: {e}")