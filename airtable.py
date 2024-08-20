import os
from pyairtable import Api

api = Api(os.environ['AIRTABLE_API_KEY'])
events_table = api.table(os.environ['AIRTABLE_BASE_ID'], 'Events')
events_registration_table = api.table(os.environ['AIRTABLE_BASE_ID'], 'Event Registrations')
