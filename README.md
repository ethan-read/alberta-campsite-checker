The config.txt file specifies the search parameters for the campsite. It is pre-loaded with example values
and should remain in that format, otherwise the script will return an error.

The SMS functionality requires a twilio account and a file named twilio.env in the same directory as
the script, configured with phone numbers and twilio account information in the format of:


export TWILIO_PHONE_NUMBER='+1234567890'
export TWILIO_ACCOUNT_SID='your account sid'
export TWILIO_AUTH_TOKEN='your auth token'
export RECIPIENT_PHONE_NUMBER='+10987654321'
