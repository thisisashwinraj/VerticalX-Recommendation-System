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
This module contains the top-level environment of the Movie recommendation system.
It contains functions for generating recommendations, fetching posters and movies
related infomation using RESTful APIs and displaying the front-ent of the web app.

The front-end of the web application is developed using streamlit and css and the 
backend uses python3. The supporting modules and the related resources are stored 
in the model sub-directory of this repository. The API keys are stored as secrets.

Module Functions:
    [1] fetch_movie_poster
    [2] fetch_movie_trailer
    [3] apply_style_to_sidebar_button
    [4] recommend_movies
	[5] silverspace_home_page
	[6] about_silverspace_page
	[7] send_bug_report_page

.. versionadded:: 1.0.0
.. versionupdated:: 1.2.0

Read more about the functionality of the main module in :ref:`SilverSpace Homepage`
"""

import streamlit as st  # Import Streamlit library for building web applications
import pickle  # Import pickle to serialize and deserialize Python objects
import requests  # Import requests library for making HTTP requests
import pandas as pd  # Import pandas library for data manipulation and analysis
from azure.storage.blob import BlobServiceClient

import re  # Import regular expression library for text processing
import json  # Import JSON library for working with the OMDB JSON data
import time  # Import time library for adding delays and sleeping time

from model import send_mail  # Import send_mail function from ~/model
from config import api_credentials  # Importing API credentials from ~/config
from config import azure_credentials  # Importing Azure credentials from ~/config

from sumy.nlp.tokenizers import Tokenizer  # Import Tokenizer to tokenize text
from sumy.parsers.plaintext import PlaintextParser  # Import PlaintextParser for parsing
from sumy.summarizers.lex_rank import LexRankSummarizer  # Import LexRankSummarizer

import googleapiclient.discovery  # Import discovery module from googleapiclient
import googleapiclient.errors  # Import errors module from googleapiclient library


# Set the title and favicon for the streamlit web application
st.set_page_config(
    page_title="SilverSpace",
    page_icon="assets/favicon/silverspace_favicon.png",
)

# Remove the extra padding from the top margin of the web app
st.markdown(
    """
        <style>
               .block-container {
                    padding-top: 1rem;
					padding-bottom: 1rem;
                }
        </style>
        """,
    unsafe_allow_html=True,
)

# Hide streamlit menu and footer from the web app's interface
hide_menu_style = """
<style>
#MainMenu  {visibility: hidden;}
footer {visibility: hidden;}
</style>
"""
st.markdown(hide_menu_style, unsafe_allow_html=True)  # Allow HTML parsing

# Hide streamlit's default image expanders from app interface
hide_img_fs = """
<style>
button[title="View fullscreen"]{
    visibility: hidden;}
</style>
"""
st.markdown(hide_img_fs, unsafe_allow_html=True)  # Allow HTML parsing


def apply_style_to_sidebar_button(file_name):
    """
    Function to apply CSS-3 style specified in the arg file to the sidebar button.

    The function takes a CSS file as a parameter and applies the customized style
    to all the buttons widgets on the sidebars of the silverspace web application

    Read more in the :ref:`Styling the SilverSpace Web Application`.

    .. versionadded:: 1.2.0

    Parameters:
        [css file] file_name: CSS file holding style to be applied on the buttons

    Returns:
        None -> Applies the style specified in the CSS file to all sidebar button
    """
    try:
        # Open the CSS file and apply style to the sidebar button using markdown
        with open(file_name, encoding="utf-8") as file:
            st.markdown(f"<style>{file.read()}</style>", unsafe_allow_html=True)

    except:
        pass  # Do nothing if an error is raised, and continue program execution


# Call the apply_style_to_sidebar_button function with location of the CSS file
apply_style_to_sidebar_button("assets/style.css")


def load_pickle_from_azure(pickle_file_name):
    connection_string = azure_credentials.AZURE_CONNECTION_STRING
    container_name = azure_credentials.AZURE_CONTAINER_NAME

    blob_service_client = BlobServiceClient.from_connection_string(connection_string)
    
    # Get a reference to the container where your pickle file is stored
    container_client = blob_service_client.get_container_client(container_name)
    
    # Get a reference to the pickle file
    blob_client = container_client.get_blob_client(pickle_file_name)
    
    # Download the pickle file as a bytes object
    blob_data = blob_client.download_blob().readall()
    
    # Load the pickle file in rb (read-binary) mode
    pickle_data = pickle.loads(blob_data, encoding='latin1', fix_imports=True)
    
    return pickle_data


def fetch_movie_poster(movie_id):
    """
    Function to fetch the movie posters from the TMDb API using the given movieID.

    The function sends a GET request to the TMDb API to fetch the movie poster for
    a given movie ID. It returns the movie poster as a URL string that can be used
    to display the image. If the poster is not found or there is an error fetching
    movie's poster, the function will return the placeholder image url to the user

    Read more in the :ref:`TMDb API in SilverSpace Web Application`.

    .. versionadded:: 1.0.0
    .. versionupdated:: 1.2.0

    Parameters:
        [str] movie_id -> The TMDb ID of the movie to fetch the poster images for

    Returns:
        [str] url -> A string representation of the URL of the movie poster image

    NOTE: The API key used in this function is maintained using streamlit secrets
    When testing locally, replace the TMDb API Key in config/api_credentials file
    """
    # Send request to the TMDB API to get movie poster
    response = requests.get(api_credentials.TMDB_API_KEY.format(movie_id))
    data = response.json()  # Parse the JSON response from the API

    # Return the URL of the movie poster image
    return "https://image.tmdb.org/t/p/w500/" + data["poster_path"]


def fetch_movie_trailer(movie_name):
    """
    Function to fetch the movie trailers from the YouTube API using the given name.

    The function sends a GET request to the YouTube API to fetch movie trailer for
    a given movie name. It returns the movie trailers as a streamlit video element
    If the movie's trailer is not found on YouTube or if there's an error fetching
    movie trailer, the function will return a streamlit warning informing the same

    Read more in the :ref:`TMDb API in SilverSpace Web Application`.

    .. versionadded:: 1.0.0
    .. versionupdated:: 1.2.0

    Parameters:
        [str] movie_id -> The TMDb ID of the movie to fetch the poster image for

    Returns:
        [str] url -> A string representation of the URL of the movie poster image

    NOTE: The API key used in this function is maintained using streamlit secrets
    When testing locally, replace the TMDb API Key in config/api_credentials file
    """

    # Define the API key and YouTube API service
    youtube = googleapiclient.discovery.build(
        "youtube", "v3", developerKey=api_credentials.YOUTUBE_API_KEY
    )

    # Search for the movie trailer on YouTube
    query = movie_name + " official trailer"
    request = youtube.search().list(part="id", q=query, type="video")
    response = request.execute()

    # Extract the video ID from the API response
    video_id = response["items"][0]["id"]["videoId"]

    # Display the trailer in the streamlit app
    if video_id:
        # Display the video in the Streamlit app using the video ID
        return st.video(f"https://www.youtube.com/watch?v={video_id}")
    else:
        # If the video ID is not found, display a message in the web app
        return st.write("Trailer not found")


def recommend_movies(movie):
    """
    Function to recommend five movies, similar to the movie passed as the argument.

    The function takes title of a movie as an argument, searches for movies in the
    dataset that are similar to it, and returns the top five movie recommendations.
    Similarity is calculated based on a pre-computed similarity matrix of the data.

    Read more in the :ref:`SilverSpace Movie Recommendations - Algorithm`.

    .. versionadded:: 1.0.0
    .. versionupdated:: 1.2.0

    Parameters:
        [str] movie_id -> The title of the movie to recommend similar movies for

    Returns:
        [list] recommended_movies_titles -> Titles of the recommended movies
        [list] recommended_movies_poster -> URLs of poster of the recommended movie
    """
    try:
        # Get the index of the movie from the movies DataFrame
        movie_index = movies[movies["title"] == movie].index[0]
    except:
        # If the movie is not found, display an error message
        st.error("Could not find movie")

    # Get the cosine similarity of the movie with other movies
    distances = similarity[movie_index]
    # Get the top five movies that are most similar to the given movie
    movies_list = sorted(list(enumerate(distances)), reverse=True, key=lambda x: x[1])[
        1:6
    ]

    # Initialize lists to store the recommended movies and their posters
    recommended_movies_titles = []
    recommended_movies_poster = []

    try:
        # Iterate through the list of recommended movies
        for i in movies_list:
            # Get the movie ID and title of the recommended movie
            movie_id = movies.iloc[i[0]].movie_id
            recommended_movies_titles.append(movies.iloc[i[0]].title)

            # Fetch the poster of the recommended movie and add it to the list
            recommended_movies_poster.append(fetch_movie_poster(movie_id))
    except:
        # If the movie poster cannot be fetched, display an error message
        st.error("Could not fetch movie poster")

    # Return the list of recommended movies and their posters
    return recommended_movies_titles, recommended_movies_poster


def silverspace_home_page():
    """
    [SilverSpace Web App] (Page 01/03) - A Content Based Movie Recommendation System

    Function to display SilverSpace's home screen, with various interactive elements.

    The home page incorporates a select box element on the sidebar, that facilitates
    user input of the movie name. This data is then subsequently utilized to execute
    multiple tasks including displaying movie info & generating movie recommendation.

    This web application utilizes several API's to fetch information to be displayed
    to the user. Similarity matrix is maintained in pickle form hosted using Git LFS.

    Read more in the :ref:`SilverSpace - Home Page`.

    .. versionadded:: 1.2.0

    Dependencies:
        pandas, requests, re, json, pickle, streamlit, time, sumy, & googleapiclient

    APIs Used:
        TMDb API, OMDB API, YouTube API (Tokens are maintained as Streamlit Secrets)

    Alerts:
        movie_recommendations_email_sent_alert: Recommendations mailed succesfully
    """
    # Create a list of all movie titles
    movies_list = movies["title"].values

    # Display a dropdown sidebar widget to select a movie
    selected_movie = st.sidebar.selectbox("Select a Movie to Explore:", movies_list)

    # Add empty lines to the sidebar to separate content
    for _ in range(19):
        st.sidebar.write("\n\n")

    # Define the text and color of the sidebar footer (uses inline css)
    sidebar_footer_text = "SilverScape © 2023 • Designed by Ashwin Raj"
    sidebar_footer_color = "grey"

    # Create the sidebar footer HTML string with the specified text and color
    sidebar_footer = (
        f"<span style='color:{sidebar_footer_color}'>{sidebar_footer_text}</span>"
    )

    # Display the sidebar footer with the HTML string
    st.sidebar.markdown(sidebar_footer, unsafe_allow_html=True)

    # Define the OMDB API key and base URL
    API_KEY = api_credentials.OMDB_API_KEY
    OMDB_BASE_URL = "http://www.omdbapi.com/"

    # Search for the selected movie on OMDB using the API
    params = {"apikey": API_KEY, "t": selected_movie}
    response = requests.get(OMDB_BASE_URL, params=params).json()

    # If the user clicks on the selected_movie button
    if selected_movie:
        # Create two columns for displaying the movie title and ratings
        title_column, ratings_column = st.columns([1.935, 1])

        with title_column:
            # Display the selected movie title in a markdown header
            st.markdown("## " + selected_movie)

        with ratings_column:
            # Add a line break for maintaining the web app layout
            st.markdown("<br>", unsafe_allow_html=True)

            # If the IMDB rating is available, display it with a star emoji
            if "imdbRating" in response:
                st.markdown(
                    f"<p style='text-align: right;'>⭐ IMDb rating: {response['imdbRating']}/10</p>",
                    unsafe_allow_html=True,
                )

            # If the rating is not found, display a message
            else:
                st.write("Rating not found")

        # Create two columns for displaying the movie details
        left_ribbon_column, right_ribbon_column = st.columns([1.5, 1])

        # Create text for the left ribbon with released year, TV rating, and runtime
        with left_ribbon_column:
            left_details_ribbon_text = (
                "Released: "
                + response["Year"]
                + "&nbsp;&nbsp;•&nbsp;&nbsp;Rated: TV "
                + response["Rated"]
                + "&nbsp;&nbsp;•&nbsp;&nbsp;Runtime: "
                + response["Runtime"]
            )
            # Set the color of the left details ribbon to grey
            left_details_ribbon_color = "grey"
            # Create the left details ribbon with the text and color
            left_details_ribbon = f"<span style='color:{left_details_ribbon_color}'>{left_details_ribbon_text}</span>"

            # Display the left details ribbon in a markdown format
            st.markdown(left_details_ribbon, unsafe_allow_html=True)

        with right_ribbon_column:
            # Create the text for the right details ribbon with genre
            right_details_ribbon_text = "Genre: " + response["Genre"]
            # Set the color of the right details ribbon to grey
            right_details_ribbon_color = "grey"

            # Create the right details ribbon with the text and color
            right_details_ribbon = f"<p style='text-align: right;'><span style='color:{right_details_ribbon_color}'>{right_details_ribbon_text}</span></p>"

            # Display the right details ribbon in a markdown format
            st.markdown(right_details_ribbon, unsafe_allow_html=True)

        # poster_column to display movie poster and video_column to display movie trailer
        poster_column, video_column = st.columns([1, 1.935])

        with poster_column:
            if response.get("Poster"):
                # Display the poster in the streamlit app
                st.image(response["Poster"])
            else:
                # Display warning if no poster is returned
                st.markdown("<br><br><br><br>", unsafe_allow_html=True)
                st.warning("Poster is unavailable at the moment")

        with video_column:
            try:
                fetch_movie_trailer(
                    selected_movie
                )  # fetch and display the movie trailer
            except:
                # Display warning if no video is returned
                st.markdown("<br><br><br><br>", unsafe_allow_html=True)
                st.warning("Video is unavailable at the moment")

        st.markdown(
            "<p align='justify'>" + response["Plot"] + "</p>", unsafe_allow_html=True
        )

        # Display quick info about the movie
        left_details_ribbon_text = (
            "Awards: "
            + response["Awards"]
            + "&nbsp;&nbsp;•&nbsp;&nbsp;Language: "
            + response["Language"]
        )

        # set the colour of the test as grey using CSS
        left_details_ribbon_color = "grey"
        # Apply style to the text using the span class in HTML format
        left_details_ribbon = f"<span style='color:{left_details_ribbon_color}'>{left_details_ribbon_text}</span>"

        st.markdown(left_details_ribbon, unsafe_allow_html=True)

        # Add a horizontal line to separate the movie details from the recommended movies
        st.markdown("---")

        # Get name and posters of the recommended movies related to the selected movie
        name, posters = recommend_movies(selected_movie)

        # Create two columns of unequal width in the streamlit app interface
        quick_info_left, quick_info_right = st.columns([1.935, 1])

        # In the left column, create an expander widget for Contact the CroMa Team section
        with quick_info_left:
            # Create an expander widget for displaying more information about the movie
            st.markdown("**:information_desk_person: &nbsp;More Information:**")

            # Display the details of director, writer and the star cast
            cast_director_and_team_expander = st.expander("Full Cast and Crew")
            cast_director_and_team_expander.markdown(
                "**🎬 &nbsp;Director:** " + response["Director"], unsafe_allow_html=True
            )
            cast_director_and_team_expander.markdown(
                "**👨‍💼 &nbsp;Writer:** " + response["Writer"]
            )
            cast_director_and_team_expander.markdown(
                "**🎭 &nbsp;Cast:** " + response["Actors"]
            )

            # Display the details of the movie's metascore and its box office collection
            box_office_info_expander = st.expander("Production and Box Office")
            box_office_info_expander.markdown(
                "**🎬 &nbsp;Metascore:** " + response["Metascore"],
                unsafe_allow_html=True,
            )
            box_office_info_expander.markdown(
                "**👨‍💼 &nbsp;BoxOffice Collection:** " + response["BoxOffice"]
            )

        # In the right column, display a text input to fetch email id for mailing movie details
        with quick_info_right:
            # Increase the gap between the text input and the button to structure the UI
            st.markdown(
                """
				<style>
				div.stTextInput > div:first-child > input {
					height: 400px;
				}
				</style>
				""",
                unsafe_allow_html=True,
            )

            # Display an input widget to collect user's mail id for sending movie details
            movie_info_receiver_email_id = st.text_input(
                "Send Movie Info to Mail", placeholder="Enter your email id"
            )

            # Reset the bottom margin of the button and the text area to structure the UI
            st.markdown(
                """
			<style>
			div.stTextArea > div:first-child, div.stButton > button:first-child {
				margin-bottom: 10px;
			}
			</style>
			""",
                unsafe_allow_html=True,
            )

            # Create button to send movie details to the mail id entered in the text input
            send_movie_info_mail = st.button("Send the Movie Detail to Email")

            # If the button is clicked, send the movie details to the entered email id
            if send_movie_info_mail:
                send_mail.MovieInfoMail.send_movie_recommendations_mail(
                    movie_info_receiver_email_id, name
                )

                # Show a success message and remove it after 3 seconds
                movie_recommendations_email_sent_alert = st.success(
                    "Mail sent succesfully!", icon="✅"
                )

                time.sleep(3)  # Hold the execution for three seconds
                movie_recommendations_email_sent_alert.empty()  # Clear the alert message

        # Add a horizontal line to separate the two sections
        st.markdown("---")

        # Display a markdown message for recommended movies section.
        st.markdown("**🎭 &nbsp;More Flicks Like This:**")

        # Create 5 equal columns to display 5 recommended movies.
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:  # Within the first column
            # Display first recommended movie poster, with the movie name as the caption
            st.image(
                posters[0], use_column_width=True, caption=name[0], output_format="JPEG"
            )

        with col2:  # Within the second column
            # Display second recommended movie poster with the movie name as the caption
            st.image(
                posters[1], use_column_width=True, caption=name[1], output_format="JPEG"
            )

        with col3:  # Within the third column
            # Display third recommended movie poster, with the movie name as the caption
            st.image(
                posters[2], use_column_width=True, caption=name[2], output_format="JPEG"
            )

        with col4:  # Within the fourth column
            # Display fourth recommended movie poster with the movie name as the caption
            st.image(
                posters[3], use_column_width=True, caption=name[3], output_format="JPEG"
            )

        with col5:  # Within the fifth column
            # Display fifth recommended movie poster, with the movie name as the caption
            st.image(
                posters[4], use_column_width=True, caption=name[4], output_format="JPEG"
            )


def about_silverspace_page():
    """
    [SilverSpace Web App] (Page 02/03) - About Page for Movie Recommendations System

    Function to display SilverSpace's home screen, with various interactive elements.

    The about page documents the purpose, and use cases of the Movie recommendations
    system using various interactive widgets & elements. Check official docs for ref.

    The page includes several function to learn more about the movie recommender. It
    includes a email text input on the sidebar which can then be filled to subscribe
    to SilverSpace dev teams newsletter to get updates regarding new feature updates.

    Read more in the :ref:`Silverspace - About Movie Recommendation System`.

    .. versionadded:: 1.2.0

    Dependencies:
        streamlit, send_mail (custom-defined module)

    Alerts:
        newsletter_subscribed_alert: User's mail Id added to newsletter mailing list
    """
    # Display a markdown title for the about section with an emoji
    st.markdown("# :dart: About SilverSpace")

    # Display a paragraph with basic information about CroMa and it's features
    st.markdown(
        "<p align = 'justify'> SilverSpace is a web app that provides "
        + "a vast catalogue of movies, along with detailed information "
        + "about each one. With SilverSpace, you can browse through an "
        + "extensive collection of movies, from classic to contemporary, "
        + "watch their trailer & get a sneek peek into the plot to "
        + "discover titles that you're sure to love</p>",
        unsafe_allow_html=True,
    )

    # Display paragraph with information about ticketing machine and real-time database
    st.markdown(
        "<p align = 'justify'>SilverSpace utilizes multiple APIs like "
        + "OMDB open API, TMDB v3 API, YouTube API, and other APIs to "
        + "deliver personalized movie recommendations, corresponding to "
        + "the user's selection. SilverSpace is committed to providing "
        + "a seamless user experience, with an easy-to-navigate "
        + "interface that makes finding your favorite movies a breeze. "
        + "This web app is designed to work on any device so you can access "
        + "it anytime & anywhere</p>",
        unsafe_allow_html=True,
    )

    # Add an input box for the user to enter their email ID
    st.sidebar.text_input("Join our mailing list", placeholder="Enter your Email Id")

    # Apply the CSS styles defined in the parameter file to the sidebar buttons
    apply_style_to_sidebar_button("assets/style.css")

    # Add a button for the user to subscribe to the newsletter
    newsletter_mailing_list_user_email_id = st.sidebar.button(
        "Subscribe to our Newsletter"
    )

    if newsletter_mailing_list_user_email_id:
        # Display a success message when user subscribes to receive our newsletters
        newsletter_subscribed_alert = st.sidebar.success(
            "You have subscribed to newsletter", icon="✅"
        )

        time.sleep(3)  # Hold the execution for the next three seconds
        newsletter_subscribed_alert.empty()


def send_bug_report_page():
    """
    [SilverSpace Web App] (Page 03/03) - Send bug report to the silverspace dev team

    Fuction for sending a bug report mail from the specified sender email address to
    the team. The mail is structured with options to include one or more attachments.

    The send_bug_report() function sends an email containing bug reports submitted by
    users. This function takes in the user's name, e-mail id, and the bug description
    etc as input parameters. It then composes an email message using the user's input,
    and sends it to the dev team. If sent successfully it'll return a success message.

    Read more in the :ref:`SilverSpace - Bug Reports Page`.

    .. versionadded:: 1.2.0

    Dependencies:
        streamlit, send_mail (custom-defined module)

    Warnings:
        invalid_email_address: True if a user enters an invalid email id (ref: mail)

    Alerts:
        bug_report_sent_alert: Alert the users that the bug report has been e-mailed

    NOTE: Upcoming updates will include method to generate bug reports in PDF format
    """
    # Display a markdown title for the bug report  with a bug emoji
    st.markdown("# :ladybug: Send Bug Report")

    # Display a message to users who wish to report a bug
    st.markdown(
        "<p align = 'justify'>If you believe that you have discovered any "
        + "vulnerability in SilverSpace, please fill the form below with a thorough "
        + "explanation of the vulnerability. We will revert back to you after due "
        + "diligence of your bug report</p>",
        unsafe_allow_html=True,
    )
    # Create two columns to hold text input fields
    col1, col2 = st.columns(2)

    # Define context managers to set the current column for the following input fields
    with col1:
        # Create a text input field in the first column to read user's full name
        br_full_name = st.text_input("Full Name:")
    with col2:
        # Create a text input field in the second column to read user's email id
        br_email_id = st.text_input("E-Mail Id:")

    # Create two columns to hold input dropdown fields
    col3, col4 = st.columns(2)

    # Define context managers to set the current column for selectbox input field
    with col3:
        # Create a selectbox input field in the third column to read the bug location
        br_bug_in_page = st.selectbox("Which page is the bug in?", page_list)

    # Tuple of strings that represent different types of bugs for users to select from
    bug_types = (
        "General Bug/Error",
        "Access Token/API Key Disclosure",
        "Memory Corruption",
        "Database Injection",
        "Code Execution",
        "Denial of Service",
        "Privacy/Authorization",
    )

    # Define context managers to set the current column for selectbox input field
    with col4:
        # Create a selectbox input field in the fourth column to read the bug type
        br_bug_type = st.selectbox("What type of bug is it?", bug_types)

    # Create a text area where users can describe the bug and steps to reproduce it
    br_bug_description = st.text_area(
        "Describe the issue in detail (include steps to reproduce the issue):"
    )

    # Widget to upload relevant attachments, such as screenshots, charts, and reports.
    # The file uploader widget is set to accept multiple files (limit: 200mb per file)
    br_uploaded_files = st.file_uploader(
        "Include any relevant attachments such as screenshots, or reports:",
        accept_multiple_files=True,
    )

    # Checkbox that user must check to indicate that they accept terms & conditions
    bug_report_terms_and_conditions = st.checkbox(
        "I accept the terms and conditions and I consent to be contacted in future by "
        + "the CroMa support team"
    )

    # Create a button that the users can click to send the bug reports to the CroMa team
    # Disabled argument enables the button only if the user has checked the T&C checkbox
    if st.button("Send Bug Report", disabled=not bug_report_terms_and_conditions):
        # Create an instance of a BugReportMail object from the send_mail module
        bug_report = send_mail.BugReportMail

        # Call send_bug_report_mail method of the BugReportMail object to send the mail
        bug_report.send_bug_report_mail(
            br_full_name,
            br_email_id,
            br_bug_in_page,
            br_bug_type,
            br_bug_description,
            br_uploaded_files,
        )

        # Displays a success message to user indicating that their report has been sent
        bug_report_sent_alert = st.success("Your bug report has been sent!")

        time.sleep(3)  # Hold the execution for the next three seconds
        bug_report_sent_alert.empty()  #  Clear the bug_report_sent_alert from the frontend

    # Create an expander to display the FAQs regarding bug reports in the sidebar
    faq_expander = st.sidebar.expander("Frequently Asked Questions")

    # Display the various frequently asked questions in the sidebar expander
    faq_expander.write(
        "Q: Do you offer any kind of bug bounty?\nA: No, we do not offer any bug bounties."
    )  # FAQ Question 1
    faq_expander.write(
        "Q: How long does it takes to hear back?\nA: You'll hear back from us within 3 days."
    )  # FAQ Question 2
    faq_expander.write(
        "Q: Can we share our reports with others?\nA: We expect you don't share any report."
    )  # FAQ Question 3

    # Apply the CSS styles defined in the parameter file to the sidebar buttons
    apply_style_to_sidebar_button("assets/style.css")


try:
    # Try to load the movies dictionary from the pickle dump using pickle module
    movies_dict = load_pickle_from_azure("movie_dict_bkp.pkl")

except:
    # If file is not found or there's an error, display the error status message
    st.error("The web app is down 1")

# Convert the movies dictionary into a pandas dataframe
movies = pd.DataFrame(movies_dict)

try:
    # Try to load the similarity matrix from the pickle dump using pickle module
    similarity = load_pickle_from_azure("similarity_bkp.pkl")
except:
    # If file is not found or there's an error, display the error status message
    st.error("The web app is down 2")

# Create a dictionary of different pages of the web app along with the functions
page_list = {
    "SilverSpace Home": silverspace_home_page,
    "About SilverSpace": about_silverspace_page,
    "Send Bug Reports": send_bug_report_page,
}

# Create a dropdown menu for selecting a page from the page_list, passing the dictionary key
selected_page = st.sidebar.selectbox("Navigate Within Webapp:", page_list.keys())

# Reduce the margin and padding to structure the web application's user interface
st.markdown(
    """
		<style>
		hr {
			margin: 0px;
			padding: 0px;
		}
		</style>
		""",
    unsafe_allow_html=True,
)

st.sidebar.markdown("""---""")  # Add a horizontal line to the web app's sidebar

page_list[
    selected_page
]()  # Call function corresponding to the web app's page keeping the key as the index
