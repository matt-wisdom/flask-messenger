import requests
import json
import random
import shutil
import os
import functools

SEND_API_ENDPOINT = "https://graph.facebook.com/v11.0/me/messages"

class Message(object):
    """
        Message class to encapsulate a message.

        :param type: Type of message. Valid values are 'RESPONSE', 'UPDATE' and 'MESSAGE_TAG'.
        :param recipient: The recipient object which is a dictionary of one entry that can have any of 
            the following keys: id, user_ref, post_id, comment_id and the appropriate value.
        :param text: Text to be sent. Must not be set when either sender_action or notification_type are set.
        :param sender_action: Sender action. Valid values are 'typing_on', 'typing_off' and 'mark_seen'. Cannot
            be set with text and notification_type.
        :param notification_type: The notification_type. Valid values are 'REGULAR', 'SILENT_PUSH' and 'NO_PUSH'.
            Cannot be set with text and sender_action
    """
    _fields = {}
    def __init__(self, type, recipient, text="", sender_action="", notification_type=""):
        self._sender_action = False
        self._text = False
        self._attachment = None
        self._quick_replies = []
        if type not in ["RESPONSE", "UPDATE", "MESSAGE_TAG"]:
            raise Exception("type must be one of: RESPONSE, UPDATE, MESSAGE_TAG")
        if not isinstance(recipient, dict):
            raise Exception("recipient must be a dict with a single entry. The key can be any of: id, user_ref, post_id, comment_id")
        if list(recipient.keys())[0] not in ['id', 'user_ref', 'post_id', 'comment_id']:
            raise Exception("recipient dictionary's key must be any of: id, user_ref, post_id, comment_id")
        self._fields["recipient"] = recipient
        self._fields["messaging_type"] = type
        if sender_action:
            if sender_action not in ["typing_on", "typing_off", "mark_seen"]:
                raise Exception("sender_action must be any of: typing_on, typing_off, mark_seen")
            self._fields["sender_action"] = sender_action
            self._sender_action = True
        if notification_type:
            if notification_type not in ["REGULAR", "SILENT_PUSH", "NO_PUSH"]:
                raise Exception("notification_type must be any of: REGULAR, SILENT_PUSH, NO_PUSH")
            self._fields["notification_type"] = notification_type
        if text:
            self._fields["message"] = {}
            if self._sender_action:
                raise Exception("text and sender_action cannot be used together. Specify only one of them.")
            self._fields["message"]["text"] = text
            self._text = True

    def add_quick_reply(self, quick_reply_obj):
        """
            Add a quick reply to the message. May be called multiple times to add multiple quick replies.

            :param quick_replies: A :class:`flask_messenger.QuickReply` object.
        """
        self._quick_replies.append(quick_reply_obj)


    def set_attachment(self, attachment_obj):
        """
            Add an attachment to the message.

            :param attachment_obj: An attachment object to be sent. Attachment objects include all the classes
                defined in :mod:`flask_messenger.templates` or :class:`flask_messenger.Attachment`. Must not be set when sender_action or text is set.
        """
        if self._sender_action:
            raise Exception("attachment and sender_action cannot be used together. Specify only one of them.")
        if self._text:
            raise Exception("attachment and text cannot be used together. Specify only one of them.")
        self._fields["message"] = {}
        self._attachment = attachment_obj

    def get_dict(self):
        """
            :return: A dictionary of the message data.
        """
        if self._attachment:
            self._fields["message"]["attachment"] = self._attachment.get_dict()
        if not self._fields["message"]:
            raise ValueError("message cannot be empty")

        if self._quick_replies:
            self._fields["message"]["quick_replies"] = []
            for i in self._quick_replies:
                self._fields["message"]["quick_replies"].append(i.get_dict())

        return self._fields

        


class QuickReply(object):
    """ 
        Quick Reply class.

        :param type: The type of the quick reply. Valid values are 'text', 'location',
             'user_email' and 'user_phone_number'.
        :param title: Title of the quick reply. It must be set when `type` is 'text'.
        :param image_url: An image to be sent alongside a text quick reply.
        :payload: payload for text quick reply.
    """
    _fields = {}
    def __init__(self, type, title="", image_url="", payload=""):
        if type not in ["text", "location", "user_phone_number", "user_email"]:
            raise ValueError("QuickReply type is invalid. Must be any of: text, location, user_phone_number, user_email")
        self._fields["content_type"] = type
        if type == "text":
            if not title:
                raise Exception("title must be set when using text quick_reply")
            if not payload:
                raise Exception("payload must be set when using text quick_reply")
            self._fields["title"] = title
            if image_url:
                self._fields["image_url"] = image_url
            self._fields["payload"] = payload

    def get_dict(self):
        """
            :return: A dictionary of the quick reply data.
        """
        return self._fields

class Attachment(object):
    """
        Attachment class.

        :param attachment_dict: This is optional and is only used by the :class:`flask_messenger.events.RecievedMessage`
            to get the attachment object for a recieved message. The value is a dictionary of the
            attachment field in the recieved message data.
    """
    supportedtypes = ["image", "video", "audio", "file"]
    def __init__(self, attachment_dict={}):
        self._attachment_dict = attachment_dict
        self._is_location_data = False
        self._coordinates = None
        if attachment_dict:
            self._type = attachment_dict["type"]
            if self._type == "template":
                self.elements = attachment_dict["payload"]["product"]["elements"]
            else:
                self._is_location_data = True if self._type == "location" else False
                if self._is_location_data:
                    self._coordinates = attachment_dict["payload"]["coordinates"]
                self._url = attachment_dict["payload"]["url"]

    @property
    def url(self):
        """
            URL of the attachment.
        """
        return self._url

    @property
    def is_location_data(self):
        """
           True if the attachment is as a result of a user clicking a location quick reply.
        """
        return self._is_location_data
    
    @property
    def coordinates(self):
        """
            Co-ordinates (lat, long) if the attachment is as a result of a user clicking
            a location quick reply.
        """
        return self._coordinates
    
    @url.setter
    def url(self, url):
        self._url = url
    
    @property
    def type(self):
        return self._type

    @property
    def is_reusable(self):
        return self._is_reusable
    

    @type.setter
    def type(self, type):
        if type not in self.supportedtypes:
            raise Exception("type %s not supported"%type)
        self._type = type
    
    def get_dict(self):
        """
            :return: A dictionary of the attachment data.
        """
        out = {}
        if not out["type"]: raise ValueError("type not specified.")
        out["type"] = self._type
        out["payload"] = {"url": self._url}
        return out

    def download_attachment(self):
        download_file(self._url)

def send_message(recipient, access_token, text="", attachment=None, quick_replies=[], sender_action="", type="RESPONSE", notification_type=""):
    """
        Send a message using facebook's send api.

        :param recipient: The recipient object which is a dictionary of one entry that can have any of 
            the following keys: id, user_ref, post_id, comment_id and the appropriate value.
        :param access_token: The page's access token. Optional if access_token was set when instantiating
            :class:`flask_messenger.Messenger` class.
        :param text: The text to be sent as message. This is must not be set if `attachment` or `sender_action` is set.
        :param attachment: An attachment object to be sent. Attachment objects include all the classes defined in
            :mod:`flask_messenger.templates` or :class:`flask_messenger.message.Attachment`. Must not be set when sender_action or text is set.
        :param quick_replies: Takes a list of :class:`flask_messenger.message.QuickReply` objects to be sent with the message.
        :param sender_action: It can be any of "typing_on", "typing_off" or "mark_seen". Must not be set when attachment
            or text is set.
        :param type: The type of the message to be sent. Valid options are 'RESPONSE', 'UPDATE'and 'MESSAGE_TAG'.
        :param notification_type: Valid values are 'REGULAR', 'SILENT_PUSH', 'NO_PUSH'.

        :return: A dictionary of the response.
    """

    if sender_action and (text or attachment):
        raise Exception("text/attachment cannot be used with sender_action. Specify only one of them.")
    if text and attachment:
        raise Exception("text and attachment cannot be sent together. Specify one")

    message = Message(type, recipient, text, sender_action, notification_type)

    for quick_reply in quick_replies:
        message.add_quick_reply(quick_reply)

    if attachment:
        message.set_attachment(attachment)

    message_data = message.get_dict()
    resp = requests.post(SEND_API_ENDPOINT, params={'access_token': access_token},
        data=json.dumps(message_data), headers={'Content-Type':'application/json'})
    return resp.json()

def download_file(url, dir_="."):
    """
        Download a file from a given url into dir.

        :param url: url to download the file from.
        :param dir_: optional.The directory to download the file into.
            Defaults to the current directory.
    """
    fname_full = url.split("/")[-1]
    fname, ext =  os.path.splitext(fname_full)
    if os.path.exists(fname_full):
        fname += str(random.randrange(0, 9999999999999))
    fname_full = os.path.join(dir_, fname+ext)

    with requests.get(url, stream=True) as r:
        with open(fname_full, "wb") as f:
            r.raw.read = functools.partial(r.raw.read, decode_content=True)
            shutil.copyfileobj(r.raw, f)
    return fname_full
