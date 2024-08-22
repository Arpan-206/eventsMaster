import os
# Use the package we installed
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from datetime import datetime
from pytz import timezone
import airtable as at
from rich import print

from dotenv import load_dotenv
load_dotenv()

# Initialize your app with your bot token and signing secret
app = App(
    token=os.environ.get("SLACK_BOT_TOKEN"),
    signing_secret=os.environ.get("SLACK_SIGNING_SECRET")
)

@app.command("/events")
def events(ack, body, say, respond):
    ack()
    events = at.get_upcoming_events()

    # check if the command was sent in a DM
    if not body['channel_name'] == "directmessage":
        respond("Please use this command in a DM with me.")
        return

    if len(events) == 0:
        respond("No upcoming events!", )
    else:
        data = {
            "type": "home",
            "blocks": [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*Welcome, <@{body['user_id']}>!*"
                    },
                    "accessory": {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Suggest an event!",
                            "emoji": True,

                        },
                        "value": "suggest_event_button_click",
                        "action_id": "suggest_event_button_click"
                    }
                },
            ]
        }

        for event in events:
            if not at.check_registration(event_slug=event['slug'], slack_id=body['user_id']):
                data["blocks"].extend([{
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{event['announcement_post']}|{event['title']}>*\n {event['start_time'].strftime('%B %d, %H:%M')} - {event['end_time'].strftime('%B %d, %H:%M')} UTC |  Convert to your timezone <{event['time50_link']}|here>."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
    					"type": "button",
    					"text": {
    						"type": "plain_text",
    						"emoji": True,
    						"text": "RSVP"
    					},
    					"style": "primary",
    					"value": f"rsvp_{event['id']}",
    					"action_id": "rsvp_button_click"
    				},
                    ]
                }])
            else:
                data["blocks"].extend([{
                    "type": "divider"
                },
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"*<{event['announcement_post']}|{event['title']}>*\n {event['start_time'].strftime('%B %d, %H:%M')} - {event['end_time'].strftime('%B %d, %H:%M')} UTC |  Convert to your timezone <{event['time50_link']}|here>."
                    }
                },
                {
                    "type": "actions",
                    "elements": [
                        {
    					"type": "button",
    					"text": {
    						"type": "plain_text",
    						"emoji": True,
    						"text": "un-RSVP (why though :shrug:?)"
    					},
    					"style": "danger",
    					"value": f"unrsvp_{event['id']}",
    					"action_id": "unrsvp_button_click"
    				},
                    ]
                }])
        say(data)

@app.action("rsvp_button_click")
def handle_rsvp_button(ack, body, client, respond):
    ack()
    event_id = body["actions"][0]["value"].split("_")[1]
    event = at.get_event_by_id(event_id)
    user = client.users_info(user=body["user"]["id"])

    # check if user is already registered
    if at.check_registration(event.slug, user["user"]["id"]):
        respond(f"You are already registered for *{event.title}*!")

    at.register_for_event(event.slug, user["user"]["real_name"], user["user"]["id"], user["user"]["profile"]["email"])
    respond(f"RSVP'd for *{event.title}*!")

@app.action("unrsvp_button_click")
def handle_unrsvp_button(ack, body, client, respond):
    ack()
    event_id = body["actions"][0]["value"].split("_")[1]
    event = at.get_event_by_id(event_id)
    user = client.users_info(user=body["user"]["id"])

    # check if user is already registered
    if not at.check_registration(event.slug, user["user"]["id"]):
        respond(f"You are not registered for *{event.title}*!")

    at.unregister_for_event(event.slug, user["user"]["id"])

    respond(f"Un-RSVP'd for *{event.title}*!")



# Clear DM with bot
@app.command("/clear_dm")
def clear_dm(ack, client, body, respond):
    ack()
    # Get the ID of the DM channel
    channel_id = body["channel_id"]

    # Get a list of all messages in the channel
    messages = client.conversations_history(channel=channel_id)["messages"]

    for message in messages:
        # Delete the message
        client.chat_delete(channel=channel_id, ts=message["ts"])

    respond("Deleted all messages in this DM!")

# Ready? Start your app!
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
