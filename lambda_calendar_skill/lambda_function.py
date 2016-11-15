from __future__ import print_function

import boto3
from datetime import datetime, timedelta
from boto3.dynamodb.conditions import Attr

APP_ID = ""
DYNAMODB_TABLE_NAME = "calendar_event"
CALENDAR_NAME = "my"
AUDIO_BUCKET_URL = "https://s3.amazonaws.com/my-calendar-audio/{}.mp3"


def event_information_response(title, event_date, event_hour, event_id, session_attributes={}):

    event_dt = datetime.strptime("{} {}".format(event_date, event_hour), "%Y-%m-%d %H") + timedelta(hours=9)
    print(event_dt)

    event_day = event_dt.strftime('%d')
    event_hour = int(event_dt.strftime('%I'))
    ampm = event_dt.strftime('%p')

    ssml_doc = '<speak>{} {} at <say-as interpret-as="date">????{}{}</say-as><audio src="{}" /></speak>'.format(
        event_hour,
        ampm,
        event_dt.strftime('%m'),
        event_day,
        AUDIO_BUCKET_URL.format(event_id)
    )
    print(ssml_doc)

    formated_dt = "{} {} at {} {} ".format(
        event_hour,
        ampm,
        event_dt.strftime('%B'),
        int(event_day)
        )
    print(formated_dt)

    speechlet = {
        'outputSpeech': {
            'type': 'SSML',
            'ssml': ssml_doc
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': formated_dt
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'SSML',
                'ssml': ssml_doc
            }
        },
        'shouldEndSession': (len(session_attributes) == 0)
    }

    return build_response(session_attributes, speechlet)

def ask_event_response(event_count, event_date):
    ask_text = "There are {} events. Give me an event number to hear information.".format(event_count)
    speechlet = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': ask_text
        },
        'card': {
            'type': 'Simple',
            'title': "few event found",
            'content': ask_text
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': ask_text
            }
        },
        'shouldEndSession': False
    }

    return build_response(
        create_session_attribute(event_date),
        speechlet
    )

def no_event_response():
    speechlet = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': "event not found"
        },
        'card': {
            'type': 'Simple',
            'title': "event not found",
            'content': ""
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': "event not found"
            }
        },
        'shouldEndSession': True
    }

    return build_response({}, speechlet)

def usage_response():
    speechlet = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': "Give me a date to find events on {} calendar".format(CALENDAR_NAME)
        },
        'card': {
            'type': 'Simple',
            'title': "event not found",
            'content': "Give me a date to find events on {} calendar.".format(CALENDAR_NAME)
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': "Give me a date to find events on {} calendar".format(CALENDAR_NAME)
            }
        },
        'shouldEndSession': True
    }

    return build_response({}, speechlet)

def session_end_request():
    title = "see you"
    good_by_text = "If you are interested to {}, just ask me.".format(CALENDAR_NAME)
    speechlet = {
        'outputSpeech': {
            'type': 'PlainText',
            'text': good_by_text
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': good_by_text
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': good_by_text
            }
        },
        'shouldEndSession': True
    }

    return build_response({}, speechlet)

def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }

def search_event(event_date):
    dynamodb = boto3.resource("dynamodb")
    table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    response = table.scan(
        FilterExpression=Attr("begin_date").eq(event_date)
    )
    return response['Items']

def search_by_date(event_date, session):
    items = search_event(event_date)
    event_count = len(items)

    if event_count <= 0:
        return no_event_response()

    if event_count == 1:
        return event_information_response(
            items[0]['summary'],
            items[0]['begin_date'],
            items[0]['begin_hour'],
            items[0]['uid']
        )
    if event_count > 1:
        if session["new"]:
            return ask_event_response(event_count, event_date)

    return usage_response()

def search_by_number(event_number, session):
    event_date = get_session_attribute(session)
    print("event date:{}".format(event_date))
    if event_date == None:
        return usage_response()

    items = search_event(event_date)
    event_count = len(items)
    print("event event_count:{}".format(event_count))
    if event_count <= 0:
        return no_event_response()


    print("event event_number:{}".format(event_number))
    if event_count >= event_number:
        event_index = event_number - 1
        return event_information_response(
            items[event_index]['summary'],
            items[event_index]['begin_date'],
            items[event_index]['begin_hour'],
            items[event_index]['uid'],
            create_session_attribute(event_date)
        )

    return no_event_response()


def create_session_attribute(event_date):
    return {"eventDate": event_date}

def get_session_attribute(session):
    attributes = session.get('attributes', {})
    if "eventDate" not in attributes:
        return None
    return attributes["eventDate"]

# --------------- Main handler ------------------

def lambda_handler(event, context):
    print(event)

    if (event['session']['application']['applicationId'] != APP_ID):
        raise ValueError("Invalid Application ID")

    if event['request']['type'] == "IntentRequest":
        intent_name = event['request']['intent']['name']
        if intent_name == "searchIntent":
            return search_by_date(event['request']['intent']['slots']['date']['value'], event['session'])
        elif intent_name == "eventIntent":
            return search_by_number(int(event['request']['intent']['slots']['number']['value']), event['session'])
        elif intent_name == "AMAZON.HelpIntent":
            return usage_response()
        elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
            return session_end_request()

    raise ValueError("un supported request")
