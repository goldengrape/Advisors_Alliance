import streamlit as st 
from six_hats_backend import (
    init_chain, init_advisor, transcribe
    )
import os 
from langchain.chat_models import ChatOpenAI
# from langchain.callbacks.base import BaseCallbackHandler
from langchain.schema import HumanMessage
from StreamHandler import StreamDisplayHandler, StreamSpeakHandler
from audiorecorder import audiorecorder



def init_session_state(key,value):
    if key not in st.session_state:
        st.session_state[key]=value


def init_sessions():
    init_session_state("individual_chain",None)
    init_session_state("summary_chain",None)
    init_session_state("human_input",None)
    init_session_state("history",[])
    init_session_state("advisor_list",init_advisor())
    init_session_state("stream_box",st.empty())


def set_settings(c):
    if st.secrets.get("openai_api_key"):
        openai_key = st.secrets.get("openai_api_key")
        speech_key=st.secrets.get("speech_key")
        speech_region=st.secrets.get("speech_region")
    else:
        openai_key = c.text_input("主公请输入虎符(OpenAI API Key)", value="", type="password")
        speech_key=c.text_input("主公请输入虎符(Azure Speech Key)", 
                                value="",  type="password")
        speech_region=c.text_input("主公请输入虎符(Azure Speech Region)", 
                                value="westus", type="password")

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
    speak_choose=c.selectbox("语音",options=["关闭","开启"],index=0)

    make_model_button = c.button("打造虎符")

    if openai_key:
        os.environ["OPENAI_API_KEY"] = openai_key
    if speech_key:
        os.environ['SPEECH_KEY']=speech_key
    if speech_region:
        os.environ['SPEECH_REGION']=speech_region

    if make_model_button and openai_key:
        stream_display_handler = StreamDisplayHandler(
            st.session_state["stream_box"], display_method='markdown')

        if speak_choose=="开启" and len(speech_key)>0 and len(speech_region)>0:
            speak_box=c.empty()
            stream_speak_handler = StreamSpeakHandler(
                container=speak_box,
                run_place=st.secrets.get("run_place", "cloud"),
                synthesis="zh-CN-YunjianNeural",
                rate="+50.00%")

            stream_handler=[stream_display_handler,stream_speak_handler]
        elif speak_choose=="开启":
            c.error("请输入语音虎符")
        else:
            stream_handler=[stream_display_handler]
        
        llm=ChatOpenAI(
            model_name=st.session_state["model"],
            temperature=st.session_state["temperature"],
            streaming=True, callbacks=stream_handler
            )
        individual_chain, summary_chain=init_chain(llm)
        st.session_state["individual_chain"]=individual_chain
        st.session_state["summary_chain"]=summary_chain
        c.success("虎符打造成功")

    # if openai_key:
    #     os.environ["OPENAI_API_KEY"] = openai_key
    #     llm=ChatOpenAI(
    #         model_name=st.session_state["model"],
    #         temperature=st.session_state["temperature"],
    #         streaming=True, callbacks=stream_handler
    #         )
    #     individual_chain, summary_chain=init_chain(llm)
    #     st.session_state["individual_chain"]=individual_chain
    #     st.session_state["summary_chain"]=summary_chain
    # else:
    #     st.error("请输入OpenAI API Key")
    
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
    st.session_state["history"].append("----")
    st.session_state["history"].append("**主公**说："+st.session_state["human_input"])
    for advisor in st.session_state["advisor_list"][:-1]:
        img_container.image(advisor["logo"],width=img_size)
        res=st.session_state["individual_chain"].run(
            {"name":advisor["name"],
            "personality":advisor["personality"],
            "work":advisor["work"],
            "human_input":st.session_state["human_input"],
            "chat_history":current_memory,
            "length":st.session_state["answer_length"]}
        )
        st.session_state["summary_chain"].memory.chat_memory.add_ai_message(res)
        st.session_state["history"].append(f"> {res}")
        markdown_container.markdown(f'{res}')

    advisor=st.session_state["advisor_list"][-1]
    img_container.image(advisor["logo"],width=img_size)
    res=st.session_state["summary_chain"].run(
        {"name":advisor["name"],
        "personality":advisor["personality"],
        "work":advisor["work"],
        "human_input":st.session_state["human_input"],
        "length":st.session_state["answer_length"]+50
        },
    )
    st.session_state["history"].append(res)
    markdown_container.markdown(f"{res}")
    return

def set_chatbox(c,audio):
    transcript=""
    if len(audio) > 0:
        with st.spinner("识别中..."):
            transcript = transcribe(audio.tobytes())

    human_input=c.text_area("主公请提问", value=transcript)
    ask_button=c.button("提问")
    col1,col2=c.columns([1,6])
    current_img=col1.empty()
    current_advice=col2.empty()
    st.session_state["stream_box"]=current_advice
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