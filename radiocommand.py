"""Command line interface for looking up callsigns."""

from bs4 import BeautifulSoup as Soup
import re
import requests
import time
from getpass import getpass


def main():
    print("[Starting RADIOCOMMAND]")
    print("[Creating a session...]\n")

    radio = RadioCommandSession()
    email: str = input("Enter QRZ.com email or callsign: ")
    password: str = getpass("Enter QRZ.com password: ")
    try:
        radio.loginQrz(email, password)
    except Exception as e:
        print(f"Error: Could not login. {e}")
        main()
    time.sleep(2)
    print("[Authentication successful]")
    try:
        while True:
            callsign = input("[Enter callsign]: ")
            ham = radio.queryCallsign(callsign)
            print(f"NAME: {ham['name']}")
            print(f"CALLSIGN: {ham['callsign']}")
            print(f"ADDRESS: {ham['address']}")
            print(f"EMAIL: {ham['email']}")
            print(f"NATION: {ham['nation']}")
            print(f"PIC LINK: {ham['profile_pic']}")
            print()
    except KeyboardInterrupt:
        print("[Session ending...]")
        print("[Logging out]")


class RadioCommandSession:

    def __init__(self):
        self.session: requests.Session = requests.Session()

    def loginQrz(self, login: str, password: str):
        payload = {"username": login, "password": password}
        self.session.post("https://www.qrz.com/login", data=payload)

    def queryCallsign(self, callsign: str) -> str:
        # Alternate url
        # "https://www.qrz.com/lookup?tquery={callsign}&mode=callsign"
        QRZ: str = f"https://www.qrz.com/db/{callsign}"
        response = self.session.get(QRZ)

        soup = Soup(response.text, "html.parser")
        try:
            name = soup.find(
                style="color: black; font-weight: bold").get_text()
        except AttributeError:
            name = None
            pass

        try:
            address = soup.find(
                style="color: #666; font-weight: normal; font-size: 17px").get_text()
        except AttributeError:
            address = None
            pass

        try:
            email = soup.find(id="eml").get_text()
        except AttributeError:
            email = None
            pass

        try:
            nation = soup.find(span="position:relative;top:-8px;").get_text()
        except AttributeError:
            nation = None
            pass

        try:
            picTag = soup.find(id="mypic")
            if picTag and "static/qrz/qrz_com200x150.jpg" in picTag:  # Default profile picture
                pic = None
            else:
                pic = re.search("src=\"(http.*)/>", picTag)
        except Exception:
            pic = None
            pass

        return {
            "name": name,
            "callsign": callsign.upper(),
            "address": address,
            "email": email,
            "nation": nation,
            "profile_pic": pic
        }


if __name__ == "__main__":
    main()
