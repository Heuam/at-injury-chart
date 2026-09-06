from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import streamlit as st

# ====================================================
# 1. 페이지 환경 & 반응형 모던 스타일(CSS)
# ====================================================
st.set_page_config(
    page_title="선수 부상 일지 접수",
    page_icon="⚡",
    layout="centered",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    /* 전체 배경 및 폰트 */
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    
    /* 상단 기본 메뉴바/푸터 숨김 */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* 모바일 카드 박스 디자인 */
    .card-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 18px 20px;
        margin-bottom: 20px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    
    .card-title {
        font-size: 15px;
        font-weight: 700;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 12px;
        border-bottom: 1px solid #334155;
        padding-bottom: 8px;
    }

    /* 입력 필드 커스텀 */
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    .stTextInput>div>div>input:focus, .stTextArea>div>div>textarea:focus {
        border-color: #38BDF8 !important;
    }

    /* 라벨 텍스트 스타일 */
    label, p, span {
        color: #E2E8F0 !important;
        font-size: 13px !important;
    }

    /* 제출 버튼 디자인 */
    .stButton>button {
        width: 100%;
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        font-size: 15px !important;
        padding: 12px 0 !important;
        border-radius: 10px !important;
        border: none !important;
        box-shadow: 0 4px 10px rgba(2, 132, 199, 0.3) !important;
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #0369A1 !important;
        transform: translateY(-1px);
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ====================================================
# 2. 메일 발송 로직
# ====================================================
GMAIL_USER = "kimkibum0613@gmail.com"
GMAIL_APP_PW = "isulkubwaqatfzyp"
RECEIVER_EMAIL = "kimkibum0613@naver.com"


def send_injury_email(data: dict) -> bool:
  try:
    msg = MIMEMultipart("alternative")
    msg["Subject"] = (
        f"[부상 접수] {data['player_name']} 선수 ({data['body_part']} / 통증"
        f" {data['current_pain']}점)"
    )
    msg["From"] = GMAIL_USER
    msg["To"] = RECEIVER_EMAIL

    html_content = f"""
        <html>
        <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1E293B;">
            <div style="max-width: 550px; margin: 0 auto; border: 1px solid #E2E8F0; border-radius: 10px; overflow: hidden;">
                <div style="background-color: #0284C7; color: #FFFFFF; padding: 18px 20px;">
                    <h2 style="margin: 0; font-size: 18px;">선수 부상 일지 접수 보고서</h2>
                    <p style="margin: 4px 0 0 0; font-size: 12px; opacity: 0.9;">작성일: {data['record_date']} | 발생일: {data['injury_date']}</p>
                </div>
                <div style="padding: 20px;">
                    <h4 style="margin: 0 0 8px 0; color: #0284C7; border-bottom: 2px solid #E2E8F0; padding-bottom: 4px;">1. 기본 인적사항</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 13px;">
                        <tr><td style="padding: 6px; width: 35%; background: #F8FAFC; font-weight: bold;">선수명</td><td style="padding: 6px;">{data['player_name']}</td></tr>
                        <tr><td style="padding: 6px; background: #F8FAFC; font-weight: bold;">등번호 / 포지션</td><td style="padding: 6px;">{data['jersey_pos']}</td></tr>
                    </table>

                    <h4 style="margin: 0 0 8px 0; color: #0284C7; border-bottom: 2px solid #E2E8F0; padding-bottom: 4px;">2. 부상 부위 및 통증</h4>
                    <table style="width: 100%; border-collapse: collapse; margin-bottom: 16px; font-size: 13px;">
                        <tr><td style="padding: 6px; width: 35%; background: #F8FAFC; font-weight: bold;">부상 부위</td><td style="padding: 6px;">[{data['side']}] {data['body_part']}</td></tr>
                        <tr><td style="padding: 6px; background: #F8FAFC; font-weight: bold;">현재 통증(NRS)</td><td style="padding: 6px; font-weight: bold; color: {'#EF4444' if data['current_pain'] >= 7 else '#0284C7'};">{data['current_pain']} / 10 점</td></tr>
                        <tr><td style="padding: 6px; background: #F8FAFC; font-weight: bold;">과거 부상 이력</td><td style="padding: 6px;">{data['prev_injury']}</td></tr>
                    </table>

                    <h4 style="margin: 0 0 8px 0; color: #0284C7; border-bottom: 2px solid #E2E8F0; padding-bottom: 4px;">3. Subjective (주관적 증상)</h4>
                    <table style="width: 100%; border-collapse: collapse; font-size: 13px;">
                        <tr><td style="padding: 6px; width: 35%; background: #F8FAFC; font-weight: bold;">부상 기전</td><td style="padding: 6px;">{data['mechanism']}</td></tr>
                        <tr><td style="padding: 6px; background: #F8FAFC; font-weight: bold;">당시 통증</td><td style="padding: 6px;">{data['initial_pain']} / 10 점</td></tr>
                        <tr><td style="padding: 6px; background: #F8FAFC; font-weight: bold;">통증 양상</td><td style="padding: 6px;">{data['pain_type']}</td></tr>
                    </table>
                </div>
            </div>
        </body>
        </html>
        """
    msg.attach(MIMEText(html_content, "html"))

    with smtplib.SMTP("smtp.gmail.com", 587) as server:
      server.starttls()
      server.login(GMAIL_USER, GMAIL_APP_PW)
      server.sendmail(msg["From"], [msg["To"]], msg.as_string())
    return True
  except Exception as e:
    st.error(f"메일 발송 에러: {e}")
    return False


# ====================================================
# 3. 모바일 화면 헤더
# ====================================================
st.markdown(
    f"""
    <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 16px;">
        <div>
            <div style="color: #38BDF8; font-size: 11px; font-weight: 800; letter-spacing: 0.5px;">AT MEDICAL REPORT</div>
            <div style="font-size: 20px; font-weight: 700; color: #FFFFFF; margin-top: 2px;">선수 부상 일지 접수</div>
        </div>
        <div style="background-color: #334155; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: #94A3B8;">
            {date.today().strftime('%m.%d')}
        </div>
    </div>
""",
    unsafe_allow_html=True,
)

# ====================================================
# 4. 입력 폼 영역 (카드 모듈화)
# ====================================================
with st.form("injury_report_form", clear_on_submit=True):

  # 카드 1: 선수 기본 정보
  st.markdown(
      '<div class="card-box"><div class="card-title">👤 선수 기본'
      " 정보</div>",
      unsafe_allow_html=True,
  )
  c1, c2 = st.columns(2)
  with c1:
    name = st.text_input("선수명 *", placeholder="이름 입력")
    injury_date = st.date_input("부상 발생일", value=date.today())
  with c2:
    jersey_pos = st.text_input(
        "등번호 / 포지션", placeholder="예: 10번 / FW"
    )
    record_date = st.date_input("차트 작성일", value=date.today())
  st.markdown("</div>", unsafe_allow_html=True)

  # 카드 2: 부상 부위 및 통증 지수
  st.markdown(
      '<div class="card-box"><div class="card-title">🏥 부상 부위 & 통증'
      " (NRS)</div>",
      unsafe_allow_html=True,
  )
  side = st.radio(
      "부상 부위 구분", ["좌(L)", "우(R)", "해당 없음"], horizontal=True
  )
  body_part = st.text_input(
      "상세 부상 부위 *",
      placeholder="예: 발목 외측인대, 햄스트링 기시부",
  )

  current_pain = st.slider(
      "현재 통증 정도 (0: 전혀 없음 ~ 10: 극심한 통증)",
      min_value=0,
      max_value=10,
      value=0,
  )

  prev_injury_choice = st.radio(
      "과거 동일/유사 부상 이력", ["없음", "있음"], horizontal=True
  )
  prev_injury_detail = ""
  if prev_injury_choice == "있음":
    prev_injury_detail = st.text_input(
        "과거 부상 상세 (부위 및 시기)",
        placeholder="예: 우측 발목 인대 / 6개월 전",
    )
  st.markdown("</div>", unsafe_allow_html=True)

  # 카드 3: 주관적 증상 (Subjective)
  st.markdown(
      '<div class="card-box"><div class="card-title">📝 증상 상세'
      " (Subjective)</div>",
      unsafe_allow_html=True,
  )
  mechanism = st.text_area(
      "1. 부상 기전 (어떻게 다쳤나요?)",
      placeholder="예: 착지 도중 발목이 안쪽으로 꺾이며 뚝 소리가 남",
  )
  initial_pain = st.select_slider(
      "2. 부상 당시 통증 정도 (0~10)",
      options=list(range(11)),
      value=5,
  )
  pain_types = st.multiselect(
      "3. 통증 양상 (해당 항목 모두 터치)",
      ["날카로움(Sharp)", "둔함(Dull)", "욱신거림(Throbbing)", "저림(Tingling)"],
  )
  st.markdown("</div>", unsafe_allow_html=True)

  # 전송 버튼
  submitted = st.form_submit_button("의무팀(AT)에 일지 제출하기")

  if submitted:
    if not name or not body_part:
      st.error("선수명과 상세 부상 부위는 필수 입력 항목입니다.")
    else:
      prev_str = (
          f"있음 ({prev_injury_detail})"
          if prev_injury_choice == "있음"
          else "없음"
      )
      payload = {
          "player_name": name,
          "jersey_pos": jersey_pos or "미작성",
          "injury_date": str(injury_date),
          "record_date": str(record_date),
          "side": side,
          "body_part": body_part,
          "current_pain": current_pain,
          "prev_injury": prev_str,
          "mechanism": mechanism or "미작성",
          "initial_pain": initial_pain,
          "pain_type": ", ".join(pain_types) if pain_types else "없음",
      }

      with st.spinner("의무팀 메일함으로 안전하게 전송 중..."):
        if send_injury_email(payload):
          st.success("부상 일지가 의무팀으로 정상 접수되었습니다.")
          st.balloons()
