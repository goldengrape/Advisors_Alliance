import streamlit as st 
from six_hats_GUI import init_sessions, set_settings,set_header,set_chatbox, display_history

init_sessions()

# layout 
settings = st.sidebar.container()
header = st.container()
chat_box=st.container()
st.markdown("---")
history=st.container()

# 
with settings:
    set_settings(settings)

set_header(header)
set_chatbox(chat_box)
display_history(history)