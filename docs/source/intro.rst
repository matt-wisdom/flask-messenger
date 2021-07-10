Quickstart
============

``flask_messenger`` is a flask extension that provides an easy way to use facebook's
messenger api. It makes creation of webhooks and sending of messages very easy and can
be used to create chatbots with less effort.


Examples
========

Installation/Usage:
*******************

As at the the time of writing this, this extension is not yet available on PyPi.
To install using pip, run:
::
    python -m pip install git+https://github.com/cRyp70s/flask-messenger.git
Or clone the repository and install.
::
    git clone https://github.com/cRyp70s/flask-messenger.git
    python setup.py install


Simple bot
**********
A simple bot.
::
     """This example is a bot that replies to an hello 
        message from a user."""

     from flask_messenger import Messenger
     from flask import Flask
     
     app = Flask(__name__)
     messenger = Messenger(app, webhook_token={'/webhook': 'VERIFY_TOKEN'},
         access_token='dsfdfdfdfdfd')
     
     @messenger.on("messages")
     def handle_text(msg_obj):
        if msg_obj.text == 'hello':
            messenger.reply_to(msg_obj, text="Hi, how may i help you?")
     
     if __name__ == '__main__':
         app.run()

Run the above code (you can use ngrok to make your localhost accessible).
Ensure you've created your facebook page and you understand how to setup a 
facebook app webook and subscribe to events. If you don't. Visit this link `Messenger Api <https://developers.facebook.com/docs/messenger-platform/>`_
