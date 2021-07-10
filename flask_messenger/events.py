from .message import Attachment

class BaseEvent(object):
    """
        Contains a couple of methods to be inherited
        by event classes.
    """
    def __init__(self, data):
        self._data = data

    @property
    def sender(self):
        return self._data["sender"]

    @property
    def recipient_id(self):
        return self._data["recipient"]["id"]

    @property
    def timestamp(self):
        return self._data.get("timestamp")

class RecievedMessage(BaseEvent):
    """
        Event class for a message event.

        :param data: The data from messenger.
    """
    def __init__(self, data):
        if data.get("messaging"):
            self._data = data.get("messaging")[0]
        else:
            self._data = data
        self._attachments = []

    @property
    def text(self):
        return self._data["message"].get("text")
    
    @property
    def mid(self):
        return self._data["message"]["mid"]

    @property
    def is_quick_reply():
        return True if self._data["message"].get("quick_reply") else False  

    @property
    def is_reply(self):
        return True if self._data["message"].get("reply_to") else False

    @property
    def has_attachment(self):
        return True if self._data["message"].get("attachments") else False

    @property
    def is_referral(self):
        return True if self._data["message"].get("referral") else False

    @property
    def quick_reply_payload(self):
        if not self.is_quick_reply:
            return None
        return self._data["message"]["quick_reply"]["payload"]

    @property
    def reply_to(self):
        if not self.is_reply:
            return None
        return self._data["message"]["reply_to"]["mid"]

    @property
    def referral_id(self):
        if not self.is_referral:
            return None
        return self._data["message"]["referral"]["product"]["id"]
    
    @property
    def attachments(self):
        """
            Returns a list of :class:`flask_messenger.message.Attachment` objects.
        """
        if not self.has_attachment:
            return None
        if not self._attachments:
            for i in self._data["message"]["attachments"]:
                self._attachments.append(Attachment(i))
        return self._attachments

class Reaction(BaseEvent):
    """
        Event class for reaction event.
    """
    @property
    def reaction(self):
        return self._data["reaction"]["reaction"]

    @property
    def action(self):
        return self._data["reaction"]["action"]

    @property
    def emoji(self):
        """
            Returns the emoji's unicode value.
        """
        return self._data["reaction"]["emoji"]

    @property
    def mid(self):
        return self._data["reaction"]["mid"]

class PostBack(BaseEvent):
    """
        Event class for postbacks
    """
    @property
    def mid(self):
        return self._data["postback"]["mid"]   

    @property
    def title(self):
        return self._data["postback"]["title"]

    @property
    def payload(self):
        return self._data["postback"]["payload"]

    @property
    def referral(self):
        ref = self._data["postback"].get("referral")
        return ref if ref else None

class MessageReads(BaseEvent):
    """
        Event class for message_reads
    """
    @property
    def watermark(self):
        return self._data["read"]["watermark"]

class MessageDeliveries(BaseEvent):
    """
        Event class for message_deliveries
    """
    @property
    def mids(self):
        return self._data["delivery"]["mids"]

    @property
    def watermark(self):
        return self._data["delivery"]["watermark"]
    


