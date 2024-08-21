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
def events(ack, body, say):
    ack()
    events = at.get_past_events()
    if len(events) == 0:
        say("No upcoming events!")
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

        say(data)

@app.action("rsvp_button_click")
def handle_some_action(ack, body, client, say):
    ack()
    event_id = body["actions"][0]["value"].split("_")[1]
    event = at.get_event_by_id(event_id)
    user = client.users_info(user=body["user"]["id"])
    at.register_for_event(event.slug, user["user"]["real_name"], user["user"]["id"], user["user"]["profile"]["email"])

    say(f"RSVP'd for *{event.title}*!")

# Ready? Start your app!
if __name__ == "__main__":
    SocketModeHandler(app, os.environ.get("SLACK_APP_TOKEN")).start()
