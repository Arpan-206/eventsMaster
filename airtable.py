import os
from pyairtable import Api
from dotenv import load_dotenv
from datetime import datetime, timezone
from pyairtable.orm import Model, fields as F

load_dotenv()

api = Api(os.environ['AIRTABLE_API_KEY'])

def clean_dict_and_eve(event):
    x = {
        'id': event.id,
        'slug': event.slug,
        'title': event.title,
        'description': event.description,
        'start_time': event.start_time,
        'end_time': event.end_time,
        'type_of_event': event.type_of_event,
        'owner': event.owner,
        'announcement_post': event.announcement_post,
        'sad_event': event.sad_event,
        'time50_link': event.time50_link
    }
    return x

def clean_dict_and_reg(reg):
    x = {
        'id': reg.id,
        'event': [clean_dict_and_eve(e) for e in reg.event][0],
        'name': reg.name,
        'slack_id': reg.slack_id,
        'email': reg.email
    }
    return x

class Event(Model):
    slug = F.TextField('Slug')
    title = F.TextField('Title')
    description = F.TextField('Description')
    start_time = F.DatetimeField('Start Time')
    end_time = F.DatetimeField('End Time')
    type_of_event = F.TextField('Type of Event')
    owner = F.TextField('Owner')
    announcement_post = F.UrlField('Announcement Post')
    sad_event = F.CheckboxField('SAD Event')
    time50_link = F.UrlField('Time50 Link', readonly=True)
    sad_liaison = F.CollaboratorField('SAD Liaison', readonly=True)

    class Meta:
        table_name = 'Events'
        base_id = os.environ['AIRTABLE_BASE_ID']
        api_key = os.environ['AIRTABLE_API_KEY']

class EventRegistration(Model):
    event = F.LinkField('Event', Event)
    name = F.TextField('Name')
    slack_id = F.TextField('Slack ID')
    email = F.EmailField('Email')

    class Meta:
        table_name = 'Event Registrations'
        base_id = os.environ['AIRTABLE_BASE_ID']
        api_key = os.environ['AIRTABLE_API_KEY']


def get_events() -> list[dict]:
    # only return fields and ID
    x = Event.all()
    return [clean_dict_and_eve(e) for e in x]

def get_past_events() -> list[dict]:
    eve = Event.all()
    return [clean_dict_and_eve(e) for e in eve if e.end_time < datetime.now().replace(tzinfo=timezone.utc)]

def get_upcoming_events() -> list[dict]:
    eve = Event.all()
    return [clean_dict_and_eve(e) for e in eve if e.start_time > datetime.now().replace(tzinfo=timezone.utc)]

def get_ongoing_events() -> list[dict]:
    eve = Event.all()
    return [clean_dict_and_eve(e) for e in eve if e.start_time < datetime.now().replace(tzinfo=timezone.utc) and e.end_time > datetime.now().replace(tzinfo=timezone.utc)]

def get_event_by_slug(slug: str) -> Event | None:
    eve = Event.all()
    for e in eve:
        if e.slug == slug:
            return e
    return None

def get_event_by_id(id: str) -> Event:
    return Event.from_id(id)

def get_event_registrations(event_slug: str) -> list[dict]:
    eve = get_event_by_slug(event_slug)
    reg = EventRegistration.all()
    return [clean_dict_and_reg(r) for r in reg if r.event == eve]

def register_for_event(event_slug: str, name: str, slack_id: str, email: str) -> dict:
    eve = get_event_by_slug(event_slug)
    reg = EventRegistration(event=[eve], name=name, slack_id=slack_id, email=email)
    # reg.save()
    return clean_dict_and_reg(reg)
