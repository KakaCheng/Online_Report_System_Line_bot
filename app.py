from controller.line_bot_controller import line_bot_event_controller
#ngrok
from flask import Flask, request, abort
#line bot
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import ImageMessage, TextMessage, LocationMessage
from linebot.models import TextSendMessage
from linebot.models import MessageEvent, FollowEvent
from google.cloud.logging.handlers import CloudLoggingHandler
from error_map import *

import google.cloud.logging
import logging
import os

app = Flask(__name__)
#註冊機器人
line_bot_api = LineBotApi("T1N/eGyrqMKT0Z4LVI2Y/I39GeEH2yjiVh5djSgebQz5l6SDHzqpRfmiv/MdaJ6UfiwIWRqakL6vGEU8dxGJqgt5WgUn2u5u2NcK7N6r/c9G/9I/3mHRfS2FBuJ3aIM7qOPlCaM9r226t+tqo/IdAQdB04t89/1O/w1cDnyilFU=")
handler = WebhookHandler("490dce7f975d80d26b2c8c73b14d920f")

# 建立line event log，用來記錄line event
client = google.cloud.logging.Client()
bot_event_handler = CloudLoggingHandler(client,name = "Line_BOT_Tibame_logging")
bot_event_logger = logging.getLogger("Line_BOT_Tibame_logging")
bot_event_logger.setLevel(logging.INFO)
bot_event_logger.addHandler(bot_event_handler)

@app.route("/", methods = ['POST'])
def callback():
    signature = request.headers["X-Line-Signature"]
    body = request.get_data(as_text = True)
    
    bot_event_logger.info(body)
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
        return app_err.HANDLER_FAIL
    
    return "SUCCESS"

@handler.add(FollowEvent)
def handle_follow_event(event):
    ret = app_err.SUCCESS

    ret = line_bot_event_controller.handle_rich_menu(line_bot_api, event)
    if ret != line_bot_event_controller_err.SUCCESS:
        return "CONTROLLER_FAIL"

    return "SUCCESS"

@handler.add(MessageEvent, message = ImageMessage)
def handle_image_message(event):
    ret = app_err.SUCCESS

    ret = line_bot_event_controller.handle_image_message(line_bot_api, event)
    if ret != line_bot_event_controller_err.SUCCESS:
        return "CONTROLLER_FAIL"

    return "SUCCESS"
    
@handler.add(MessageEvent, message = TextMessage)
def handle_message(event):
    ret = app_err.SUCCESS

    ret = line_bot_event_controller.handle_message_reply(line_bot_api, event)
    if ret != line_bot_event_controller_err.SUCCESS:
        return "CONTROLLER_FAIL"

    return "SUCCESS"

@handler.add(MessageEvent, message = LocationMessage)
def handle_location_message(event):
    ret = app_err.SUCCESS

    ret = line_bot_event_controller.handle_location_message_reply(line_bot_api, event)
    if ret != line_bot_event_controller_err.SUCCESS:
        return "CONTROLLER_FAIL"

    return "SUCCESS"

if __name__ == "__main__":
    app.run(host = "0.0.0.0", port = int(os.environ.get("PORT", 8080)))
