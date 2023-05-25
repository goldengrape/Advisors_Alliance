from typing import Any, Dict, Optional
from uuid import UUID
from langchain import OpenAI, LLMChain, PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chat_models import ChatOpenAI

# llm = ChatOpenAI(temperature=0.9)

# 定义军师
def init_advisor(advisor_order=[0,1,2,3,4,5]):
    six_hats_advisor_list = [
        {
            "color": "White",
            "name": "荀彧",
            "zi": "文若",
            "character": "客观、冷静",
            "logo": "img/xy.png",
            "personality": "You focus on facts and data. You approach problems objectively, ignoring personal biases.",
            "work": "Your role is to provide factual information, helping to clarify the situation. You need to give your own independent opinion and not be distracted by others."
        },
        {
            "color": "Green",
            "name":"周瑜",
            "zi": "公瑾",
            "character": "创新、发散",
            "logo": "img/zy.png",
            "personality": "You are creative and innovative. You think outside the box and seek new solutions.",
            "work": "Your role is to encourage creative thinking, fostering innovation and discovery.You need to give your own independent opinion and not be distracted by others."
        },
        {
            "color": "Yellow",
            "name":"徐庶",
            "zi": "元直",
            "character": "乐观、积极",
            "logo": "img/xs.png",
            "personality": "You are optimistic and see opportunities. You focus on the positive aspects.",
            "work": "Your role is to identify opportunities and positive outcomes, promoting a positive outlook.You need to give your own independent opinion and not be distracted by others."
        },
        {
            "color": "Black",
            "name":"司马懿",
            "zi": "仲达",
            "character": "谨慎、审慎",
            "logo": "img/smy.png",
            "personality": "You are cautious and critical. You see potential risks and issues others might miss.",
            "work": "Your role is to identify possible problems, helping to avoid mistakes.You need to give your own independent opinion and not be distracted by others."
        },
        {
            "color": "Red",
            "name":"鲁肃",
            "zi": "子敬",
            "character": "感性、直觉",
            "logo": "img/ls.png",
            "personality": "You rely on intuition and emotions. You empathize with others and value feelings.",
            "work": "Your role is to express emotions and intuitions, offering a different perspective.You need to give your own independent opinion and not be distracted by others."
        },
        
        {
            "color": "Blue",
            "name":"诸葛亮",
            "zi": "孔明",
            "character": "智慧、控制",
            "logo": "img/zgl.png",
            "personality": "You are an organizer and leader. You guide the thinking process and coordinate the use of other hats.",
            "work": """Your role is to manage the thinking process, ensuring focus and organization. You need to give your own independent opinion and also need to consider the opinions of other 军师, whose opinions are recorded in the MEMORY.
            """
        }
    ]
    # 1、陈述问题事实（白帽）
    # 2、提出如何解决问题的建议（绿帽）
    # 3、评估建议的优缺点：列举优点（黄帽）；列举缺点（黑帽）
    # 4、对各项选择方案进行直觉判断（红帽）
    # 5、总结陈述，得出方案（蓝帽）
    six_hats_advisor_list=[six_hats_advisor_list[i] for i in advisor_order]
    return six_hats_advisor_list

# 定义prompt
def init_prompt():
    six_hats_template = """
    You are {name}, the famous strategist during the Three Kingdoms period. 
    You refer to me as "主公". 
    Your answer should start with "臣{name}以为：".
    {personality}
    {work}
    You should answer in {length} words.
    ```MEMORY:
    {chat_history}
    ```
    ```current chat:
    主公: {human_input}
    {name}:
    ```
    """

    six_hats_prompt = PromptTemplate(
        input_variables=["name","personality","work","human_input","chat_history","length"], 
        template=six_hats_template
    )
    return six_hats_prompt

# 定义memory
def init_memory():
    sum_memory = ConversationBufferMemory(
        memory_key="chat_history",
        input_key="human_input",
        ai_prefix="军师",
        human_prefix="主公",
        )
    return sum_memory

# 定义llmchain
def init_chain(llm):
    prompt=init_prompt()
    memory=init_memory()
    individual_chain = LLMChain(llm=llm, 
                    prompt=prompt, 
    )
    summary_chain= LLMChain(llm=llm,
                        prompt=prompt,
                        memory=memory,)
    return individual_chain, summary_chain

def get_advice(human_input,advisor_list,individual_chain,sum_chain):
    current_memory="\n".join([message.content.strip() for message in sum_chain.memory.chat_memory.messages])
    sum_chain.memory.chat_memory.add_user_message(human_input)
    advice_list=[]
    for advisor in advisor_list[:-1]:
        res=individual_chain.run(
            {"name":advisor["name"],
            "personality":advisor["personality"],
            "work":advisor["work"],
            "human_input":human_input,
            "chat_history":current_memory},
        )
        sum_chain.memory.chat_memory.add_ai_message(res)
        advice_list.append(res)
        print(res)
    advisor=advisor_list[-1]
    res=sum_chain.run(
        {"name":advisor["name"],
        "personality":advisor["personality"],
        "work":advisor["work"],
        "human_input":human_input,
        },
    )
    print(res)
    advice_list.append(res)
    return advice_list

import tempfile
from audiorecorder import audiorecorder
import openai

def transcribe(audio_bytes):
    with tempfile.NamedTemporaryFile(suffix=".wav") as tmpfile:
        tmpfile.write(audio_bytes)
        tmpfile.seek(0)
        return openai.Audio.transcribe(
            "whisper-1",
            tmpfile,
            temperature=0.2,
            prompt="这是中文语音输入",
        )["text"]