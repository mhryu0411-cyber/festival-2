import os
import time
from datetime import datetime
import pandas as pd
import pytz
import streamlit as st

# 한국 시간대(KST) 정의
KST = pytz.timezone("Asia/Seoul")

# 페이지 기본 설정 (Wide 레이아웃)
st.set_page_config(
    page_title="세계 축제 이미지 분석", page_icon="🌍", layout="wide"
)

# 상단 여백, 스크롤바 숨김, 모둠별 하얀색 직사각형 카드 디자인 CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

    html, body, [class*="css"], [class*="st-"], button, input, textarea, div, span, h1, h2, h3, h4, p {
        font-family: 'Nanum Gothic', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* 상단바 여백 넉넉하게 확보 */
    .block-container {
        padding-top: 2.8rem !important;
        padding-bottom: 2.5rem !important;
        padding-left: 1.5rem !important;
        padding-right: 1.5rem !important;
    }

    /* 아주 은은하고 투명한 파스텔 배경 */
    .stApp {
        background: linear-gradient(135deg, rgba(224, 195, 252, 0.15) 0%, rgba(142, 197, 252, 0.15) 50%, rgba(251, 194, 235, 0.15) 100%) !important;
        background-attachment: fixed !important;
    }

    /* Streamlit 아이콘 텍스트 유출 차단 */
    [data-testid="stIconMaterial"], 
    .material-symbols-outlined,
    span[data-testid="stHeaderActionElements"] {
        font-size: 0px !important;
        visibility: hidden !important;
        display: none !important;
    }

    /* 설정 아이콘 버튼 투명 처리 */
    [data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* 모바일 및 PC에서 1~4모둠 가로 스크롤 (스크롤바 숨김) */
    [data-testid="stHorizontalBlock"] {
        display: flex !important;
        flex-direction: row !important;
        flex-wrap: nowrap !important;
        overflow-x: auto !important;
        gap: 16px !important;
        padding-bottom: 16px !important;
        scroll-snap-type: x mandatory;
        -webkit-overflow-scrolling: touch;
        scrollbar-width: none;
    }

    [data-testid="stHorizontalBlock"]::-webkit-scrollbar {
        display: none;
    }

    /* 각 모둠 영역을 선명한 하얀색 직사각형 카드로 독립 분리 */
    [data-testid="column"] {
        flex: 0 0 85vw !important;
        max-width: 340px !important;
        min-width: 290px !important;
        background-color: #ffffff !important;
        border-radius: 20px !important;
        padding: 18px !important;
        box-shadow: 0 8px 24px rgba(0, 0, 0, 0.08) !important;
        border: 1px solid #e2e8f0 !important;
        scroll-snap-align: center;
    }

    /* 모바일 가로 스크롤 유도 안내 뱃지 스타일 */
    .scroll-guide {
        background: rgba(99, 102, 241, 0.1);
        color: #4f46e5;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 0.85rem;
        font-weight: 700;
        text-align: center;
        margin-bottom: 15px;
        display: inline-block;
        border: 1px solid rgba(99, 102, 241, 0.2);
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# 데이터 저장을 위한 폴더 및 CSV 경로
UPLOAD_DIR = "uploads"
CSV_FILE = "metadata.csv"

if not os.path.exists(UPLOAD_DIR):
  os.makedirs(UPLOAD_DIR)


def load_data():
  if os.path.exists(CSV_FILE):
    df = pd.read_csv(CSV_FILE)
    if "group" not in df.columns:
      df["group"] = "1모둠"
    return df
  else:
    return pd.DataFrame(columns=["group", "filename", "timestamp"])


def save_post(group_name, file_buffer):
  file_extension = "jpg"
  if hasattr(file_buffer, "name") and "." in file_buffer.name:
    file_extension = file_buffer.name.split(".")[-1]

  safe_filename = f"{os.urandom(6).hex()}.{file_extension}"
  file_path = os.path.join(UPLOAD_DIR, safe_filename)

  progress_text = "업로드 중입니다.. 🥳"
  progress_bar = st.progress(0, text=progress_text)

  for percent_complete in range(1, 101, 20):
    time.sleep(0.05)
    progress_bar.progress(
        percent_complete, text=f"{progress_text} ({percent_complete}%)"
    )

  with open(file_path, "wb") as f:
    f.write(file_buffer.getbuffer())

  progress_bar.progress(100, text=f"{progress_text} (100%)")
  time.sleep(0.2)
  progress_bar.empty()

  kst_now = datetime.now(KST).strftime("%H:%M:%S")

  new_row = pd.DataFrame(
      [{
          "group": group_name,
          "filename": safe_filename,
          "timestamp": kst_now,
      }]
  )

  st.session_state.data = pd.concat(
      [st.session_state.data, new_row], ignore_index=True
  )
  st.session_state.data.to_csv(CSV_FILE, index=False)


# 세션 상태 초기화
if "data" not in st.session_state:
  st.session_state.data = load_data()

if "is_teacher" not in st.session_state:
  st.session_state.is_teacher = False

if "fullscreen_img" not in st.session_state:
  st.session_state.fullscreen_img = None

for g in ["1모둠", "2모둠", "3모둠", "4모둠"]:
  if f"pending_file_{g}" not in st.session_state:
    st.session_state[f"pending_file_{g}"] = None


# --- 전체 화면 모달 (사진 클릭 시 크게 보기) ---
if st.session_state.fullscreen_img:
  with st.container():
    st.image(st.session_state.fullscreen_img, use_container_width=True)
    if st.button("❌ 닫기 (화면 복귀)", use_container_width=True, type="primary"):
      st.session_state.fullscreen_img = None
      st.rerun()
  st.stop()


# --- 상단 타이틀 ---
col_head, col_auth = st.columns([12, 1])

with col_head:
  st.markdown(
      "<h1 style='color: #1e293b; font-weight: 800; font-size: 1.8rem;"
      " margin-top: 10px; margin-bottom: 5px;'>🌍 세계 축제 이미지 분석</h1>",
      unsafe_allow_html=True,
  )

with col_auth:
  with st.popover("⚙️"):
    if not st.session_state.is_teacher:
      pw_input = st.text_input(
          "",
          type="password",
          placeholder="비밀번호 입력",
          key="teacher_pw_input",
          label_visibility="collapsed",
      )
      if pw_input == "1232":
        st.session_state.is_teacher = True
        st.success("확인되었습니다.")
        st.rerun()
      elif pw_input and pw_input != "1232":
        st.error("오류")
    else:
      st.caption("교사 모드 사용 중")
      if st.button("종료", use_container_width=True):
        st.session_state.is_teacher = False
        st.rerun()

if st.session_state.is_teacher:
  st.info("🔓 [교사 모드 활성화됨] 개별 사진 삭제가 가능합니다.")

# 직관적인 가로 스크롤 안내 뱃지
st.markdown(
    '<div style="text-align: center; margin: 15px 0 20px 0;"><span'
    ' class="scroll-guide">👉 손가락으로 옆으로 밀어서 2~4모둠을 확인하세요!</span></div>',
    unsafe_allow_html=True,
)

# --- 패들렛 스타일 1~4모둠 가로 스크롤 보드 ---
st.session_state.data = load_data()
df = st.session_state.data

groups = ["1모둠", "2모둠", "3모둠", "4모둠"]
cols = st.columns(4)

for idx, group_name in enumerate(groups):
  with cols[idx]:
    st.markdown(
        f"<h3 style='font-weight: 800; color: #1e293b; font-size: 1.2rem;"
        f" margin-top: 0; margin-bottom: 0.8rem; text-align: center;'>📌"
        f" {group_name}</h3>",
        unsafe_allow_html=True,
    )

    # 모둠별 사진 업로드 팝오버
    with st.popover(f"➕ 사진 올리기", use_container_width=True):
      st.markdown(
          f"<p style='font-weight: 800; font-size: 13px; color: #1e293b;"
          f" margin-bottom: 8px;'>📸 {group_name} 사진 첨부</p>",
          unsafe_allow_html=True,
      )

      # 1단계: 사진 파일 선택
      uploaded_file = st.file_uploader(
          "사진 선택 또는 촬영",
          type=["jpg", "jpeg", "png"],
          key=f"uploader_{group_name}",
          label_visibility="collapsed",
      )

      if uploaded_file is not None:
        st.session_state[f"pending_file_{group_name}"] = uploaded_file

      # 2단계: 업로드 대기 중인 파일이 있으면 "이 사진을 올리시겠습니까?" 확인 창 표시
      if st.session_state[f"pending_file_{group_name}"] is not None:
        pending = st.session_state[f"pending_file_{group_name}"]
        st.warning("이 사진을 올리시겠습니까?")
        st.image(pending, use_container_width=True)

        col_yes, col_no = st.columns(2)
        with col_yes:
          if st.button(
              "✅ 올리기", key=f"confirm_{group_name}", use_container_width=True
          ):
            save_post(group_name, pending)
            st.session_state[f"pending_file_{group_name}"] = None
            st.success("등록 완료!")
            st.rerun()
        with col_no:
          if st.button(
              "❌ 취소", key=f"cancel_{group_name}", use_container_width=True
          ):
            st.session_state[f"pending_file_{group_name}"] = None
            st.rerun()

    st.write("")

    # 해당 모둠 게시물 카드 목록 (최신순)
    group_df = df[df["group"] == group_name].iloc[::-1].reset_index(drop=True)

    if group_df.empty:
      st.markdown(
          "<p style='text-align: center; color: #94a3b8; font-size: 0.85rem;"
          " margin-top: 2rem;'>제출된 사진이 없습니다.</p>",
          unsafe_allow_html=True,
      )
    else:
      for i, row in group_df.iterrows():
        with st.container(border=True):
          file_path = os.path.join(UPLOAD_DIR, row["filename"])

          if os.path.exists(file_path):
            # 돋보기 버튼 없이, 사진 자체를 누르면 전체화면 모달로 확대되도록 버튼으로 이미지 감싸기
            if st.button("사진 크게 보기", key=f"zoom_{row['filename']}"):
              st.session_state.fullscreen_img = file_path
              st.rerun()

            st.image(file_path, use_container_width=True)
          else:
            st.error("파일 없음")

          st.caption(f"시간: {row['timestamp']}")

          if st.session_state.is_teacher:
            if st.button("🗑️ 삭제", key=f"del_{row['filename']}"):
              if os.path.exists(file_path):
                os.remove(file_path)
              st.session_state.data = st.session_state.data[
                  st.session_state.data["filename"] != row["filename"]
              ]
              st.session_state.data.to_csv(CSV_FILE, index=False)
              st.success("삭제됨")
              st.rerun()
