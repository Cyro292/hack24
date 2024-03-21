# Download the helper library from https://www.twilio.com/docs/python/install
import os
from twilio.rest import Client

from dotenv import load_dotenv

load_dotenv()

# Set environment variables for your credentials
# Read more at http://twil.io/secure

account_sid = "AC690145ec38222226d949960846d71393"
auth_token = os.environ["TWILIO_AUTH_TOKEN"]
client = Client(account_sid, auth_token)

call = client.calls.create(
  url="http://demo.twilio.com/docs/voice.xml",
  to="+41779671592",
  from_="+14243651541"
)

print(call.sid)