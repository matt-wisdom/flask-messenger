# -*- coding: utf-8 -*-
import json
from functools import wraps, partial
from flask import current_app, _app_ctx_stack, request, abort
from .events import RecievedMessage, PostBack, MessageDeliveries, Reaction, MessageReads
from .message import Message, send_message

EVENTS_OBJECT_MAP = {'messages':RecievedMessage, 'messaging_postback':PostBack, 
    'message_deliveries': MessageDeliveries, 'message_reactions':Reaction, 'message_reads':MessageReads}

EVENTS_FIELD = {"messages": ["message", "messaging"], "messaging_postback":"postback",
     "message_deliveries":"delivery", "message_reads":"read", 'message_reactions': 'reaction'}

class Messenger(object):
    """
        Messenger api class.
        Example Usage::  
            app = Flask(__name__)
            messenger = Messenger(app, webhook_token={'/webhook': 'VERIFY_TOKEN'}, 
                access_token='whatever-it-is')

            @messenger.on("messages")
            def handle_text(msg_obj):
                if msg_obj.text == 'hello':
                    messenger.reply_to(msg_obj, text="Hi, how may i help you?")

            if __name__ == "__main__":
                app.run()

        :param app: The flask application instance. If the application instance
                is unknown when instantiating this class, then call
                ``messenger.init_app(app)`` when the application instance is
                available.
        :param webhook_token: A dictionary of webhook endpoints, verify token pair. The endpoint
                must be a valid flask endpoint string. i.e It must start with as '/'. The verify token
                is a string of the verify token you set in your facebook developer dashbord.
        :param access_token: Optional. This is your api access token which is used when sending messages.

        .. note:: All method parameter types are strings unless stated otherwise.

    """

    # Event registers for each webhook endpoint, 
    #the keys must be valid endpoints and the values are dicts of event keys and handlers_list values
    # Events for a webhook can have multiple handlers.
    _event_register = {} #{webhook:{event: []}}

    # All webhook endpoints
    _webhooks = []


    _events = list(EVENTS_FIELD.keys())

    def __init__(self, app=None, webhook_token={}, access_token=''):
        self.app = app
        self._access_token = access_token
        self.endpoints_verify_tokens = webhook_token
        self._webhooks = list(webhook_token.keys())

        if app is not None:
            self.init_app(app)

    def init_app(self, app):
        """
            Initialize this extension.
        """
        with app.app_context():
            self.logger = current_app.logger
        if not self.endpoints_verify_tokens:
            self.logger.critical("Verify tokens and webhooks not specified.")
            raise ValueError("Verify token(s) and webhooks must be specified.")
        self._set_up_webhooks_with_verification(app)



    def add_webhook(self, endpoint, token):
        """
            Add or override existing webhook anytime.

            :param endpoint: A valid endpoint string.
            :param token: The verify token for the endpoint.

        """
        self.endpoints_verify_tokens[endpoint] = token
        self._webhooks.append(endpoint)
        self._set_up_webhooks_with_verification(current_app, endpoint)

    def _set_up_webhooks_with_verification(self, app, endpoint=""):
        def webhook_base_handler(endpoint):
            # Base handler for all requests, handles verification and calls the handler set by user.
            if request.method == "GET":

                verify_token = self.endpoints_verify_tokens.get(endpoint)
                if not verify_token:
                    self.logger.critical("Verify token cannot be None.")
                    raise ValueError("Verify token cannot be None")

                # flask port of the code from messenger api docs
                mode = request.args.get("hub.mode")
                token = request.args.get("hub.verify_token")
                challenge = request.args.get("hub.challenge")
                if mode and token:
                    self.logger.debug("Recieved verification challenge")
                    if mode == 'subscribe' and token == verify_token:
                        self.logger.debug("Verification successful.")
                        return challenge
                    else:
                        self.logger.error("Verification unsuccessful.")
                        abort(403)
            return self.events_dispatcher(endpoint, request)

        if endpoint:
            self._webhooks.append(endpoint)
            view_func = partial(webhook_base_handler, endpoint)
            view_func.__name__ = "view_func_" + str(self._webhooks.index(endpoint))
            self._event_register[endpoint] = {}
            app.add_url_rule(endpoint, view_func=view_func, methods=["GET", "POST"])
        else:
            for endpoint in self._webhooks:
                view_func = partial(webhook_base_handler, endpoint)
                self._event_register[endpoint] = {}
                view_func.__name__ = "view_func_" + str(self._webhooks.index(endpoint))
                app.add_url_rule(endpoint, view_func=view_func, methods=["GET", "POST"])
        self.logger.debug("webhook endpoints set.")

    def events_dispatcher(self, endpoint, request):
        """
            Method to get the event type of a webhook event and
            call the event handler with the appropriate event
            object.

            :param endpoint: The endpoint for which the event was sent.
            :param request: The flask request object for that event.
        """
        callback_parser = ParseEvents(request.get_json())
        event, data, event_obj = callback_parser.parse()
        self.logger.debug("Recieved event: %s"%event)
        if event in self._events:
            handlers = self._event_register[endpoint].get(event)
            if handlers:
                for handler in self._event_register[endpoint].get(event):
                    handler(event_obj)
        return ""

    def on(self, event, webhook="all"):
        """
            Decorator to register event handler.  
            Usage::
                @on(event, webhook)
                def handler(event_obj):
                    pass

            :param event: The event to set an handler for. It must be one of messages, 
                    messaging_postback, message_deliveries, message_reads or message_reactions.
            :param webhook: The webhook endpoint to register the event handler for.
                    webhook can be a single webhook endpoint, list of webhooks endpoint or the string
                    'all' to set the handler for all webhooks endpoint.

        """
        def _on(handler):
            
            if webhook == "all":
                for i in self._webhooks:
                    if not self._event_register[i].get(event):
                        self._event_register[i][event] = []
                    self.logger.debug("Registering event %s for webhook %s"%(event, i))
                    self._event_register[i][event].append(handler)
            else:
                if isinstance(webhook, (list, tuple)):
                    for i in webhook:
                        if not isinstance(i, str):
                            self.logger.error("webhook not a string or list/tuple of strings")
                            raise ValueError("webhook must either be a string or list/tuple of strings")
                        if not self._event_register[i].get(event):
                            self._event_register[i][event] = []
                        self.logger.debug("Registering event %s for webhook %s"%(event, i))
                        self._event_register[i][event].append(handler)
                elif isinstance(webhook, str):
                    if not self._event_register[webhook].get(event):
                        self._event_register[webhook][event] = []
                    self.logger.debug("Registering event %s for webhook %s"%(event, webhook))
                    self._event_register[webhook][event].append(handler)
                else:
                    self.logger.error("webhook not a string or list/tuple of strings")
                    raise ValueError("webhook must either be a string or list/tuple of strings")
            return handler
        return _on

    def reply_to(self, msg_obj, **kwargs):
        """
            Reply to a message.

            :param msg_obj: The message event object whose sender is to be sent a reply.
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
        return self.send_message(msg_obj.sender, **kwargs)

    def send_message(self, recipient, access_token=None, text="", attachment=None, quick_replies=[],
         sender_action="", type="RESPONSE", notification_type=""):
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
        if not access_token:
            if not self._access_token:
                self.logger.error("access_token not specified.")
                raise ValueError("access_token not specified.")
            access_token = self._access_token
        resp = send_message(recipient, access_token, text, attachment, quick_replies, sender_action, type, notification_type)
        self.logger.debug("message sent")
        return resp.json()

class ParseEvents(object):
    """
        Class to parse event data and determine the appropriate event type.

        :param request_dict: A dictionary of the data sent by messenger.
    """
    def __init__(self, request_dict):
        self.request_dict = request_dict 

    def _extract_event(self):
        # Parses only page objects
        if self.request_dict.get('object') != 'page':
            return None
        entry = self.request_dict['entry'][0]["messaging"][0]
        print(entry)
        self.entry = entry
        for i in EVENTS_FIELD:
            if isinstance(EVENTS_FIELD[i], list):
                for j in EVENTS_FIELD[i]:
                    if entry.get(j):
                        print(i)
                        return i
                continue
            if entry.get(EVENTS_FIELD[i]):
                print(i)
                return i

    def parse(self):
        """
            Parse the data.

            :return: This method returns a 3-tuple with the first element being
                the event type, the second element being the raw entry and the last
                is the appropriate event object.
        """
        # Extract events and event object
        ev = self._extract_event()
        event_obj = EVENTS_OBJECT_MAP[ev](self.entry)
        return self._extract_event(), self.entry, event_obj

