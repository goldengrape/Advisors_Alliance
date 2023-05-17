import streamlit as st 
from six_hats_backend import init_chain, init_advisor
import os 
from langchain.chat_models import ChatOpenAI

def init_session_state(key,value):
    if key not in st.session_state:
        st.session_state[key]=value


def init_sessions():
    init_session_state("individual_chain",None)
    init_session_state("summary_chain",None)
    init_session_state("human_input",None)
    init_session_state("history",[])
    init_session_state("advisor_list",init_advisor())

def set_settings(c):
    openai_key = c.text_input("OpenAI API Key", value="", type="password")
    st.session_state["model"] = c.selectbox(
        "模型", options=["gpt-3.5-turbo", "gpt-4"], index=0)
    temp_options = {"严谨": 0.1, "平衡": 0.5, "创意": 0.9}
    temperature = temp_options.get(
        c.select_slider("回答",
                        options=temp_options.keys(), value="平衡"))
    answer_length_options = {"简略": 50, "适中": 100, "详细": 150}
    answer_length = answer_length_options.get(
        c.select_slider("回答长度",
                        options=answer_length_options.keys(), value="简略"))

    st.session_state["answer_length"] = answer_length
    st.session_state["temperature"] = temperature
    
    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
        llm=ChatOpenAI(
            model_name=st.session_state["model"],
            temperature=st.session_state["temperature"],
            )
        individual_chain, summary_chain=init_chain(llm)
        st.session_state["individual_chain"]=individual_chain
        st.session_state["summary_chain"]=summary_chain
    else:
        st.error("请输入OpenAI API Key")
    
def set_header(c):
    c.markdown("#### 军师联盟")
    img_col=c.columns(6)
    for i, advisor in enumerate(st.session_state["advisor_list"]):
        # c.markdown(f'![image]({advisor["logo"]})')
        img_col[i].image(advisor["logo"],width=100)

        # img_col[i].latex(f'{advisor["name"]}')
        img_col[i].latex(f'{advisor["zi"]}')
        # img_col[i].markdown(f'* 个性{advisor["character"]}')


def get_advice(img_container,markdown_container):
    img_size=100
    current_memory="\n".join([
        message.content.strip() for message in st.session_state["summary_chain"].memory.chat_memory.messages])
    st.session_state["summary_chain"].memory.chat_memory.add_user_message(st.session_state["human_input"])
    
    st.session_state["history"].append("主公说："+st.session_state["human_input"])
    for advisor in st.session_state["advisor_list"][:-1]:
        res=st.session_state["individual_chain"].run(
            {"name":advisor["name"],
            "personality":advisor["personality"],
            "work":advisor["work"],
            "human_input":st.session_state["human_input"],
            "chat_history":current_memory,
            "length":st.session_state["answer_length"]}
        )
        st.session_state["summary_chain"].memory.chat_memory.add_ai_message(res)
        st.session_state["history"].append(res)
        img_container.image(advisor["logo"],width=img_size)
        markdown_container.markdown(f'{res}')
    advisor=st.session_state["advisor_list"][-1]
    res=st.session_state["summary_chain"].run(
        {"name":advisor["name"],
        "personality":advisor["personality"],
        "work":advisor["work"],
        "human_input":st.session_state["human_input"],
        "length":st.session_state["answer_length"]+50
        },
    )
    st.session_state["history"].append(res)
    img_container.image(advisor["logo"],width=img_size)
    markdown_container.markdown(f"{res}")
    return

def set_chatbox(c):
    human_input=c.text_area("主公请提问", value="")
    ask_button=c.button("提问")
    col1,col2=c.columns([1,6])
    current_img=col1.empty()
    current_advice=col2.empty()
    if human_input and ask_button and st.session_state["individual_chain"]:
        st.session_state["human_input"]=human_input
        # human_input,advisor_list,individual_chain,sum_chain
        get_advice(current_img,current_advice)
    # current_advice=c.empty()


def display_history(c):
    c.markdown("##### 会议纪要")
    meeting_notes=""
    for advice in st.session_state["history"]:
        meeting_notes+=f"\n\n{advice}"
    c.markdown(meeting_notes)
    c.download_button(
        label="下载会议纪要",
        data=meeting_notes,
        file_name="会议纪要.txt",
        mime="text/plain",
    )