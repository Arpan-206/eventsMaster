from typing import Union

from fastapi import FastAPI
import airtable as at

app = FastAPI(
    title="Hack Club Events API",
    description="An API for Hack Club Events",
    version="0.1.0",
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT"
    },
    contact={
        "name": "Arpan Pandey",
        "email": "arpan@hackclub.com"
    }
)

@app.get("/")
def get_events():
    return at.get_events()

@app.get("/past")
def get_past_events():
    return at.get_past_events()

@app.get("/upcoming")
def get_upcoming_events():
    return at.get_upcoming_events()

@app.get("/event/{event_slug}")
def get_event(event_slug: str):
    return at.clean_dict_and_eve(at.get_event_by_slug(event_slug))

@app.post("/register")
def register_for_event(event_slug: str, name: str, slack_id: str, email: str):
    return at.register_for_event(event_slug, name, slack_id, email)
