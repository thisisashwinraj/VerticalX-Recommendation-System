import streamlit

SENDER_EMAIL_ID = streamlit.secrets["SENDER_EMAIL_ID"]
SENDER_EMAIL_PASSWORD = streamlit.secrets["SENDER_EMAIL_PASSWORD"]

"""
SENDER_EMAIL_ID = os.environ["SENDER_EMAIL_ID"]
SENDER_EMAIL_PASSWORD = os.environ["SENDER_EMAIL_PASSWORD"]
"""