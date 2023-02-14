import requests
from urllib.parse import urlparse
import tkinter as tk


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
    elif response.status_code == 404:
        return False
    else:
        response.raise_for_status()  # raise an exception for any other status code


def check_url(website):
    if not website.startswith("https://") or website.startswith("http://"):
        website = "https://" + website

    if not website.endswith("/"):
        website = website + "/"

    print("Checking URL: " + website)

    cms_list = {
        "Wordpress": ["wp-login.php", "wp-admin"],
        "TYPO3": ["typo3"],
        "Contao (TYPOlight)": ["contao"],
        "Drupal": ["user/login", "user"],
        "Joomla": ["administrator"],
        "Magento": ["admin", "admin/dashboard"],
        "PrestaShop": ["admin123"],
        "Shopify": ["admin", "admin/auth/login"]
    }

    if is_valid_url(website):
        found_path = None
        possible_cms = []
        for cms, paths in cms_list.items():
            for path in paths:
                c_url = website + path
                reachable = is_website_reachable(c_url)

                if reachable:
                    found_path = c_url
                    possible_cms.append(cms)
                    break

        if found_path is not None:
            print("Die URL '" + found_path + "' konnte gefunden werden.")

            if len(possible_cms) > 1:
                print("Mögliche CMS-Systeme sind daher: " + ", ".join(possible_cms))
                print(
                    "Rufe die URL am besten einmal auf, meistens lässt sich an einem Schriftzug erkennen, um welches CMS es sich genau handelt.")

            else:
                print("Wahrscheinlich ist auf dieser URL " + "".join(possible_cms) + " installiert.")

        else:
            print("Es konnte keines der verfügbaren CMS-Systeme (" + ", ".join(
                cms_list.keys()) + ") gefunden werden.")
            print(
                "Bitte beachte, dass dies keine 100%ige Garantie ist, dass auf dieser URL kein CMS installiert ist, da dieses Skript lediglich Standard-URLs testet, die auch vom Seitenbetreiber geändert worden sein können.")

    else:
        print("Die angegebene URL ist nicht valide.")


if __name__ == "__main__":
    root = tk.Tk()
    root.title("CMS Check by Marvin Roßkothen")

    frame = tk.Frame(root)
    frame.pack(padx=40, pady=20)

    url_input = tk.Entry(frame, width=40)
    url_input.bind("<Return>", lambda event: check_url(url_input.get()))
    url_input.pack()

    button = tk.Button(frame, text="Prüfen", command=lambda: check_url(url_input.get()))
    button.pack()

    root.mainloop()
