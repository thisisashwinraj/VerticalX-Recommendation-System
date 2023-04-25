# Author: Ashwin Raj <thisisashwinraj@gmail.com>
# License: Creative Commons Attribution - NonCommercial - NoDerivs License
# Discussions-to: github.com/thisisashwinraj/CroMa-Crowd-Management-System/discussions

# This file contains code derived from or inspired by code licensed under the GNU
# Affero General Public License v3 (AGPLv3). Copyright (C) 2023 SilverSpace
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation, either version 3 of the License, or (at your option) any
# later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License along
# with this program.  If not, see <https://www.gnu.org/licenses/>.

"""
This module contains the code for sending emails with attachments using the SMTP
protocol. It can be used to send both plain text mails, and rich text HTML mails
after changing payload to encoded format. This module uses smtp.gmail.com server 
at port 587 for sending the mails with MIMEBase payloads, and base64 attachments.

Module Classes and Methods:
    [1] MovieInfoMail
        [a] is_valid_email
        [b] send_movie_recommendations_mail

    [2] BugReportMail
        [a] send_bug_report_mail

.. versionadded:: 1.2.0

Read more about the use case of SMTP e-mail in :ref:`SilverSpace - Send to mail`
"""

import re  # Module for regular expressions operations
import smtplib  # Module defining an SMTP client session object
from datetime import datetime  # Module supplies classes for working with date & time
import time  # Module provides various time-related functions

from email.mime.multipart import (
    MIMEMultipart,
)  # Imports Multipurpose Internet Mail Extensions
from email.mime.text import (
    MIMEText,
)  # Sub-class of MineMase used for adding text to email
from email.mime.base import (
    MIMEBase,
)  # Base class for all MIME-specific subclasses in email

from email import (
    encoders,
)  # Module with functions to encode & decode data in various formats
from email.mime.application import (
    MIMEApplication,
)  # Adds non-text files to email messages

from config import mail_credentials  # custom module for storing email credentials


class MovieInfoMail:
    """
    Class for validation mail id and sending movie recommendations to user via mail

    This class provides methods for validating mail addresses and for sending movie
    information to recipients via plain-text mail on their e-mail id's. It requires
    access to valid mail credentials of the recipiemt in order to send the messages.

    The mail is sent to the receiver's mail id using smtp.gmail.com server port 587.

    .. versionadded:: 1.2.0

    NOTE: Attachments can also be passed as arguments for the user to send any file.
    """

    def is_valid_email(email):
        """
        Method to check if the string passed as an argument is a valid mail id or not.

        Using regular expression, this method checks whether the given string matches
        the pattern specified for validating an e-mail address, and returns True only
        if there's match. The method returns False if it doesn't match the expression.

        Read more in the :ref:`SilverSpace - Send to mail`.

        .. versionadded:: 1.0.0
        .. versionupdated:: 1.2.0

        Parameters:
            [str] e-mail id -> String that needs to be checked if its a valid mail id

        Returns:
            [bool] True/False -> Returns True if e-mail id is valid & False otherwise
        """
        # Define a regular expression for validating email addresses
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"

        # Return boolean value indicating whether the email address is valid or not
        return re.match(pattern, email) is not None

    def send_movie_recommendations_mail(
        RECEIVER_EMAIL_ID, list_of_movies, attachment=None
    ):
        """
        Method to send the movie recommendations e-mail with an attachment to the users.

        Sends an email from the support team's mail id to the web app user's mail using
        the smtp.gmail.com server at port 587 along with a PDF attachment, as a payload.
        The PDF attachment is a optional argument and depends on the user's preferences.

        .. versionadded:: 1.2.0

        Parameters:
            [str] RECEIVER_EMAIL_ID -> email id of the user to which mail is to be sent
            [str] list_of_movies -> list of movies recommended as per user's selections
            [file] attachment (optional arg) -> attachments to be included in the email

        Returns:
            None -> Sends an email with atttachment to the receivers mail id using SMTP
        """
        # Receiver's email id is fixed as the developer team's email id
        SENDER_EMAIL_ID = mail_credentials.SENDER_EMAIL_ID

        message = MIMEMultipart()  # Create an instance of MIMEMultipart

        message[
            "To"
        ] = RECEIVER_EMAIL_ID  #  Store the receivers mail id in the To field

        message["From"] = SENDER_EMAIL_ID  # Store the senders mail id in the From field

        message[
            "Subject"
        ] = "Howdy, your recommendations are here!"  # Store the subject of the mail in the subject field

        # Store the body of the mail to be sent to the users
        br_mail_body = (
            "Greetings,"
            + ",\n\nWe hope this email finds you well. We appreciate you being amongst the first hundred users to try SilverSpace.\n\nPlease find below the movie recommendations as per your selection. "
            + "\n\n1. "
            + list_of_movies[0]
            + "\n2. "
            + list_of_movies[1]
            + "\n3. "
            + list_of_movies[2]
            + "\n4. "
            + list_of_movies[3]
            + "\n5. "
            + list_of_movies[4]
            + "\n\nWe have taken great care to ensure the accuracy of the recommendations, and we hope you will have a great time  watching these flicks.\n\nIf you have any questions or need further assistance, please do not hesitate to reach out to us.\n\nBest regards,\nSilverSpace Community Team"
        )

        message.attach(
            MIMEText(br_mail_body, "plain", "utf-8")
        )  # Attach the email body with the mail instance

        # Check if a file is provided as an attachment to be sent across
        if attachment:
            att = MIMEApplication(
                attachment.read()  # pylint: disable=no-member
            )  # Read the attachment using read method
            att.add_header(
                "Content-Disposition",
                "attachment",
                filename=attachment.name,  # pylint: disable=no-member
            )
            message.attach(att)  # Attach the file to the email

        server = smtplib.SMTP(
            "smtp.gmail.com", 587
        )  # Create an SMTP session at Port 587
        server.starttls()  # Encrypt the connection using transport layer security
        server.ehlo()  # Hostname to send for this command defaults to the FQDN of the local host.

        # Authenticate the sender before sending the email to the receiver
        server.login(
            mail_credentials.SENDER_EMAIL_ID, mail_credentials.SENDER_EMAIL_PASSWORD
        )
        text = (
            message.as_string()
        )  # Converts the Multipart mail into a string & send the mail

        # Perform entire mail transaction
        server.sendmail(mail_credentials.SENDER_EMAIL_ID, RECEIVER_EMAIL_ID, text)
        server.quit()  # Terminate the SMTP session after sending the mail


class BugReportMail:  # pylint: disable=too-few-public-methods
    """
    Class to send bug report emails with form info and file attachments to the admin

    The bug report typically includes information about the error including steps to
    reproduce the issue, the expected behavior, and the actual behavior observed. It
    also includes details about the user's environment such as the operating systems,
    software version and hardware details. These reports help developers to identify
    & fix the reported issue - improving the software's functionality, & performance

    The mail is sent to the receiver's email id (in this case, the admins or cluster
    managers) using the smtp.gmail.com server at port 587 alongside all the payloads.

    .. versionadded:: 1.2.0
    """

    def send_bug_report_mail(
        br_full_name,
        br_email_id,
        br_bug_in_page,
        br_bug_type,
        br_bug_description,
        attachment=None,
    ):  # pylint: disable=no-self-argument
        """
        Method to send a mail with a bug report, reported by a user to CroMa's dev team

        Sends an email from the support team's mail id to the dev team's email id using
        the smtp.gmail.com server at port 587 along with a PDF attachment, as a payload.

        .. versionadded:: 1.2.0

        Parameters:
            [str] br_full_name -> Full name of the contributor who is reporting the bug
            [str] br_email_id -> E-Mail id of the contributor who is reporting the bugs
            [str] br_bug_in_page -> Specific page in which the bug was reported by user
            [str] br_bug_type -> The type/kind of the bug that are being reported to us
            [str] br_bug_description -> Bug description with step to reproduce the same
            [file] attachment: A pdf file or an image file to be attached to the e-mail

        Returns:
            None -> Sends an email with atttachment to the receivers mail id using SMTP
        """
        # Receiver's and Sender's email id is fixed to be the developer team's email id
        RECEIVER_EMAIL_ID = "rajashwin733@gmail.com"
        SENDER_EMAIL_ID = mail_credentials.SENDER_EMAIL_ID

        message = MIMEMultipart()  # Create an instance of MIMEMultipart

        message[
            "To"
        ] = RECEIVER_EMAIL_ID  #  Store the receivers mail id in the To field

        message["From"] = SENDER_EMAIL_ID  # Store the senders mail id in the From field

        message[
            "Subject"
        ] = "SilverSpace Bug Report"  # Store the subject of the mail in the subject field

        br_mail_body = (
            "Hello team,\n\nA new bug report has been raised in SilverSpace. "
            + "Please find the details as mentioned below.\n\nSubmitted by: "
            + br_full_name
            + "\n\nE-Mail Id: "
            + br_email_id
            + "\n\nBug Reported In: "
            + br_bug_in_page
            + "\n\nType of Bug: "
            + br_bug_type
            + "\n\nDescription: "
            + br_bug_description
            + "\n\nRegards,\nSilverSpace Support Team"
        )  # Store the body of the mail in the function variable named br_mail_body

        message.attach(
            MIMEText(br_mail_body, "plain", "utf-8")
        )  # Attach body with email instance

        # Check if a file is provided as an attachment to be sent across
        if attachment:
            att = MIMEApplication(
                attachment.read()  # pylint: disable=no-member
            )  # Read the attachment using read method
            att.add_header(
                "Content-Disposition",
                "attachment",
                filename=attachment.name,  # pylint: disable=no-member
            )
            message.attach(att)  # Attach the file to the email

        server = smtplib.SMTP(
            "smtp.gmail.com", 587
        )  # Create an SMTP session at Port 587
        server.starttls()  # Encrypt the connection using transport layer security
        server.ehlo()  # Hostname to send for this command defaults to the FQDN of the local host.

        # Authenticate the sender before sending the email to the receiver
        server.login(
            mail_credentials.SENDER_EMAIL_ID, mail_credentials.SENDER_EMAIL_PASSWORD
        )
        text = (
            message.as_string()
        )  # Converts the Multipart mail into a string & send the mail

        # Perform entire mail transaction
        server.sendmail(mail_credentials.SENDER_EMAIL_ID, RECEIVER_EMAIL_ID, text)
        server.quit()  # Terminate the SMTP session after sending the mail
