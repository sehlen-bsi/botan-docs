#!/usr/bin/python

import ctypes
import subprocess
import sys
import time
import pyperclip
import re

kernel32 = ctypes.windll.kernel32
kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
kernel32.GlobalLock.restype = ctypes.c_void_p
kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
user32 = ctypes.windll.user32
user32.GetClipboardData.restype = ctypes.c_void_p

def run(cmd, stdin):
    vc = subprocess.Popen(cmd,
                          stdout=subprocess.PIPE,
                          stderr=subprocess.PIPE,
                          stdin=subprocess.PIPE)
    (stdout, stderr) = vc.communicate(stdin, timeout=1)
    if stderr:
        print(stderr, file=sys.stderr)
    return stdout


def filter_html(html_utf8):
    html = html_utf8.decode("utf-8")

    # the <span> tags confuse pandoc somehow
    span = re.compile(r"(<span[^>]*>|</span>)")
    filtered_html = span.sub("", html)

    return filtered_html.encode("utf-8")


def add_rst_table_header(rst):
    header = ".. table::\n   :class: longtable\n   :widths: 20 80\n\n"
    return header +"\n".join([f"   {s}" for s in rst.splitlines()])


def is_format_available(format):
    return user32.IsClipboardFormatAvailable(format)


def get_clipboard_as(format):
    if not is_format_available(format):
        return None

    data = user32.GetClipboardData(format)
    data_locked = kernel32.GlobalLock(data)
    text = ctypes.c_char_p(data_locked)
    value = text.value
    kernel32.GlobalUnlock(data_locked)

    return value


def try_finding_html_format_number():
    format_number = 0
    while True:
        format_number = user32.EnumClipboardFormats(format_number)
        if format_number == 0:
            break
        try:
            value_str = get_clipboard_as(format_number).decode("utf-8")
            if value_str.startswith("<!DOCTYPE HTML PUBLIC"):
                return format_number
        except:
            pass

    return None


html_format = None
def is_html_format_available():
    global html_format
    if not html_format:
        html_format = try_finding_html_format_number()
        if not html_format:
            return False
        print("Found clipboard format containing HTML: %d" % html_format)

    return is_format_available(html_format)


def get_clipboard_as_html():
    try:
        user32.OpenClipboard(0)
        if not is_html_format_available():
            return None

        return get_clipboard_as(html_format)
    finally:
        user32.CloseClipboard()


print("Waiting for input...")
last_html = None
while True:
    time.sleep(1)

    html = get_clipboard_as_html()
    if not html or html == last_html:
        continue
    last_html = html

    print("Got new LibreOffice table, converting...")
    html = filter_html(html)
    rst = run(["pandoc", "--from=html", "--to=rst", "--wrap=auto", "--columns=100"], html)

    rst_table = add_rst_table_header(rst.decode("utf-8"))
    pyperclip.copy(rst_table)

    print("C'est partie...")
