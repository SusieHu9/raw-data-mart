import streamlit as st  # pip install streamlit


if not 'status' in st.session_state:
    st.session_state['status'] = None
if not 'info_user' in st.session_state:
    st.session_state['info_user'] ={}



# emojis: https://www.webfx.com/tools/emoji-cheat-sheet/
st.set_page_config(page_title="“Will Call” Raw Data Mart", page_icon=":floppy_disk:", layout="wide")

hide_bar= """
    <style>
    [data-testid="stSidebar"][aria-expanded="true"] > div:first-child {
        visibility:hidden;
        width: 0px;
    }
    [data-testid="stSidebar"][aria-expanded="false"] > div:first-child {
        visibility:hidden;
    }
    </style>
"""

import requests
import json

url = 'https://raw-data-mart-default-rtdb.firebaseio.com/'

# Define function for user registration
def register():
    with st.form('Register'):
        email = st.text_input("Email:")
        password = st.text_input("Password", type="password")
        invite_code = st.text_input("Invitation code")
        register_submit = st.form_submit_button("Register")
    if register_submit:
        a = requests.get(url+'user.json?orderBy="email"&equalTo="'+email+'"')
        try:
            true_invite_code = list(json.loads(a.text).values())[0]['invitecode']
            userid = list(json.loads(a.text).values())[0]['userid']
            if (true_invite_code == invite_code) & (password != ''):
                requests.put(url+'user/'+userid+'/password.json',json = password)
                st.success("Registration successful!")
            else: 
                st.error("Error: Invitation code does not match or password is null, please try again")
        except:
            st.error("Error: Invitation code does not match or password is null, please try again")
        

# Define function for user login
def login():
    with st.form("Log in"):
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Log in")
        if login_submit:
            a = json.loads(requests.get(url+'user.json?orderBy="email"&equalTo="'+email+'"').text)
            if a == {}:
                st.error('Error: email doesn\'t exist')
            else:
                true_password = list(a.values())[0]['password']
                if (password == true_password):
                    st.session_state['status'] = email
                    st.success("Login successful!")
                    st.experimental_rerun()
                else:
                    st.error('Error: Password is incorrect')


# Define function for resetting password
def reset_password():
    with st.form('Reset'):
        email = st.text_input("Confirm Email")
        new_password = st.text_input("New Password", type="password")
        confirm_password = st.text_input("Confirm New Password", type="password")
        reset_submit = st.form_submit_button("Rest Password")
    if reset_submit:
        a = json.loads(requests.get(url +'user.json?orderBy="email"&equalTo="'+email+'"').text)
        if a == {}:
            st.error('Error: email doesn\'t exist')
        else:
            if new_password == confirm_password:
                requests.put(url+'user/'+list(a.values())[0]['userid']+'/password.json',json=new_password)
                st.success("Reset Password Successful!")
            else:
                st.error("Passwords do not match")
                

# Display the appropriate form based on the selected option
if st.session_state['status'] == None:
    st.title("User Registration and Login")
    # Add a button to choose registration or login
    option = st.radio("Select an option", ("Log in","Register","Reset Password"))
    if option == "Register":
        st.warning("Please fill out registration form")
        st.markdown(hide_bar, unsafe_allow_html=True)
        register()
    elif option == "Log in":
        st.warning("Please enter your email and password")
        st.markdown(hide_bar, unsafe_allow_html=True)
        login()
    elif option == "Reset Password":
        st.warning("Please fill out form to reset password")
        st.markdown(hide_bar, unsafe_allow_html=True)
        reset_password()

else:
    a = json.loads(requests.get(url + 'user.json?orderBy="email"&equalTo="'+st.session_state['status']+'"').text)
    a = list(a.values())[0]
    info_user = {}
    info_user['group'] = a['group']
    info_user['name'] = a['name']
    info_user['role'] = a['role']
    info_user['permission'] = a['permission']
    st.session_state['info_user'] = info_user

if st.session_state["status"]:
    # # ---- SIDEBAR ----
    st.sidebar.title("Welcome {username}".format(username = st.session_state["info_user"]["name"]))
    # st.sidebar.header("select page here :")
    st.title("Welcome to \"Will Call\" Raw Data Mart:v:")

    st.markdown(''' _**"Will Call" Raw Data Mart**_ is a centralized web-based platform for the storage, retrieval and management of raw sport medicine data.
            Tagged data organization, multimedia data compatibility, remote accessibility and quick retrieval are all available here. You can get 
            a streamlined easy-to-use workflow for biomechanics research.
            ''', unsafe_allow_html=True)
    st.markdown('👉 Select a page from dropdown on the left to see what we can do! _**Enjoy your data time~**_', unsafe_allow_html=True)   
    st.markdown("## Introduction")
    st.markdown('### 🔎 Query & Retrieve')
    st.write('''* _**Query & Retrieve**_ allows users to query and retrieve data with tags. You can preview and download multitudes of data here.
            ''')
    st.markdown('### 📂 Data Upload')
    st.write('''* _**Data Upload**_ will provide a one-stop shop for integrating tags, uploading and storing the various multimedia data obtained.
            ''')

    st.markdown('### 🕹 Data Management')
    st.write('''* _**Data Management**_ allows you to manage collections and fine-tuned corresponding tags.
            ''')
    
    st.markdown('### 👥 Authority Management')
    st.write('''* _**Authority Management**_ is related to the security of the system. 
             It also supports administrators to manage users and their data permissions.
            ''')
    
    st.markdown("## Acknowledgements")
    st.write('''This project was completed as part of course _**BME528 - Medical Diagnostics, Therapeutics and Informatics Applications**_. 
             We would like to express our gratitude to our professor _**Dr. Brent Liu**_ , project leader _**Anshu Goyal**_,
             and project sponsor _**Biomechanics Research Lab, USC Dornsife**_ for their invaluable guidance, leadership, and support.''')
             
    st.sidebar.success("Select a page above.")
        
    def logouted():
        for k in st.session_state.keys():
            del st.session_state[k]
    logouted = st.sidebar.button("Logout",on_click = logouted)


