import streamlit as st
from datetime import date, datetime, timedelta
from GolfClassMulti import GolfMulti
import emoji
import re
def is_valid_email(email): return re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$', email)

page_title = "Golf Cancellations"
page_icon = ":man_golfing:" #https://www.webfx.com/tools/emoji-cheat-sheet/
layout = "centered"

st.set_page_config(page_title = page_title, page_icon = page_icon, layout = layout)
st.title(page_title + " " + emoji.emojize(page_icon))

with st.form("myForm", clear_on_submit = False):
    col1, col2 = st.columns(2)
    first = col1.text_input("First Name")
    last = col2.text_input("Last Name")

    email = st.text_input("Email Address") #add validation
    
    #with st.expander("Options:"):
    #key or name, both do same thing
    facilities = st.multiselect("Select Courses", options = ("Okeeheelee", "Osprey Point", "Park Ridge", "Southwinds"))
    #value allows for date range
    col3, col4 = st.columns(2)
    dates = col3.date_input("Enter date range to golf", value = (), min_value = date.today(), max_value = date.today() + timedelta(days=7), format = "MM/DD/YYYY")
    time_of_day = col4.multiselect("Select Time of Day", options = ("Morning", "Midday", "Evening"))
    
    col5, col6 = st.columns(2)
    num_players = col5.multiselect("Select Number of Players", options = ("1", "2", "3", "4"))
    num_holes = col6.multiselect("Select Number of Holes", options = ("9","18"))

    submitted = st.form_submit_button("Find Tee Times")
    if submitted: #if submit pressed
        #FIXME - input verification
        if len(first) == 0 or len(last) == 0 or len(email) == 0 or len(facilities) == 0 or len(dates) == 0 or len(num_players) == 0 or len(time_of_day) == 0 or len(num_holes) == 0:
            st.warning("Required Fields Blank")
        elif (not is_valid_email(email)):
            st.warning("Email format invalid")
        else:
            st.success("Submit success")
            dates = [date.strftime("%m-%d-%Y") for date in dates]
            print(facilities, dates, num_players, time_of_day, num_holes)

            GolfMulti(dates, facilities, num_players, time_of_day, num_holes, email)
 
