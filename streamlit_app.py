# native libraries
import datetime
import re
import requests
from time import sleep

# html parsing libraries
from bs4 import BeautifulSoup, Tag

# streamlit itself
import streamlit as st

# TODO: Use streamlit state
# TODO: Handle errors better

# Updates this script every 3 minutes
UPDATE_INTERVAL = 3 * 60  # seconds
URL = "https://www.uio.no/studier/emner/ledige-plasser/"
TIMEOUT = 10  # seconds


def get_courses(soup: BeautifulSoup) -> list[Tag]:
    table = soup.find("table", id=lambda x: x.find("naturvitenskapelige") > -1)
    if table is None or not isinstance(table, Tag):
        st.write("Fant ingen emner, sjekk at nettsiden er riktig.")
        return []

    elements = table.find_all("td", class_="vrtx-free-capacity-course-description-name")

    pattern = re.compile(r"^(IN|MAT|STK)")
    courses = [
        element
        for element in elements
        if isinstance(element, Tag) and pattern.match(element.text)
    ]

    return list(courses)


def last_updated(soup: BeautifulSoup) -> str:
    element = soup.find("span", class_="last-updated")
    if element is None or not isinstance(element, Tag):
        return "N/A"

    return element.text


def makeHref(course_text: str) -> str:
    course_code = course_text.split(" - ")[0]  # Extract course code (e.g., "IN1000")

    # Get the course prefix (e.g., "IN", "MAT", "STK", "STK-MAT")
    course_prefix = re.match(r"([A-Z-]+)", course_code)
    if course_prefix is None:
        return "#"

    match course_prefix.group(1):
        case "MAT" | "STK-MAT":
            topic = "math"
        case "STK":
            topic = "STK"
        case _:
            topic = "ifi"  # default fallback

    return f"https://www.uio.no/studier/emner/matnat/{topic}/{course_code}/index.html"


st.set_page_config(page_title="Ledige Emner UiO", page_icon="📚", layout="centered")
st.title(
    f"Ledige Emner for Informatikk, Matematikk og Statistikk kurs ved UiO {datetime.datetime.now().year}"
)
# st.caption("Henter data fra UiO...")

response = requests.get(URL, timeout=TIMEOUT)
if response.status_code != 200:
    st.write(
        f"Kunne ikke hente data (url: {URL}) (status code: {response.status_code})"
    )
else:
    soup = BeautifulSoup(response.content, "html.parser")
    st.caption(
        f"Sist oppdatert: {last_updated(soup)}, oppdaterings interval hvert: {int(UPDATE_INTERVAL / 60)} minutt."
    )
    st.divider()

    courses = get_courses(soup)
    for course in courses:
        st.markdown(
            f"* [{course.text}]({makeHref(course.text)})", unsafe_allow_html=True
        )

sleep(UPDATE_INTERVAL)
st.rerun()
