class GenericTemplate(object):
    """ 
        Class to represent a generic template.

        .. note:: All method parameter types are strings unless stated otherwise.

        :param title:  The title of the template.
        :param image_url: Optional. URL of image to be included in the template.
        :param subtitle: Optional. Subtitle
    """
    _fields = {"payload":{ "template_type":"generic"}, "type":"template"}
    def __init__(self, title, image_url="", subtitle=""):
        self._fields["payload"]['title'] = title
        if image_url:
            self._fields["payload"]["image_url"] = image_url
        if subtitle:
            self._fields["payload"]["subtitle"] = subtitle
        self.buttons = []
        self.default_action = None

    def set_default_action(self, url):
        """
            Set a default action for the template. The default action is a
            url button whose url is opened when the button is clicked if no
            other button is present.

            :param url: URL for the default action button.
        """
        self.default_action = URLButton(url)

    def add_buttons(self, button_list):
        """
            Add buttons.

            :param button_list: A list of button objects from :mod:`flask_messenger.buttons`.
        """
        # button_list is a list of button object
        if not isinstance(button_list, (list, tuple)):
            raise TypeError("button_list must be a list of button objects")
        self.buttons.extend(button_list)

    def get_dict(self):
        """
            :return: A dictionary of the template data.
        """
        if self.default_action:
            self._fields["payload"]['default_action'] = self.default_action.get_dict()
        if self.buttons:
            self._fields["payload"]['buttons'] = []
            for i in self.buttons:
                self._fields["payload"]['buttons'].append(i.get_dict())
        return self._fields
        
class ButtonTemplate(object):
    _fields = {"payload":{"template_type":"button"}, "type":"template"}

    def __init__(self, text, buttons=[]):
        """
            Button template class.

            :param text: Button text.
            :params buttons: Optional. A list of button objects from :mod:`flask_messenger.buttons`.
                Must contain a maximum of 3 buttons
        """
        self._fields["payload"]['text'] = text
        self.buttons = buttons
        if len(self.buttons)  > 2:
            raise Exception("Buttons in a button template cannot be more than 3")

    def add_buttons(self, button_list):
        """
            Add buttons.

            :param button_list: A list of button objects from :mod:`flask_messenger.buttons`.
        """
        if len(self.buttons)  > 2:
            raise Exception("Buttons in a button template cannot be more than 3")
        self.buttons.extend(button_list)

    def get_dict(self):
        """
            :return: A dictionary of the template data.
        """
        if len(self.buttons) < 1:
            raise Exception("There must be at least one button in a button template.")
        self._fields["payload"]['buttons'] = []
        for i in self.buttons:
            self._fields["payload"]['buttons'].append(i.get_dict())
        return self._fields

class RecieptTemplate(object):
    """
        Reciept Template class.

        :param recipient_name: The name of the recipient.
        :param order_number: Order number.
        :param payment_method: The method of payment.
        :param timestamp: Optional. timestamp for when payment was made.
        :param currency: Optional. Currency code. Defaults to 'USD'.
        :param merchant_name: Optional. Merchant's name.
        :param order_url: Optional. Order URL.
    """
    _fields = {"payload":{"template_type":"reciept"}, "type":"template"}

    def __init__(self, recipient_name, order_number, payment_method,
        timestamp=None,  currency="USD", merchant_name=None, order_url=""):

        self._fields["payload"]["recipient_name"] = recipient_name
        self._fields["payload"]["order_number"] = order_number
        self._fields["payload"]["payment_method"] = payment_method
        self._fields["payload"]["currency"] = currency
        if timestamp:
            self._fields["payload"]["timestamp"] = timestamp
        if merchant_name:
            self._fields["payload"]["merchant_name"] = merchant_name
        if order_url:
            self._fields["payload"]["order_url"] = order_url

        self.address = {}
        self.summary = {}
        self.adjustments = []
        self.elements = []

    def set_address(self, street_1, city, postal_code, state, country, street_2=""):
        """
            Add an address to the reciept. Address may not be set before sending template.

            :param street_1: Street name.
            :param city: City name.
            :param postal_code: Postal Code.
            :param state: State.
            :param country: Country.
            :param street_2: Optional. second street name.

        """
        self.address["street_1"] = street_1
        self.address["street_2"] = street_2
        self.address["city"] = city
        self.address["postal_code"] = postal_code
        self.address["state"] = state
        self.address["country"] = country

    def set_summary(self, total_cost, subtotal=0, shipping_cost=0, total_tax=0):
        """
            Set the reciept's summary. This must be set before sending the template.

            :param total_cost: The total cost of the purchase.
            :type: float.
            :param subtotal: Optional.
            :type: float.
            :param shipping_cost: Optional.
            :type: float.
            :param total_tax: Optional.
            :type: float.
        """

        #Catch invalid values.
        float(total_cost)
        float(subtotal)
        float(shipping_cost)
        float(total_tax)
        self.summary["total_cost"] = total_cost
        if subtotal:
            self.summary["subtotal"] = subtotal
        if shipping_cost:
            self.summary["shipping_cost"] = shipping_cost
        if total_tax:
            self.summary["total_tax"] = total_tax

    def add_adjustment(self, name, amount):
        """
            Add adjustments. Optional.
        """
        float(amount)
        self.adjustments.append({"name":name, "amount":amount})

    def add_element(self, title, price ,subtitle="", quantity=0, currency="", image_url=""):
        """
            Add an element to the template.

            :param title: Title of element.
            :param price: Price of element.
            :param subtitle: Optional. Subtitle.
            :param quantity: Optional. Quantity of element.
            :param currency: Optional. Currency code.
            :param image_url: Optional. Image.
        """
        el = {}
        el['title'] = title
        el['price'] = price
        if subtitle:
            el["subtitle"] = subtitle
        if quantity:
            el["quantity"] = quantity
        if currency:
            el["currency"] = currency
        if image_url:
            el["image_url"] = image_url
        self.elements.append(el)

    def get_dict(self):
        """
            :return: A dictionary of the template data.
        """
        if self.address:
            self._fields["payload"]['address'] = self.address
        if not self.summary:
            raise Exception("A summary must be provided when using reciept template. Use the `set_summary` method to set the summary")
        self._fields["payload"]['summary'] = self.summary
        if self.adjustments:
            self._fields["payload"]['adjustments'] = self.adjustments
        if self.elements:
            self._fields["payload"]['elements'] = self.elements
        return self._fields

class MediaTemplate(object):
    """
        Media template class.

        :param media_type: Optional. Type of media to be sent in template. valid values are 'image' or 'video'.
            Defaults to 'image'.
        :param attachment_id: The id of a previously saved attachment. Cannot be set when url is set.
        :param url: The url of the media to be sent with the template. Cannot be set when url is set.
    """
    _fields = {"payload":{"template_type":"media", "elements":[{"media_type": ""}]}, "type":"template"}
    def __init__(self, media_type="image", attachment_id="", url=""):
        if not attachment_id and not url:
            raise ValueError("One of either attachment_id or url must be specified. If both are specified, attachment_id will be used.")

        if media_type not in ["image", "video"]:
            raise ValueError("Media type must be either image or video")

        self._fields["payload"]["elements"][0]["media_type"] = media_type
        if attachment_id:

            self._fields["payload"]["elements"][0]["attachment_id"] = attachment_id
        else:
            self._fields["payload"]["elements"][0]["url"] = url

        self._button = None

    def add_button(self, button):
        """ 
            Add a button to the template.

            :param button: A button object from :mod:`flask_messenger.buttons`.
        """
        self._button = button

    def get_dict(self):
        """
            :return: A dictionary of the template data.
        """
        if self._button:
            self._fields["payload"]["elements"][0]["buttons"] = self._button.get_dict()
        return self._fields
