from BrowserBot import Browser
from os import getenv
from dotenv import load_dotenv
load_dotenv()


if __name__ == "__main__":
    query = r"site:linkedin.com/in/ OR site:linkedin.com/pub/ Warszawa (Angular OR React) -Manager -Lider"
    browser_instance = Browser(username=getenv('LOGIN'),
                               password=getenv('PASS'),
                               query=query,
                               n_pages=5,
                               quantity=50
                               )
    browser_instance.talent_mapping()




