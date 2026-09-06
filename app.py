import sqlite3
from datetime import date
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import smtplib
import pandas as pd
import streamlit as st

# ====================================================
# 1. 페이지 환경 & 반응형 모던 스타일(CSS)
# ====================================================
st.set_page_config(
    page_title="선수 부상 일지 & AT 관리 시스템",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    .stApp {
        background-color: #0F172A;
        color: #F8FAFC;
    }
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .card-box {
        background-color: #1E293B;
        border: 1px solid #334155;
        border-radius: 14px;
        padding: 16px 18px;
        margin-bottom: 16px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.2);
    }
    .card-title {
        font-size: 14px;
        font-weight: 700;
        color: #38BDF8;
        display: flex;
        align-items: center;
        gap: 8px;
        margin-bottom: 10px;
        border-bottom: 1px solid #334155;
        padding-bottom: 6px;
    }
    .stTextInput>div>div>input, .stTextArea>div>div>textarea {
        background-color: #0F172A !important;
        color: #F1F5F9 !important;
        border: 1px solid #334155 !important;
        border-radius: 8px !important;
    }
    label, p, span {
        color: #E2E8F0 !important;
        font-size: 13px !important;
    }
    .stButton>button {
        width: 100%;
        background-color: #0284C7 !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border-radius: 10px !important;
        border: none !important;
    }
    </style>
""",
    unsafe_allow_html=True,
)

# ====================================================
# 2. 로컬 데이터베이스(SQLite) 초기화
# ====================================================
conn = sqlite3.connect("injury_records.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS records (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    player_name TEXT,
    jersey_pos TEXT,
    injury_date TEXT,
    record_date TEXT,
    side TEXT,
    body_part TEXT,
    current_pain INTEGER,
    prev_injury TEXT,
    mechanism TEXT,
    initial_pain INTEGER,
    pain_type TEXT,
    obj_appearance TEXT,
    obj_rom TEXT,
    obj_mmt TEXT,
    obj_gait TEXT,
    ass_trainer_opinion TEXT,
    ass_diagnosis TEXT,
    plan_action TEXT,
    plan_limit TEXT,
    plan_return TEXT,
    plan_rehab TEXT
)
"""
)
conn.commit()

# ====================================================
# 3. 메일 발송 로직
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
        <body style="font-family: sans-serif; line-height: 1.6; color: #1E293B;">
            <div style="max-width: 550px; margin: 0 auto; border: 1px solid #E2E8F0; border-radius: 10px; padding: 20px;">
                <h3 style="color: #0284C7; margin-top: 0;">선수 부상 일지 접수 리포트</h3>
                <p style="font-size: 12px; color: #64748B;">작성일: {data['record_date']} | 발생일: {data['injury_date']}</p>
                <hr style="border: 0; border-top: 1px solid #E2E8F0;">
                <p><b>선수명:</b> {data['player_name']} ({data['jersey_pos']})</p>
                <p><b>부상 부위:</b> [{data['side']}] {data['body_part']}</p>
                <p><b>현재 통증(NRS):</b> <b style="color:red;">{data['current_pain']} / 10점</b></p>
                <p><b>과거 부상력:</b> {data['prev_injury']}</p>
                <p><b>부상 기전:</b> {data['mechanism']}</p>
                <p><b>당시 통증 / 양상:</b> {data['initial_pain']}점 / {data['pain_type']}</p>
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
# 4. 상단 탭 구성 (선수 입력 탭 / AT 관리자 탭)
# ====================================================
tab_player, tab_at = st.tabs(
    ["📱 선수 차트 입력", "📋 AT 관리자 대시보드 (SOAP 관리)"]
)

# ----------------------------------------------------
# 탭 1: 선수 차트 입력
# ----------------------------------------------------
with tab_player:
  st.markdown(
      f"""
        <div style="display: flex; justify-content: space-between; align-items: flex-end; margin-bottom: 12px;">
            <div>
                <div style="color: #38BDF8; font-size: 11px; font-weight: 800;">AT MEDICAL SYSTEM</div>
                <div style="font-size: 20px; font-weight: 700; color: #FFFFFF;">선수 부상 일지 접수</div>
            </div>
            <div style="background-color: #334155; padding: 4px 10px; border-radius: 12px; font-size: 12px; font-weight: 600; color: #94A3B8;">
                {date.today().strftime('%m.%d')}
            </div>
        </div>
    """,
      unsafe_allow_html=True,
  )

  with st.form("injury_report_form", clear_on_submit=True):
    st.markdown(
        '<div class="card-box"><div class="card-title">👤 선수 기본'
        " 정보</div>",
        unsafe_allow_html=True,
    )
    c1, c2 = st.columns(2)
    with c1:
      name = st.text_input("선수명 *")
      injury_date = st.date_input("부상 발생일", value=date.today())
    with c2:
      jersey_pos = st.text_input("등번호 / 포지션", placeholder="예: 10 / FW")
      record_date = st.date_input("차트 작성일", value=date.today())
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="card-box"><div class="card-title">🏥 부상 부위 & 통증'
        " (NRS)</div>",
        unsafe_allow_html=True,
    )
    side = st.radio(
        "부상 부위 구분", ["좌(L)", "우(R)", "해당 없음"], horizontal=True
    )
    body_part = st.text_input(
        "상세 부상 부위 *", placeholder="예: 발목 외측인대, 햄스트링"
    )
    current_pain = st.slider("현재 통증 정도 (0~10)", 0, 10, 0)
    prev_injury_choice = st.radio(
        "과거 부상 이력", ["없음", "있음"], horizontal=True
    )
    prev_injury_detail = ""
    if prev_injury_choice == "있음":
      prev_injury_detail = st.text_input(
          "과거 부상 상세 (부위 및 시기)",
          placeholder="예: 우측 발목 인대 / 6개월 전",
      )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        '<div class="card-box"><div class="card-title">📝 주관적 증상'
        " (Subjective)</div>",
        unsafe_allow_html=True,
    )
    mechanism = st.text_area(
        "1. 부상 기전 (어떻게 다쳤는가?)",
        placeholder="예: 착지 도중 발목이 안쪽으로 꺾임",
    )
    initial_pain = st.select_slider(
        "2. 부상 당시 통증 정도 (0~10)", options=list(range(11)), value=5
    )
    pain_types = st.multiselect(
        "3. 통증 양상",
        ["날카로움(Sharp)", "둔함(Dull)", "욱신거림(Throbbing)", "저림(Tingling)"],
    )
    st.markdown("</div>", unsafe_allow_html=True)

    submitted = st.form_submit_button("의무팀(AT)에 일지 제출하기")

    if submitted:
      if not name or not body_part:
        st.error("선수명과 부상 부위는 필수 입력 항목입니다.")
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

        # DB에 저장
        cursor.execute(
            """
                INSERT INTO records (
                    player_name, jersey_pos, injury_date, record_date, side, body_part,
                    current_pain, prev_injury, mechanism, initial_pain, pain_type,
                    obj_appearance, obj_rom, obj_mmt, obj_gait, ass_trainer_opinion,
                    ass_diagnosis, plan_action, plan_limit, plan_return, plan_rehab
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, '', '', '', '', '', '', '', '미정', '', '')
            """,
            (
                payload["player_name"],
                payload["jersey_pos"],
                payload["injury_date"],
                payload["record_date"],
                payload["side"],
                payload["body_part"],
                payload["current_pain"],
                payload["prev_injury"],
                payload["mechanism"],
                payload["initial_pain"],
                payload["pain_type"],
            ),
        )
        conn.commit()

        # 메일 발송
        with st.spinner("의무팀 메일함으로 안전하게 전송 중..."):
          send_injury_email(payload)
        st.success("부상 일지가 정상 접수되었습니다.")
        st.balloons()

# ----------------------------------------------------
# 탭 2: AT 관리자 대시보드 (O / A / P 작성 및 차트 분석)
# ----------------------------------------------------
with tab_at:
  st.subheader("📋 AT 의무팀 관리자 대시보드")

  # AT 접근 비밀번호 설정
  at_pw = st.text_input(
      "트레이너 보안 비밀번호 입력", type="password", key="at_password"
  )

  if at_pw == "1234":  # 기본 비밀번호: 1234
    df = pd.read_sql("SELECT * FROM records", conn)

    if df.empty:
      st.info("현재 접수된 선수 부상 일지가 없습니다.")
    else:
      # 상단 통계 바
      m1, m2, m3 = st.columns(3)
      m1.metric("총 부상 접수 건수", f"{len(df)}건")
      m2.metric("등록 선수 수", f"{df['player_name'].nunique()}명")
      latest_row = df.iloc[-1]
      m3.metric(
          "최근 보고 선수",
          f"{latest_row['player_name']} ({latest_row['body_part']})",
      )

      st.divider()

      col_left, col_right = st.columns([1, 1])

      with col_left:
        st.markdown("#### 1. 일지 선택 및 분석")
        target_player = st.selectbox(
            "선수를 선택하세요", df["player_name"].unique()
        )
        player_df = df[df["player_name"] == target_player].sort_values(
            "record_date"
        )

        # 통증 회복 추이 꺾은선 차트
        st.markdown(f"**📈 [{target_player}] 통증 지수(NRS) 회복 추이**")
        chart_data = (
            player_df[["record_date", "current_pain"]]
            .set_index("record_date")
            .rename(columns={"current_pain": "NRS 통증 점수"})
        )
        st.line_chart(chart_data)

        # 특정 차트 선택
        record_options = {
            f"ID {r['id']} | {r['record_date']} - {r['side']} {r['body_part']}": r[
                "id"
            ]
            for _, r in player_df.iterrows()
        }
        selected_label = st.selectbox(
            "평가/수정할 부상 기록 선택", list(record_options.keys())
        )
        target_id = record_options[selected_label]
        target_record = df[df["id"] == target_id].iloc[0]

        # 선수가 보낸 정보 요약 확인
        st.markdown(
            f"""
            <div class="card-box">
                <div class="card-title">🔍 선수가 제출한 내용 (Subjective)</div>
                <p><b>선수:</b> {target_record['player_name']} ({target_record['jersey_pos']})</p>
                <p><b>부상일 / 작성일:</b> {target_record['injury_date']} / {target_record['record_date']}</p>
                <p><b>부상 부위:</b> [{target_record['side']}] {target_record['body_part']} (통증: {target_record['current_pain']}점)</p>
                <p><b>부상 기전:</b> {target_record['mechanism']}</p>
                <p><b>통증 양상:</b> {target_record['pain_type']}</p>
                <p><b>과거력:</b> {target_record['prev_injury']}</p>
            </div>
            """,
            unsafe_allow_html=True,
        )

      with col_right:
        st.markdown("#### 2. AT 차트 작성 (Objective / Assessment / Plan)")
        with st.form("at_soap_form"):
          # Objective
          st.markdown("**[Objective - 객관적 검사]**")
          appearance = st.multiselect(
              "4. 외관 확인",
              [
                  "부종(Swelling)",
                  "피하출혈",
                  "압통(Tenderness)",
                  "변형(Deformity)",
              ],
              default=[
                  x.strip()
                  for x in str(target_record["obj_appearance"]).split(",")
                  if x.strip()
              ],
          )
          rom = st.text_input(
              "5. 가동범위 (ROM)",
              value=str(target_record["obj_rom"] or ""),
              placeholder="예: 제한 있음 (AROM: 굴곡 10도 제한 / PROM: 통증 동반)",
          )
          mmt = st.selectbox(
              "6. 도수근력검사 (MMT)",
              [
                  "5점 (Normal)",
                  "4점 (Good)",
                  "3점 (Fair)",
                  "2점 (Poor)",
                  "1점 (Trace)",
              ],
              index=0,
          )
          gait = st.selectbox(
              "7. 이동 및 보행",
              ["자가 보행 가능", "파행(쩔뚝거림)", "부축/목발 필요"],
              index=0,
          )

          # Assessment
          st.markdown("**[Assessment - 평가]**")
          opinion = st.text_area(
              "8. 트레이너 소견",
              value=str(target_record["ass_trainer_opinion"] or ""),
              placeholder="예: ATFL 2도 염좌 의심, 내반 스트레스 검사 양성",
          )
          diagnosis = st.text_input(
              "9. 병원 진단 결과",
              value=str(target_record["ass_diagnosis"] or ""),
              placeholder="예: 방문 완료 (전거비인대 부분파열 / X-ray 골절 없음)",
          )

          # Plan
          st.markdown("**[Plan - 조치 및 계획]**")
          actions = st.multiselect(
              "10. 당일 현장 조치",
              ["Icing", "Compression", "Elevation", "Taping", "깁스/보호대"],
              default=[
                  x.strip()
                  for x in str(target_record["plan_action"]).split(",")
                  if x.strip()
              ],
          )
          limit = st.selectbox(
              "11. 일일 트레이닝 제한 범위",
              [
                  "Full Out (모든 훈련 제외 / 치료 및 재활)",
                  "Limited (조깅 및 개인 볼 훈련만 가능)",
                  "Full Training (테이핑 후 정상 훈련 소화)",
              ],
              index=0,
          )
          return_time = st.text_input(
              "12. 예상 복귀 시기",
              value=str(target_record["plan_return"] or ""),
              placeholder="예: 부상일로부터 약 2주일 뒤 복귀 예상",
          )
          rehab_plan = st.text_area(
              "13. 재활 및 치료 계획 / 특이사항",
              value=str(target_record["plan_rehab"] or ""),
              placeholder="예: 1~3일차 RICE 처치 후 4일차부터 등척성 강화 및 발목 밸런스 훈련 실시",
          )

          save_btn = st.form_submit_button("트레이너 차트 저장하기")

          if save_btn:
            cursor.execute(
                """
                    UPDATE records
                    SET obj_appearance = ?, obj_rom = ?, obj_mmt = ?, obj_gait = ?,
                        ass_trainer_opinion = ?, ass_diagnosis = ?, plan_action = ?,
                        plan_limit = ?, plan_return = ?, plan_rehab = ?
                    WHERE id = ?
                """,
                (
                    ", ".join(appearance),
                    rom,
                    mmt,
                    gait,
                    opinion,
                    diagnosis,
                    ", ".join(actions),
                    limit,
                    return_time,
                    rehab_plan,
                    target_id,
                ),
            )
            conn.commit()
            st.success(
                f"[{target_record['player_name']}] 선수의 트레이너 평가(O/A/P)가"
                " 저장되었습니다."
            )
            st.rerun()

      st.divider()
      # 전체 엑셀 다운로드 기능
      st.markdown("#### 3. 선수단 부상 데이터베이스 백업")
      csv_data = df.to_csv(index=False).encode("utf-8-sig")
      st.download_button(
          label="📥 전체 부상자 명단 엑셀(CSV) 다운로드",
          data=csv_data,
          file_name=f"부상자_차트_전체누적_{date.today()}.csv",
          mime="text/csv",
      )

  elif at_pw:
    st.error("비밀번호가 일치하지 않습니다.")
