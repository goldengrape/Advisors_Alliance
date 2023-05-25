import streamlit as st 
from six_hats_GUI import (
    init_session_state,
    init_sessions, 
    set_settings,
    set_header,set_chatbox, display_history)
from audiorecorder import audiorecorder


init_sessions()

# layout 
header = st.container()
# settings = st.sidebar.container()
settings=st.expander("虎符")
audio = audiorecorder("主公请讲话", "记录中...")

chat_box=st.container()

st.markdown("---")
history=st.container()

# 
with settings:
    set_settings(settings)

set_header(header)
set_chatbox(chat_box,audio)
display_history(history)