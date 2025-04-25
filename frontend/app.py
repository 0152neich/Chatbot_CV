import streamlit as st
import requests
import time

st.set_page_config(page_title="Chatbot CV", layout="wide")

def init_session_state():
    if "candidate_name" not in st.session_state:
        st.session_state.candidate_name = ""
    if "name_confirmed" not in st.session_state:
        st.session_state.name_confirmed = False

init_session_state()

st.sidebar.title("📁 Upload CV")
uploaded_file = st.sidebar.file_uploader("Chọn một file", type=["pdf", "docx"])

if uploaded_file:
    st.sidebar.success(f"Đã tải lên: {uploaded_file.name}")

st.sidebar.subheader("👤 Nhập tên ứng viên")
name_input = st.sidebar.text_input(
    "Tên ứng viên",
    value="",
    placeholder="VD: Đào Duy Chiến",
    key="name_input",
    help="Nhập tên ứng viên để hỏi thông tin."
)

if st.sidebar.button("OK"):
    if name_input.strip():
        st.session_state.candidate_name = name_input.strip()
        st.session_state.name_confirmed = True
        st.sidebar.success(f"Tên ứng viên đã xác nhận: {st.session_state.candidate_name}")
    else:
        st.sidebar.warning("⚠️ Vui lòng nhập tên ứng viên.")

if st.session_state.name_confirmed and st.session_state.candidate_name:
    st.sidebar.info(f"Ứng viên hiện tại: **{st.session_state.candidate_name}**")

# ========== MAIN PAGE:  ============
st.title("💬 Chatbot hỏi đáp")

user_question = st.text_input(
    "Nhập câu hỏi:",
    placeholder="VD: Kinh nghiệm làm việc của ứng viên là gì?"
)

def fake_stream_response(answer, placeholder):
    words = answer.split()
    full_answer = ""
    for word in words:
        full_answer += word + " "
        placeholder.markdown(full_answer + " ▌")
        time.sleep(0.05)
    placeholder.markdown(full_answer)
    return full_answer

if st.button("Gửi"):
    if not user_question:
        st.warning("⚠️ Vui lòng nhập câu hỏi.")
    elif not st.session_state.name_confirmed or not st.session_state.candidate_name:
        st.warning("⚠️ Vui lòng nhập và xác nhận tên ứng viên.")
    else:
        api_url = "http://localhost:5000/v1/chatbot"
        payload = {
            "query": user_question,
            "user_name": st.session_state.candidate_name
        }

        try:
            st.success("🤖 Bot đang trả lời:")
            placeholder = st.empty()

            response = requests.post(api_url, json=payload, timeout=30)

            if response.status_code == 200:
                data = response.json()
                answer = data.get("info", {}).get("response", "Không có phản hồi.")
                answer = fake_stream_response(answer, placeholder)
            else:
                st.error(f"❌ Lỗi server: {response.status_code} - {response.text}")

        except Exception as e:
            st.error(f"⚠️ Không kết nối được API: {e}")