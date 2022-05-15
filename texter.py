import os
from twilio.rest import Client
from dotenv import load_dotenv
from site_checker import set_config, generate_message
from time import sleep


load_dotenv(os.path.join(os.path.dirname(__file__), 'twilio.env'))

def send(msg):
    account_sid = os.environ['TWILIO_ACCOUNT_SID']
    auth_token = os.environ['TWILIO_AUTH_TOKEN']
    from_number = os.environ['TWILIO_PHONE_NUMBER']
    to_number = os.environ['RECIPIENT_PHONE_NUMBER']
    client = Client(account_sid, auth_token)

    client.messages.create(
              body=msg,
              from_=from_number,
              to=to_number
          )


if __name__ == "__main__":
    config = set_config(os.path.join(os.path.dirname(__file__), 'config.txt'))
    while True:
        print('Querying website...')
        msg = generate_message(config)
        print(msg)
        send(msg)
        sleep(1800)
