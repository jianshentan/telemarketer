import jinja2
from flask import g, Blueprint, render_template, jsonify, request, redirect, url_for
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse, Message
from twilio.twiml.voice_response import VoiceResponse
from twilio.rest import Client
from .twilio import twilio
import urllib

bp = Blueprint("main", __name__)


tracks = {
    "national_anthem": {
        "name": "National Anthem",
        "desc": "This is the National Anthem",
        "url": "https://nobias.blob.core.windows.net/telemarketer/National%20Anthem.mp3"
    },
    "ambient": {
        "name": "Ambient",
        "desc": "Shhhhhhh",
        "url": "https://nobias.blob.core.windows.net/telemarketer/Ambient.mp3"
    }
}


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

    # Create a phone call that uses our other route to play a song from Spotify.
    twilio.client.api.account.calls.create(
        to=number,
        from_="+18572715456",  # twilio number
        url="http://86b0c44d.ngrok.io/call?track={}".format(track),
    )

    return jsonify(success=True, message="Your phone call is being made.")


@bp.route("/call", methods=["POST"])
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
