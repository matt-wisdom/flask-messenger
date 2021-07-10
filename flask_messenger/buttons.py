class Button(object):
    """
        Base button class
    """
    def get_dict(self):
        """
            :return: A dictionary of the button data.
        """
        return self._fields

class URLButton(Button):
    """
        Url buttons.

        :param url:  url to send users to on click.
        :param title: Optional. Title of the button.
    """
    _fields = {"type": "url"}
    def __init__(self, url, title=""):
        self._fields['url'] = url
        if title:
            self._fields['title'] = title
    
    def add_optionals(self, whr="", me="", fu="", wsb="", **kwargs):
        """
            Add some optional fields.

            :param whr: Optional. The webview_height_ratio.
            :param me: Optional. messenger_extensions.
            :param fu: Optional. fallback_url.
            :param wsb: Optional. webview_share_button.

        """
        whr = whr or kwargs.get["whr"]
        if whr:
            self._fields["webview_height_ratio"] = whr
        me = me or kwargs.get("me")
        if me:
            self._fields["messenger_extensions"] = me
            fu = fu or kwargs.get("fu")
            if fu:
                self._fields["fallback_url"] = fu
        wsb = wsb or kwargs.get("wsb")
        if wsb:
            self._fields["webview_share_button"] = wsb

class CallButton(Button):
    """
        Call button class.

        :param title: Title of button.
        :param payload: payload (phone number) for the button.
    """
    _fields = {"type": "phone_number"}
    def __init__(self, title, payload):
        self._fields['title'] = title
        self._fields['payload'] = payload

class PostBackButton(Button):    
    """
        Postback button class.

        :param title: Title of the button.
        :param payload: Payload to be sent to webhook on click.
    """
    _fields = {"type": "postback"}
    def __init__(self, title, payload):
        self._fields['title'] = title
        self._fields['payload'] = payload

class LogInButton(Button):
    """
        Login button class.

        :param url: login url.
    """
    _fields = {"type": "account_link"}
    def __init__(self, url):
         self._fields['url'] = url

class LogOutButton(Button):
    _fields = {"type": "account_unlink"}
