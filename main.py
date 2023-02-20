import os.path
import threading

import requests
from urllib.parse import urlparse
import tkinter as tk
import json
import time
from datetime import datetime
import webbrowser
import platform
import subprocess

__program__ = 'CMS Check'
__author__ = 'Marvin Roßkothen'
__version__ = '1.0.0'  # do not change

cms_list = {
    "Wordpress": ["wp-login.php", "wp-admin"],
    "TYPO3": ["typo3"],
    "Contao (TYPOlight)": ["contao"],
    "Drupal": ["user/login", "user"],
    "Joomla": ["administrator"],
    "Magento": ["admin", "admin/dashboard"],
    "PrestaShop": ["admin123"],
    "Shopify": ["admin", "admin/auth/login"],
    "CoastCMS": ["cms.php"],
    "Anderes": ["dashboard/login.php"]
}


def is_valid_url(url):
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_website_reachable(url):
    response = requests.head(url)
    if response.status_code == 200:
        return True
    else:
        return False


def get_possible_cms(website):
    found_path = []
    possible_cms = []
    for cms, paths in cms_list.items():
        for path in paths:
            c_url = website + path
            reachable = is_website_reachable(c_url)

            if reachable:
                found_path.append(c_url)
                possible_cms.append(cms)
                break

    return [found_path, possible_cms]


folder = os.path.join(os.path.expanduser("~/Documents"), "CMS-Check")
log_path = os.path.join(folder, 'checks.json')


def millis_to_stamp(millis):
    return datetime.fromtimestamp(millis / 1000.0)


def add_result_to_log(website, result):
    """
    Add the result of a check to the logs.
    :param website: The URL of the checked website.
    :param result: The result of get_possible_cms ([0] => Array of found urls, [1] => Possible Systems)
    """
    os.makedirs(os.path.dirname(log_path), exist_ok=True)

    current_millis = int(round(time.time() * 1000))

    log_data = []
    if os.path.exists(log_path):
        with open(log_path, 'r') as file:
            log_data = json.load(file)

    data = {
        'url': website,
        'paths': result[0],
        'cms': result[1],
        'checkedAt': current_millis
    }

    log_data.append(data)

    with open(log_path, 'w') as file:
        json.dump(log_data, file, indent=4, separators=(',', ': '))


def show_history(root_window):
    history_popup = tk.Toplevel()
    history_popup.title("Verlauf")

    popup_frame = tk.Frame(history_popup)
    history_popup.geometry("+{}+{}".format(root_window.winfo_rootx() // 2, root_window.winfo_rooty() // 2))
    popup_frame.pack(padx=40, pady=20)

    history = []

    if os.path.exists(log_path):
        with open(log_path, 'r') as file:
            history = json.load(file)
            history = history[::-1]

    index = 0
    if len(history) > 0:
        for i in range(0, 3):
            entry = history[index]

            url = entry["url"]
            paths = entry["paths"]
            cms = entry["cms"]
            checkedAt = entry["checkedAt"]

            entry_frame = tk.Frame(popup_frame)

            url_label = tk.Label(entry_frame, text="URL: " + url)
            paths_label = tk.Label(entry_frame, text="Paths: " + ", ".join(paths))
            cms_label = tk.Label(entry_frame, text="CMS: " + ", ".join(cms))

            when = millis_to_stamp(checkedAt)
            checkedAt_label = tk.Label(entry_frame, text="Check-Zeitpunkt: " + str(
                "Am {:02d}.{:02d}.{} um {:02d}:{:02d} Uhr".format(when.day, when.month, when.year, when.hour,
                                                                  when.minute)))

            url_label.pack()
            paths_label.pack()
            cms_label.pack()

            checkedAt_label.pack()

            entry_frame.pack(ipady=30)
            index += 1

        open_log = tk.Button(popup_frame, text="Alle in Logs anzeigen", command=lambda: open_file(log_path))
        open_log.pack()

    else:
        no_history = tk.Label(text="Es wurden noch keine Checks durchgeführt.")
        no_history.pack()

    history_popup.mainloop()


def open_file(filename):
    if platform.system() == 'Windows':
        os.startfile(filename)
    elif platform.system() == 'Darwin':
        subprocess.call(('open', filename))
    else:
        subprocess.call(('xdg-open', filename))

def extra_thread(label_text, website):
    if is_valid_url(website):
        label_text.set("Prüfe " + website + " ...")
        return_value = get_possible_cms(website)

        if len(return_value[0]) != 0:
            if len(return_value[1]) == 1:
                label_text.set("Es handelt sich wahrscheinlich um " + "".join(return_value[1]) + ".")
            else:
                if not len(return_value[1]) >= len(cms_list.keys()) / 2:
                    label_text.set(
                        "Es wurden mehrere mögliche CMS-Systeme gefunden werden: " + ", ".join(
                            return_value[1]) + "\nBitte prüfe folgende URL(s):\n" + "\n".join(return_value[
                                                                                                  0]) + "\n\nMeistens lässt sich auf der Seite ein Schriftzug finden, welcher offenbart, um welches CMS es sich handelt.")
                else:
                    label_text.set(
                        "Es kann sein, dass ein CMS installiert ist, allerdings konnte dieses leider nicht genau ermittelt werden.\nBitte prüfe diese URLs von möglichen festgestellten CMS-Systemen und finde manuell heraus, um welches es sich handelt:\n" + "\n".join(
                            return_value[0]))

        else:
            label_text.set("Es konnte kein CMS ermittelt werden.")

        add_result_to_log(website, return_value)

    else:
        label_text.set("Der angegebene Text ist keine valide URL.")


def check_url(root_window, website):
    if not website.startswith("https://") and not website.startswith("http://"):
        website = "https://" + website

    if not website.endswith("/"):
        website = website + "/"

    popup = tk.Toplevel()
    popup.title("CMS Check for " + website)

    popup_frame = tk.Frame(popup)
    popup.geometry("+{}+{}".format(root_window.winfo_rootx() // 2, root_window.winfo_rooty() // 2))

    popup_frame.pack(padx=40, pady=20)

    label_text = tk.StringVar()
    label_text.set("Prüfe " + website + " ...")

    # Add a Label widget with the text variable
    label = tk.Label(popup_frame, textvariable=label_text)
    label.pack()

    if is_valid_url(website):
        label_text.set("Prüfe " + website + " ...")

        thread = threading.Thread(target=lambda: extra_thread(label_text, website))
        thread.start()

        # with concurrent.futures.ThreadPoolExecutor() as executor:
        #     future = executor.submit(get_possible_cms, website)
        #     return_value = future.result()

    else:
        label_text.set("Der angegebene Text ist keine valide URL.")

    popup.mainloop()


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CMS Check by Marvin Roßkothen")

    frame = tk.Frame(root)
    frame.pack(padx=40, pady=20)

    url_input = tk.Entry(frame, width=40)
    url_input.bind("<Return>", lambda event: check_url(root, url_input.get()))
    url_input.pack()

    button = tk.Button(frame, text="Prüfen", command=lambda: check_url(root, url_input.get()))
    button.pack()

    button = tk.Button(frame, text="Verlauf", command=lambda: show_history(root))
    button.pack()

    root.mainloop()
