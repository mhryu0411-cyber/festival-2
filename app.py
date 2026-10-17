import os
import time
import pandas as pd
import streamlit as st

# 페이지 기본 설정
st.set_page_config(
    page_title="세계 축제 이미지 분석", page_icon="🌍", layout="wide"
)

# 나눔고딕 최우선 적용 & 초극미세 투명 파스텔 배경 CSS
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Nanum+Gothic:wght@400;700;800&display=swap');

    html, body, [class*="css"], [class*="st-"], button, input, textarea, div, span, h1, h2, h3, h4, p {
        font-family: 'Nanum Gothic', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* 아주 은은하고 투명도가 대폭 높아진 파스텔 배경 */
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

    /* ⚙️ 아이콘 및 사진 팝오버 투명 스타일링 */
    [data-testid="stPopover"] button {
        border: none !important;
        background: transparent !important;
        box-shadow: none !important;
        padding: 0 !important;
    }

    /* 깔끔한 백색 패들렛 카드 */
    div[data-testid="stVerticalBlock"] > div[data-testid="stContainer"] {
        background-color: rgba(255, 255, 255, 0.95) !important;
        padding: 0.8rem !important;
        border-radius: 14px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03) !important;
        border: 1px solid rgba(226, 232, 240, 0.8) !important;
        margin-bottom: 0.8rem !important;
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

  # 업로드 로딩 진행률 표시 (0% ~ 100%)
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


def delete_all_posts():
  if os.path.exists(UPLOAD_DIR):
    for f in os.listdir(UPLOAD_DIR):
      file_p = os.path.join(UPLOAD_DIR, f)
      if os.path.isfile(file_p):
        os.remove(file_p)
  empty_df = pd.DataFrame(columns=["group", "filename", "timestamp"])
  empty_df.to_csv(CSV_FILE, index=False)
  st.session_state.data = empty_df


# 세션 상태 초기화
if "data" not in st.session_state:
  st.session_state.data = load_data()

if "is_teacher" not in st.session_state:
  st.session_state.is_teacher = False

# 모둠별 카메라/앨범 및 마지막 처리 파일 중복 방지 키
for g in ["1모둠", "2모둠", "3모둠", "4모둠"]:
  if f"mode_{g}" not in st.session_state:
    st.session_state[f"mode_{g}"] = "cam"
  if f"last_processed_{g}" not in st.session_state:
    st.session_state[f"last_processed_{g}"] = None


# --- 상단 타이틀 ---
col_head, col_auth = st.columns([12, 1])

with col_head:
  st.markdown(
      "<h1 style='color: #1e293b; font-weight: 800; font-size: 1.8rem;"
      " margin-bottom: 0px;'>🌍 세계 축제 이미지 분석</h1>",
      unsafe_allow_html=True,
  )
  st.markdown(
      "<p style='color: #64748b; font-size: 0.9rem; font-weight: 700; margin-top:"
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

# 교사 모드용 배너 및 전체 삭제 버튼
if st.session_state.is_teacher:
  col_info, col_del_all = st.columns([8, 2])
  with col_info:
    st.info("🔓 [교사 모드 활성화됨] 사진 삭제 및 관리가 가능합니다.")
  with col_del_all:
    if st.button("🗑️ 전체 사진 삭제", type="primary", use_container_width=True):
      delete_all_posts()
      st.success("모든 사진이 완전히 삭제되었습니다.")
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

    # 모둠별 사진 업로드 팝오버
    with st.popover(f"➕ {group_name} 사진 올리기", use_container_width=True):
      st.markdown(
          f"<p style='font-weight: 800; font-size: 14px; color: #1e293b;"
          f" margin-bottom: 10px;'>📸 {group_name} 사진 첨부</p>",
          unsafe_allow_html=True,
      )

      # [📷 카메라] / [📁 앨범] 버튼 선택
      c1, c2 = st.columns(2)
      with c1:
        if st.button(
            "📷 카메라", key=f"btn_cam_{group_name}", use_container_width=True
        ):
          st.session_state[f"mode_{group_name}"] = "cam"
          st.rerun()
      with c2:
        if st.button(
            "📁 앨범", key=f"btn_file_{group_name}", use_container_width=True
        ):
          st.session_state[f"mode_{group_name}"] = "file"
          st.rerun()

      uploaded_file = None
      if st.session_state[f"mode_{group_name}"] == "cam":
        uploaded_file = st.camera_input(
            "촬영하기", key=f"cam_{group_name}", label_visibility="collapsed"
        )
      else:
        uploaded_file = st.file_uploader(
            "사진 선택",
            type=["jpg", "jpeg", "png"],
            key=f"file_{group_name}",
            label_visibility="collapsed",
        )

      # 중복 저장 방지 처리 및 1회만 정상 제출
      if uploaded_file is not None:
        file_id = f"{uploaded_file.name}_{uploaded_file.size}"
        if st.session_state[f"last_processed_{group_name}"] != file_id:
          st.session_state[f"last_processed_{group_name}"] = file_id
          save_post(group_name, uploaded_file)
          st.success("등록 완료!")
          st.rerun()

    st.write("")

    # 해당 모둠 게시물 카드 (최신순)
    group_df = df[df["group"] == group_name].iloc[::-1].reset_index(drop=True)

    if group_df.empty:
      st.caption("제출된 사진이 없습니다.")
    else:
      for i, row in group_df.iterrows():
        with st.container(border=True):
          file_path = os.path.join(UPLOAD_DIR, row["filename"])

          if os.path.exists(file_path):
            # 사진 자체를 팝오버로 감싸서 클릭하면 팝오버 형태 카드로 크게 노출
            with st.popover("🔍 사진 크게 보기 (클릭)", use_container_width=True):
              st.markdown(f"**📌 [{row['group']}] 제출 사진**")
              st.image(file_path, use_container_width=True)

            st.image(file_path, use_container_width=True)
          else:
            st.error("이미지를 찾을 수 없습니다.")

          st.caption(f"시간: {row['timestamp']}")

          # 교사 모드일 때 개별 삭제 버튼 표시
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
