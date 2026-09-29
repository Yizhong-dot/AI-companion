import streamlit as st
import os
from openai import OpenAI
import datetime
import json

IS_CLOUD=os.getenv("STREAMLIT_SHARING","")!=""
st.set_page_config(
    page_title="AI智能伴侣",
    page_icon="🤖",
    layout="wide",
    #控制的是侧边栏的状态
    initial_sidebar_state="expanded",
    menu_items={}
)
#生成绘画标识
def generate_session_id():
    return datetime.datetime.now().strftime("%Y-%m-%d %H_%M_%S")
#保存会话信息的函数
def save_session():
    if IS_CLOUD:
        return
    current_dir = os.path.dirname(os.path.abspath(__file__))
    sessions_dir = os.path.join(current_dir, "sessions")
    os.makedirs(sessions_dir, exist_ok=True)
    if not st.session_state.get('current_session'):
        st.session_state.current_session = generate_session_id()

    session_data = {
        "current_session": st.session_state.current_session,
        "messages": st.session_state.messages,
        "nick_name": st.session_state.get("nick_name", ""),
        "nature": st.session_state.get("nature", "")
    }
    file_path = os.path.join(sessions_dir, f"{st.session_state.current_session}.json")

    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(session_data, f, ensure_ascii=False, indent=2)
        print(f"✅ 成功保存会话到: {file_path}")
        st.toast(f"会话已保存: {st.session_state.current_session}.json")
    except Exception as e:
        print(f"❌ 保存失败: {e}")
        st.error(f"保存失败: {e}")
#加载所有会话列表信息
def load_sessions():
    if IS_CLOUD:
        return []
    session_list = []
    if os.path.exists("sessions"):
        for file_name in os.listdir("sessions"):
            if file_name.endswith(".json"):
                session_list.append(file_name[:-5])
    return sorted(session_list, reverse=True)#排序降序排序
#加载指定会话数据
def load_session(session_id):
    if IS_CLOUD:
        return
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            with open(f"sessions/{session_id}.json", "r", encoding="utf-8") as f:
                session_data = json.load(f)
                st.session_state.current_session = session_data["current_session"]
                st.session_state.messages = session_data["messages"]
                st.session_state.nick_name = session_data["nick_name"]
                st.session_state.nature = session_data["nature"]
    except Exception as e:
        print(f"❌ 加载会话失败: {e}")
        st.error(f"加载会话失败: {e}")
#删除会话信息函数
def delete_session(session_id):
    if IS_CLOUD:
        return
    try:
        if os.path.exists(f"sessions/{session_id}.json"):
            os.remove(f"sessions/{session_id}.json")
            print(f"✅ 删除会话: {session_id}.json")
            st.toast(f"删除会话: {session_id}.json")
            if session_id == st.session_state.current_session:
                st.session_state.messages = []
                st.session_state.current_session = generate_session_id()
    except Exception as e:
        print(f"❌ 删除会话失败: {e}")
        st.error(f"删除会话失败: {e}")

# 大标题
st.title("AI智能伴侣")

#logo
st.logo("resources/logo.webp")

#初始化聊天信息
if 'messages' not in st.session_state:
    st.session_state.messages = []
#昵称
if 'nick_name' not in st.session_state:
    st.session_state.nick_name = ""
#性格
if 'nature' not in st.session_state:
    st.session_state.nature = ""
#会话标识
if 'session_id' not in st.session_state:
    st.session_state.session_id = ""
#当前会话
if 'current_session' not in st.session_state or not st.session_state.current_session:
    st.session_state.current_session = generate_session_id()


#系统提示词
system_prompt =f"""
        你叫{st.session_state.nick_name}，现在是用户的真实伴侣，请完全代入伴侣角色。
        规则：
            1．每次只回1条消息
            2．禁止任何场景或状态描述性文字
            3．匹配用户的语言
            4．回复简短，像微信聊天一样
            5．有需要的话可以用❤️🌸等emoji表情
            6．用符合伴侣性格的方式对话
            7．回复的内容，要充分体现伴侣的性格特征
         
        伴侣性格：
            {st.session_state.nature}
        你必须严格遵守上述规则来回复用户。
"""

st.text(f"会话名称: {st.session_state.current_session}")
#展示聊天信息
for message in st.session_state.messages:
    if message["role"] == "user":
        st.chat_message("user").write(message["content"])
    else:
        st.chat_message("assistant").write(message["content"])


#创建与ai大模型交互的客户端对象(DEEPSEEK_API_KEY 环境变量的名字,值就是deepseek的API_KEY的)
client = OpenAI(api_key=os.environ.get('DEEPSEEK_API_KEY'),base_url="https://api.deepseek.com")

#左侧的侧边栏 - with:streamlit里的上下文管理器
with st.sidebar:
    #会话信息
    st.subheader("AI控制面板")
    #新建会话按钮
    if st.button("新建会话",icon="🚀",width="stretch"):
        if st.session_state.messages:
            save_session()

    #创建新的绘画
        new_id = generate_session_id()
        st.session_state.current_session = new_id
        st.session_state.messages = []
        st.rerun()
    #会画历史
    st.text("会话历史")
    session_list = load_sessions()
    for session in session_list:
        col1,col2 = st.columns([4,1])
        with col1:
            if st.button(session,icon="📁",key=f"load_{session}",width="stretch",type="primary" if session == st.session_state.current_session else "secondary"):
                load_session(session)
                st.rerun()


        with col2:
            if st.button("",icon = "🗑️",key=f"delete_{session}",width="stretch"):
                delete_session(session)
                st.rerun()
    #分割线
    st.divider()

    #伴侣信息
    st.subheader("伴侣信息")

    #昵称输入框
    nick_name = st.text_input("呢称",placeholder="请输入呢称:",value=st.session_state.nick_name)
    if nick_name:
        st.session_state.nick_name = nick_name

    #性格输入框
    nature = st.text_area("性格",placeholder="请输入性格:",value=st.session_state.nature)
    if nature:
        st.session_state.nature = nature

#输入框
prompt = st.chat_input("请输入您要问的问题")
if prompt:
    st.chat_message("user").write(prompt)
    print("-----------> 调用AI大模型,提示词", prompt)
    #保存用户问题
    st.session_state.messages.append({"role": "user", "content": prompt})

    #调用AI大模型
    # 与AI大模型进行交互(参数)
    response = client.chat.completions.create(
        model="deepseek-flash",
        messages=[
            {"role": "system", "content": system_prompt},
            *st.session_state.messages,
        ],
        stream=False
    )
    # 输出大模型返回的结果(非流式输出)
    #     print("<----------- 大模型返回结果", response.choices[0].message.content)
    st.chat_message("assistant").write(response.choices[0].message.content)
        # save_session()

    #流式输出返回结果
        # response_message = st.empty()
        # full_response = ""
        # for chunk in response:
        #     if chunk.choices[0].delta.content is not None:
        #         content = chunk.choices[0].delta.content
        #         full_response += content
        #         response_message.chat_message("assistant").write(full_response)
        # st.session_state.messages.append({"role": "assistant", "content": full_response})
        # save_session()
