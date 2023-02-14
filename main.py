import threading

import requests
from urllib.parse import urlparse
import tkinter as tk

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


def extra_thread(label_text, website):
    if is_valid_url(website):
        label_text.set("Prüfe " + website + " ...")
        return_value = get_possible_cms(website)

        if return_value[0] is not None:
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
    popup.geometry("+{}+{}".format(root_window.winfo_rootx() + 50, root_window.winfo_rooty() + 100))

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

    root.mainloop()
