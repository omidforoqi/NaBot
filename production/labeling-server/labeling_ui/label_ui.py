import streamlit as st
from labeldb import Labeling
from decouple import config

# import `.env` variables 
DB_HOST = config('LABEL_DB_HOST')
DB_NAME = config('POSTGRES_LABEL_DATABASE')
DB_USER = config('POSTGRES_USER')
DB_PASSWD = config('POSTGRES_LABEL_PASSWORD')
DB_PORT = config('POSTGRES_PORT')

# connect to database
labeling = Labeling(DB_NAME, DB_USER, DB_PASSWD, DB_HOST, DB_PORT)

# Set page layout to wide
st.set_page_config(
    page_title="Labeling", layout="wide",
)
# SET page title
page_title = "<h1 style='text-align: center;'>label</h1>"
st.markdown(page_title, unsafe_allow_html=True)
if 'feedback_value' not in st.session_state:
    st.session_state.feedback_value = False

def submit_feedback():
    labeling.write_record(
        st.session_state.username, 
        st.session_state.summary,
        st.session_state.feedback_value,
        st.session_state.user_summary if st.session_state.user_summary !="" else None,
        )

# user take username and check is valid or not
if 'login_result' not in st.session_state:
    st.text_input("Username", key="username")
    st.text_input("Password", key="passwd", max_chars=12, type='password')
    if st.button('Login'):
        st.session_state.login_result = labeling.login_user(st.session_state.username, st.session_state.passwd)
elif st.session_state.login_result:
    st.success(f"Welcome {st.session_state.username}")
    st.session_state.context, st.session_state.summary = labeling.give_record(st.session_state.username)
    st.subheader("Context")
    st.write(st.session_state.context)
    st.subheader("Summary")
    st.write(st.session_state.summary)
    with st.form("feedack_form"):
        st.subheader("Is this summary correct?")
        feedback_radio = st.radio("Is the summary correct?", ("True", "False"))
        st.session_state.feedback_value = True if feedback_radio == "True" else False
        st.text_area("if the summary isn't correct please write correct summary", key='user_summary')
        subimt = st.form_submit_button("Submit", on_click=submit_feedback)

else:
    st.warning(f"login not correct, Try again after refrash page")
    del st.session_state.login_result


# add user to a session 
# if user not in st.session_state:
#     st.session_state['user'] = user
