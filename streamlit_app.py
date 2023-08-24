# native libraries
import datetime
import re
import requests
from time import sleep

# html parsing libraries
import html5lib
from bs4 import BeautifulSoup

# streamlit itself
import streamlit as st

# TODO: Use streamlit state
# TODO: Handle errors better

def get_courses(soup: BeautifulSoup) -> list[str]:
  table = soup.find('table', id=lambda x: x.find('naturvitenskapelige') > -1)
  elements = table.find_all('td', class_='vrtx-free-capacity-course-description-name')
  
  pattern = re.compile(r'^(IN|MAT|STK)')
  return list(filter(
    lambda element: pattern.match(element.text), elements
  ))

def last_updated(soup: BeautifulSoup) -> str: 
  return soup.find('span', class_='last-updated').text

st.title(f"Ledige Emner for Informatikk, Matematikk og Statistikk kurs ved UiO {datetime.datetime.now().year}")
url = 'https://www.uio.no/studier/emner/ledige-plasser/#det-matematisk-naturvitenskapelige-fakultet'
response = requests.get(url)
if response.status_code != 200:
  st.write(f"Kunne ikke hente data (url: {url}) (status code: {response.status_code})")
else:
  soup = BeautifulSoup(response.content, 'html5lib')
  st.caption(f"Sist oppdatert: {last_updated(soup)}")
  st.markdown('---')
  st.markdown(
    str.join(
      '\n', [
        f"* {course.text}" for course in get_courses(soup)]
    )
  )

# Rerun this script every 1min
sleep(60)
st.experimental_rerun()
