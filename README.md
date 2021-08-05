# FLASK-MESSENGER

This is an extension that provides a relatively easy interface to use the facebook messenger api (send and recieve).  
It makes the creation of webhooks easy and provides a variety of functionalities.  
There is support for the following events: 
1. messages
2. messaging_postback
3. message_deliveries 
4. message_reads
5. message_reactions  

And there is support for sending the following:
1. Quick replies
2. Attachments (video, audio, file, image and templates)
3. Templates (generic, button, reciept, media)
4. Buttons (url, call, postback, login, logut)

<b>Note:</b> This is an unofficial wrapper around the facebook messenger api, If you dont understand what some of the terms are. Please
refer to the official facebook messenger api documentation.
## Before Starting
Ensure you've created your facebook page and you understand how to setup a facebook app webook and subscribe to events. If you don't. Visit this link
[Messenger Api](https://developers.facebook.com/docs/messenger-platform/)


## Installation/Usage:


As at the the time of writing this, this extension is not yet available on PyPi.
To install using pip, run:
<pre>
    python -m pip install git+https://github.com/cRyp70s/flask-messenger.git
</pre>
Or clone the repository and install.
<pre>
    git clone https://github.com/cRyp70s/flask-messenger.git
    python setup.py install
</pre>


## Quickstart
<pre>
from flask_messenger import Messenger
from flask import Flask

app = Flask(__name__)
messenger = Messenger(app, webhook_token={'/webhook': 'VERIFY_TOKEN'}, access_token='dsfdfdfdfdfd')

@messenger.on("messages")
def handle_text(msg_obj):
    if msg_obj.text == 'hello':
        messenger.reply_to(msg_obj, text="Hi, how may i help you?")

if __name__ == '__main__':
    app.run()
</pre>
Running the above code, starts a flask server with the webook mounted on http://localhost:5000/webhook.
You can then run ngrok to make the webhook public.
The webhook listens for messages sent by users and if the message is "hello", it replies with "Hi, how may i help you?".

### Webook endpoints  
Webhook endpoints and verify token must be passed when instantiating the `Messenger` object using the webhook_token
argument. The value is a dictionary of webhook endpoint as key and the verify token as value.

### Events  
Messenger webhook events can be listened using the  `Messenger.on` decorator to register a handler.
The argument to this decorator is the event which can be any of: __messages, messaging_postback, message_deliveries, message_reads, message_reactions__.
The handler should take only one argument i.e The event object.

### Event objects  
These are objects that represent the data sent by messenger for an event and are passed as argument to the handler function.
The event objects available and their properties are as follows:

#### RecievedMessage  
This is the event object for messages events. The properties are:
1. `text` - The text of recieved message.  
2. `mid` - The message id.  
3. `is_quick_reply` - Boolean. True if the user sent this by clicking a quick reply button.  
4. `is_reply` - True if the message is a reply.  
5. `has_attachment` - True if the message has an attachment.    
6. `is_referral` - True if the message has referral field.  
7. `quick_reply_payload` - The payload for a quick reply.  
8. `reply_to` - The message id of the message replied to.  
9. `referral_id`   
10. `attachments` - A list of Attachment objects.    

#### Reaction  
This is the event object for message_reactions events. The properties are:
1. `reaction` - The reaction.  
2. `action` - The action (either react or unreact).  
3. `emoji`- The emoji's unicode character for the reaction.  
4. `mid` - The message id for which the reation was targeted.  

#### Postback  
This is the event object for messaging_postback events which are sent when a button in a message is clicked. The properties are:
1. `mid` - The message id whose button was clicked.  
2. `title` - The title of the clicked button.  
3. `payload` - The payload of the clicked button.  
4. `referral` -   

#### MessageReads
This is the event object for message_reads events. The properties are:
1. `watermark` - 

#### MessageDeliveries
This is the event object for message_deliveries events. The properties are:
1. `watermark` - 
2. `mids` - The id's of messages delivered


### Attachments
Attachment can be any of the following types: image, video, audio, file, templates.
template objects are located in flask_messenger.templates and the others are in 
flask_messenger.message as the Attachment object.

#### Attachment object  
The __Attachment object__ can be used to send image, video, audio and file attachments
and is returned in messages with attachments. The following properties are defined:
1. `url` - set or retrieve the url of the attachment.
2. `is_location_data` - True if the attachment has location data for location quick replies.
3. `coordinates` - A list of latitude, longitude when user clicks location quick replies.
4. `type` - Sets or gets type of attachment. Any of image, video, audio, file, templates
5. `is_reusable` - 
6. `download_attachment` - Method to download the attachment.
To create an attachment. Just create an instance of the Attachment class and set the relevant properties 
defined above.
eg 
<code>
    attachment = Attachment()
    attachment.type = "image"
    attachment.url = "https://example.com/img.png"
</code>

## Template objects  
Template objects are available in flask_messenger.templates.
The following template methods are available:  
**GenericTemplate**  
    GenericTemplate objects are used to send generic template attachments. To send a generic template,
    create an instance of the the GenericTemplate class with the following arguments:
    `title`: .  
    `image_url`: Optional url of image to be included in the template.  
    `subtitle`: Optional Subtitle.  
    The following methods are also defined:  
    `set_default_action(url)`: Sets the default action to url.  
    `add_buttons(button_list)`: adds buttons given by a list of Button objects.  

**ButtonTemplate**  
    ButtonTemplate objects are used to send button template attachments. To send a button template,
    create an instance of the the ButtonTemplate class with the following arguments:
    `text`:   
    `buttons`: A list of button objects. This buttons may not be set immediately and can be set later  
    with add_buttons method.  
    The following methods is defined:  
    `add_buttons(button_list)`: Takes a list of Button objects.  

**RecieptTemplate**  
    RecieptTemplate objects are used to send reciept template attachments. To send a reciept template,
    create an instance of the the RecieptTemplate class with the following arguments:
    `recipient_name`  
    `order_number`  
    `payment_method`  
    `timestamp`: Optional.  
    `currency`: Optional. defaults to USD.  
    `merchant_name`: Optional.  
    `order_url`: Optional  
    The following methods are defined:  
    `set_address(street_1, city, postal_code, state, country, street_2="")`  
    `set_summary(total_cost, subtotal=0, shipping_cost=0, total_tax=0)`  
    `add_adjustment(name, amount)`  
    `add_element(title, price ,subtitle="", quantity=0, currency="", image_url="")`

**MediaTemplate**  
    MediaTemplate objects are used to send media template attachments. To send a media template,
    create an instance of the the MediaTemplate class with the following arguments:
    `media_type`: Optional, defaults to image. Valid values are image and video.  
    `attachment_id`: The id of a saved attachment. Either this or url must be set but not both.  
    `url`: The url of the attachment. Either this or attachment_id must be set but not both.  
    The following methods are defined:  
    `add_button(button)`: button is a Button objects.  


## Buttons
Buttons are available in flask_messenger.buttons:  
**URLButton**  
    Create an instance of URLButton with the following arguments:  
    `url`  
    `title`: Optional.  
    The following methods are defined:  
    `add_optionals(whr=whr, me=me, fu=fu, wsb=wsb)`  
        or
    `add_optionals({'whr':whr, 'me':me, 'fu':fu, 'wsb':wsb})`  
    where:
        `whr` is webview_height_ratio  
        `me` is messenger_extensions  
        `fu` is fallback_url  
        `wsb` is webview_share_button  

**CallButton**  
Create an instance of CallButton with the following arguments:  
`title`  
`payload`  

**PostBackButton**  
Create an instance of PostBackButton with the following arguments:  
`title`  
`payload`  

**LogInButton**  
Create an instance of LogInButton with the following arguments:  
`url`  

**LogOutButton**  
Create an instance of LogOutButton with the following arguments  

## Sending Messages  
A send_message and reply_to method is provided in the Messenger object

send_message takes the following arguments:
1. `recipient`: The recipient objects which is a dictionary of one entry that can have any of 
            the following keys: id, user_ref, post_id, comment_id and their  appropriate values.  
2. `access_token`: This is optional  and needs to be set if access_token was not set when creating the Messenger instantance.  
3. `text`: text string. Either text, attachment or sender_action must be set but not any two or all of them.  
4. `attachment`: The value is Attachment or template object. Either text, attachment or sender_action must be set but not any two or all of them.  
5. `quick_replies`: A list of QuickReply objects.  
6. `sender_action`: Action to be sent. Any of "typing_on", "typing_off" or "mark_seen". Cannot be set with attachment or text.  
7. `type_`: The type of message to be sent. Must be any of RESPONSE, UPDATE, MESSAGE_TAG.  

`reply_to` takes the same arguments as send_message except that in place of recipient, the RecievedMessage object should be used.

The return values is a dictionary of the response

## Quick Replies
The QuickReply object can be found in flask_messenger.message.

QuickReply(type, title, image_url, payload)  
arguments:  
1. `type`:  The type of quick replies. It can be any of: text, location, user_phone_number, user_email.  
2. `title`: This is needed only when using text type.  
3. `image_url`: The url of an image to be sent along side the text quick reply.  
4. `payload`: The payload for text quick reply.  


## TODO
- Tests
