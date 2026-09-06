from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import streamlit as st

# ====================================================
# 메일 발송 설정
# ====================================================
GMAIL_USER = "kimkibum0613@gmail.com"
GMAIL_APP_PW = "isulkubwaqatfzyp"  # 16자리 구글 앱 비밀번호
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
        <body style="font-family: sans-serif; line-height: 1.6; color: #1E293B;">
            <div style="max-width: 600px; margin: 0 auto; border: 1px solid #E2E8F0; border-radius: 8px; padding: 20px;">
                <h2 style="color: #0284C7; margin-top: 0;">선수 부상 일지 접수 리포트</h2>
                <p style="color: #64748B; font-size: 13px;">작성일: {data['record_date']} | 발생일: {data['injury_date']}</p>
                <hr style="border: 0; border-top: 1px solid #E2E8F0;">
                
                <h3>1. 기본 인적사항</h3>
                <ul>
                    <li><b>선수명:</b> {data['player_name']}</li>
                    <li><b>등번호 / 포지션:</b> {data['jersey_pos']}</li>
                </ul>

                <h3>2. 부상 부위 및 통증</h3>
                <ul>
                    <li><b>부상 부위:</b> [{data['side']}] {data['body_part']}</li>
                    <li><b>현재 자각 통증 (NRS):</b> <span style="font-size: 16px; font-weight: bold; color: {'#EF4444' if data['current_pain'] >= 7 else '#0284C7'};">{data['current_pain']} / 10 점</span></li>
                    <li><b>과거 부상 이력:</b> {data['prev_injury']}</li>
                </ul>

                <h3>3. Subjective (주관적 증상)</h3>
                <ul>
                    <li><b>부상 기전:</b> {data['mechanism']}</li>
                    <li><b>당시 통증 정도:</b> {data['initial_pain']} / 10 점</li>
                    <li><b>통증 양상:</b> {data['pain_type']}</li>
                </ul>
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
# 모바일 최적화 웹 화면 구성 (Streamlit)
# ====================================================
st.set_page_config(page_title="선수 부상 일지 접수", page_icon="📋")

st.title("📋 부상 일지 접수")
st.caption("의무팀(AT)으로 실시간 전달되는 공식 보고서입니다.")

with st.form("injury_form", clear_on_submit=True):
  st.subheader("1. 기본 정보")
  col1, col2 = st.columns(2)
  with col1:
    name = st.text_input("선수명 *")
    injury_date = st.date_input("부상 발생일", value=date.today())
  with col2:
    jersey_pos = st.text_input("등번호 / 포지션 (예: 10번 / FW)")
    record_date = st.date_input("차트 작성일", value=date.today())

  st.divider()
  st.subheader("2. 부상 부위 및 통증 지수")
  side = st.radio("부상 위치 구분", ["좌", "우", "해당 없음"], horizontal=True)
  body_part = st.text_input(
      "상세 부상 부위 * (예: 발목 외측인대, 햄스트링)"
  )

  current_pain = st.slider(
      "현재 통증 정도 (0: 통증 없음 ~ 10: 죽을 듯이 아픔)",
      0,
      10,
      0,
  )

  prev_injury_choice = st.radio(
      "과거 동일/유사 부상 이력", ["없음", "있음"], horizontal=True
  )
  prev_injury_detail = ""
  if prev_injury_choice == "있음":
    prev_injury_detail = st.text_input(
        "과거 부상 상세 (부위 및 발생 시기 기재)",
        placeholder="예: 우측 발목 인대 / 6개월 전",
    )

  st.divider()
  st.subheader("3. Subjective (주관적 증상)")
  mechanism = st.text_area(
      "1. 부상 기전 (어떻게 다쳤는가?)",
      placeholder="예: 착지 과정에서 상대 발을 밟고 안쪽으로 꺾임",
  )
  initial_pain = st.select_slider(
      "2. 부상 당시 통증 정도 (NRS 0~10)",
      options=list(range(11)),
      value=5,
  )
  pain_types = st.multiselect(
      "3. 통증 양상 (해당되는 것 모두 선택)",
      ["날카로움(Sharp)", "둔함(Dull)", "욱신거림(Throbbing)", "저림(Tingling)"],
  )

  submit_btn = st.form_submit_button(
      "AT 의무팀에 제출하기", use_container_width=True
  )

  if submit_btn:
    if not name or not body_part:
      st.error("선수명과 상세 부상 부위는 필수 입력 사항입니다.")
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

      with st.spinner("의무팀 메일함으로 전송 중..."):
        if send_injury_email(payload):
          st.success("부상 일지가 AT 의무팀으로 안전하게 전송되었습니다.")
          st.balloons()
