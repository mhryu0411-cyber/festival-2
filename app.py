import os
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="세계 축제 이미지 분석", page_icon="🌍", layout="wide"
)

# 커스텀 CSS: 확실한 나눔고딕, 감성 파스텔 그라데이션 배경, expand_more 숨김, 콤팩트 UI
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

    /* 모든 요소에 나눔고딕 최우선 적용 */
    html, body, [class*="css"], [class*="st-"], button, input, textarea, div, span, h1, h2, h3, h4, p {
        font-family: 'Nanum Gothic', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* 화사하고 예쁜 파스텔톤 그라데이션 배경 (연보라 & 스카이블루 & 연핑크 믹스) */
    .stApp {
        background: linear-gradient(120deg, #e0c3fc 0%, #8ec5fc 50%, #fbc2eb 100%) !important;
        background-attachment: fixed !important;
    }

    /* Streamlit expand_more 글자 및 유출 아이콘 완전 차단 */
    [data-testid="stIconMaterial"], 
    .material-symbols-outlined,
    span[data-testid="stHeaderActionElements"] {
        font-size: 0px !important;
        visibility: hidden !important;
        display: none !important;
    }

    /* ⚙️ 팝오버 버튼 투명화 및 깔끔 처리 */
    [data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
        font-size: 1.2rem !important;
    }

    /* 패들렛 카드 스타일 (약간의 투명도와 그림자로 예쁜 느낌 강조) */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: rgba(255, 255, 255, 0.88) !important;
        backdrop-filter: blur(8px);
        padding: 0.8rem !important;
        border-radius: 16px !important;
        box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06) !important;
        border: 1px solid rgba(255, 255, 255, 0.6) !important;
        margin-bottom: 0.8rem !important;
    }

    /* 직사각형 업로드 선택 카드 스타일 (더 콤팩트하게) */
    .choice-card-cam {
        background-color: #e0e7ff;
        border: 2px dashed #6366f1;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        color: #4338ca;
        font-weight: 700;
        font-size: 13px;
        margin-bottom: 4px;
    }
    .choice-card-file {
        background-color: #f3f4f6;
        border: 2px dashed #9ca3af;
        border-radius: 10px;
        padding: 8px;
        text-align: center;
        color: #374151;
        font-weight: 700;
        font-size: 13px;
        margin-bottom: 4px;
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

  with open(file_path, "wb") as f:
    f.write(file_buffer.getbuffer())

  new_row = pd.DataFrame(
      [{
          "group": group_name,
          "filename": safe_filename,
          "timestamp": pd.Timestamp.now().strftime("%H:%M:%S"),
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

if "zoomed_image" not in st.session_state:
  st.session_state.zoomed_image = None


# --- 상단 타이틀 및 티 안 나는 교사 인증 (타이틀 제거함) ---
col_head, col_auth = st.columns([12, 1])

with col_head:
  st.markdown(
      "<h1 style='color: #1e293b; font-weight: 800; font-size: 1.8rem;"
      " margin-bottom: 0px;'>🌍 세계 축제 이미지 분석</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #475569; font-size: 0.9rem; font-weight: 700; margin-top:"
      " -4px;'>모둠별 학습지 공유 보드</p>",
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
  st.info("🔓 [교사 모드 활성화됨] 사진을 클릭하여 크게 보거나 삭제할 수 있습니다.")

st.divider()

# --- 사진 크게 보기 전용 모달 박스 ---
if st.session_state.zoomed_image:
  with st.container(border=True):
    col_img, col_close = st.columns([5, 1])
    with col_img:
      st.markdown("### 🔍 사진 상세 보기")
      st.image(
          st.session_state.zoomed_image,
          caption=st.session_state.get("zoomed_info", ""),
          use_container_width=True,
      )
    with col_close:
      if st.button("❌ 닫기", use_container_width=True):
        st.session_state.zoomed_image = None
        st.rerun()
  st.divider()

# --- 패들렛 스타일 1~4모둠 보드 ---
st.session_state.data = load_data()
df = st.session_state.data

groups = ["1모둠", "2모둠", "3모둠", "4모둠"]
cols = st.columns(4)

for idx, group_name in enumerate(groups):
  with cols[idx]:
    st.markdown(
        f"<h3 style='font-weight: 800; color: #1e293b; font-size: 1.2rem;"
        f" margin-bottom: 0.5rem;'>📌 {group_name}</h3>",
        unsafe_allow_html=True,
    )

    # 모둠별 사진 업로드 소형 팝오버 (작은 모달 스타일)
    with st.popover(f"➕ {group_name} 사진 올리기", use_container_width=True):
      st.markdown(
          f"<p style='font-weight: 800; font-size: 14px; color: #1e293b;"
          f" margin-bottom: 8px;'>📸 {group_name} 사진 첨부</p>",
          unsafe_allow_html=True,
      )

      # 콤팩트한 2개 선택 카드
      col_btn1, col_btn2 = st.columns(2)
      cam_active = False
      file_active = False

      with col_btn1:
        st.markdown(
            '<div class="choice-card-cam">📷 카메라</div>',
            unsafe_allow_html=True,
        )

      with col_btn2:
        st.markdown(
            '<div class="choice-card-file">📁 앨범</div>',
            unsafe_allow_html=True,
        )

      tab_choice = st.radio(
          "첨부 방식",
          ["📷 카메라 촬영", "📁 파일 / 앨범 선택"],
          key=f"radio_{group_name}",
          label_visibility="collapsed",
      )

      uploaded_file = None
      if "카메라" in tab_choice:
        uploaded_file = st.camera_input(
            "촬영하기", key=f"cam_input_{group_name}"
        )
      else:
        uploaded_file = st.file_uploader(
            "사진 선택",
            type=["jpg", "jpeg", "png"],
            key=f"file_input_{group_name}",
        )

      if uploaded_file is not None:
        save_post(group_name, uploaded_file)
        st.success("등록 완료!")
        st.rerun()

    st.write("")

    # 해당 모둠 게시물 카드 리스트 (최신순)
    group_df = df[df["group"] == group_name].iloc[::-1].reset_index(drop=True)

    if group_df.empty:
      st.caption("제출된 사진이 없습니다.")
    else:
      for i, row in group_df.iterrows():
        with st.container(border=True):
          file_path = os.path.join(UPLOAD_DIR, row["filename"])

          if os.path.exists(file_path):
            st.image(file_path, use_container_width=True)

            if st.button("🔍 크게 보기", key=f"zoom_{row['filename']}"):
              st.session_state.zoomed_image = file_path
              st.session_state.zoomed_info = f"[{row['group']}] 제출된 사진"
              st.rerun()
          else:
            st.error("이미지를 찾을 수 없습니다.")

          st.caption(f"시간: {row['timestamp']}")

          if st.session_state.is_teacher:
            if st.button("🗑️ 삭제", key=f"del_{row['filename']}"):
              if os.path.exists(file_path):
                os.remove(file_path)
              st.session_state.data = st.session_state.data[
                  st.session_state.data["filename"] != row["filename"]
              ]
              st.session_state.data.to_csv(CSV_FILE, index=False)
              st.success("삭제되었습니다.")
              st.rerun()
