import jinja2
from flask import g, Blueprint, render_template, jsonify, request, redirect, url_for
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from .twilio import twilio
from .blob import blob
import dateutil.parser
import json
import datetime
import urllib
import re

bp = Blueprint("main", __name__)


tracks = {
    "happy_thanksgiving": {
        "name": "Happy Thanksgiving - don't fight!",
        "desc": "Get mad at robo-telemarketers instead of each other",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Happy%20Thanksgiving%20-%20don_t%20fight.mp3"
    },
    "national_anthem": {
        "name": "National Anthem",
        "desc": "It's the National Anthem!",
        "url": "https://nobias.blob.core.windows.net/telemarketer/The%20National%20Anthem.mp3"
    },
    "guided_meditation": {
        "name": "Guided Meditation",
        "desc": "Find your cave, where no one fights about politics",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Guided%20Meditation.mp3"
    },
    # "smooth_jazz": {
    #     "name": "Smooth Jazz Holding Tone",
    #     "desc": "Please hold while your dinner is saved",
    #     "url": "https://nobias.blob.core.windows.net/telemarketer/Smooth%20Jazz%20Holding%20Tone.mp3"
    # },
    "ambient": {
        "name": "Ambient",
        "desc": "Shhhhhhh",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Ambient.mp3"
    },
    "polite_agreement": {
        "name": "Polite agreement with your political opinions",
        "desc": "Wow, so insightful!",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Polite%20agreement.mp3"
    },
    "didgeridoo": {
        "name": "Didgeridoo",
        "desc": "Bbrrrrrrrbbbbbbrrrrgiioingingongbrrrr",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Didgeridu.mp3"
    },
}

history = {}


def __from_iso_format(string):
    return dateutil.parser.parse(string)


def __check_call_limit(number, track):
    """
    returns whether or not we're allowed to make the call based call limitations:
      - if the number has been called within the past 5 minutes
      - if the number has been called move then 5 times in the past 24 hours
    """
    now = datetime.datetime.now()

    # if number not in dic
    call_history = history.get(number, [])

    # check if number has been called in the past 5 minutes
    margin = datetime.timedelta(minutes=1)
    for i, call_el in reversed(list(enumerate(call_history))):
        call_time, success, _ = call_el
        call_time = __from_iso_format(call_time)

        # if call number is curr number and was made less than 5 mins ago
        if success:
          if call_time >= now - margin: 
              call_history.append((now.isoformat(), False, track))
              return False, "This number was dialed within the past 5 minutes. Please wait."

        # if call was made more than 5 mins ago
        if call_time <= now - margin: 
            break

    # check if number has been called more than 10 times in the past 24 hours
    margin = datetime.timedelta(days=1)
    day_cap = 10
    day_counter = 0
    for i, call_el in reversed(list(enumerate(call_history))):
        call_time, success, _ = call_el
        call_time = __from_iso_format(call_time)

        if success:
          if call_time >= now - margin:
              day_counter += 1    

          if day_counter >= day_cap:
              call_history.append((now.isoformat(), False, track))
              return False, "This number has been dialed too frequently within the past day. Please try tomorrow."

    # add new time to call history for the number and update history dict
    call_history.append((now.isoformat(), True, track))
    history[number] = call_history

    return True, "Your phone call is being made."


def __standardize_phone_number(number):
    num = re.findall("[0-9]", number)[-10:]
    standardized_number = "".join(num)
    return standardized_number


@bp.route("/")
def index():
    return render_template("index.html", tracks=tracks)


@bp.route("/about")
def about():
    return render_template("about.html")


@bp.route("/dial", methods=["POST"])
def dial_number():
    """
    A route to kick off a phone call.
    """

    # Grab the relevant phone numbers.
    number = request.form.get("phone")
    track = request.form.get("track")

    standardized_number = __standardize_phone_number(number)
    allowed, msg = __check_call_limit(standardized_number, track)

    # serialize history to file
    with open(blob.get_file_name(), 'w') as outfile:  
          json.dump(history, outfile)

    if allowed:
        # Create a phone call that uses our other route to play a song from Spotify.
        call_url = "{}call?track={}".format(request.url_root, track)
        twilio.client.api.account.calls.create(
            to=standardized_number,
            from_="+18572715456",  # twilio number
            url=call_url
        )
        return jsonify(success=True, message=msg)

    else:
        # call limitation reached
        return jsonify(success=False, message=msg)


@bp.route("/call", methods=["POST", "GET"])
def outbound_call():
    """
    A route to handle the logic for phone calls.
    """

    track = request.args.get("track")
    track_url = tracks[track]["url"]

    response = VoiceResponse()
    response.say(message="A friend or family member wanted to send you this message.")
    response.play(track_url)
    return str(response)


@bp.route("/call_response", methods=["POST", "GET"])
def call_response():
    """
    the response if someone calls the twilio number
    """
    response = VoiceResponse()
    response.say(message="Thanks for calling. Visit us at Telemarketers save Thanksgiving dot com.")
    return str(response)


@bp.route("/sms_response", methods=["POST", "GET"])
def sms_response():
    """
    the response if someone sms's the twilio number
    """
    response = MessagingResponse()
    response.message("Thanks for texting! Visit www.telemarketerssavethanksgiving.com :)")
    return str(response)


@bp.route("/update_history")
def update_history():
    """
    upload `history.txt` to blob
    """
    block_blob_service = blob.get_client()
    date = datetime.date.today().strftime("%d-%m-%y")
    block_blob_service.create_blob_from_path(
        container_name=blob.get_container_name(), 
        blob_name="{}/{}".format(date, blob.get_file_name()),
        file_path=blob.get_file_name()
    )
    return "ok"

