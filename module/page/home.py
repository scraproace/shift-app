import calendar
from datetime import datetime

import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import pandas as pd
import streamlit as st

from module.db import DBController
from schemas.shift import ShiftSchema


LIMIT_AMOUNT = 1_030_000  # 限度額
PIE_FONTPATH = './fonts/msgothic.ttc'  # 円グラフのフォントパス


def show_home_page(db: DBController) -> None:
    """ホームページを表示"""
    session_shifts: list[ShiftSchema] = st.session_state['shifts']

    today = datetime.today()

    # メイン情報
    start_datetime, end_datetime = _get_date_period(today, 31)
    current_amount = _caliculate_amount(session_shifts, start_datetime, today)
    year_amount = _caliculate_amount(session_shifts, datetime(today.year, 1, 1, 0, 0, 0), today)
    next_shift = _get_next_shift(session_shifts, today)

    # 勤務先情報
    if session_shifts:
        place_infos = []

        shift_df = pd.DataFrame([
            {
                'place_id': shift.place_id,
                'place': shift.place,
                'amount': shift.amount,
                'start_datetime': shift.start_datetime,
                'end_datetime': shift.end_datetime,
                'closing_day': shift.closing_day,
                'pay_day': shift.pay_day,
            }
            for shift in session_shifts
        ])

        for place, grouped_df in shift_df.groupby('place'):
            place_id = grouped_df.place_id.iloc[0]
            place_closing_day = grouped_df.closing_day.iloc[0]
            place_pay_day = grouped_df.pay_day.iloc[0]

            place_start_datetime, place_end_datetime = _get_date_period(today, place_closing_day)
            to_closing_day = (place_end_datetime - today).days

            mask = (place_start_datetime < grouped_df['end_datetime']) & (grouped_df['end_datetime'] <= place_end_datetime)
            place_amount = grouped_df.loc[mask, 'amount'].sum()

            if place_amount == 0:
                continue

            place_start_datetime, place_end_datetime = _get_date_period(today, place_pay_day)
            to_pay_day = (place_end_datetime - today).days
            print(place_end_datetime)
            print(today)
            print(place_end_datetime-today)

            place_next_shift = _get_next_shift(session_shifts, today, place_id)

            place_infos.append({
                '勤務先名': place,
                '締め日までの見込額': f'{place_amount:,}円',
                '次回出勤日': place_next_shift.strftime('%Y/%m/%d') if place_next_shift else 'なし',
                # '締め日まで': f'{to_closing_day}日',
                '給料日まで': f'{to_pay_day}日',
            })

        place_df = pd.DataFrame(place_infos)

    st.subheader('ホーム')

    if st.button('ログアウト', type='primary', key='logout_btn'):
        st.session_state.clear()
        st.rerun()

    _display_pie_chart(
        current_amount,
        st.session_state['user'].goal_amount,
        start_datetime,
        end_datetime,
        PIE_FONTPATH,
    )

    st.markdown(
        f'<div style="text-align: center; font-size: 28px; font-weight: bold;">{LIMIT_AMOUNT:,}円まで残り{LIMIT_AMOUNT - year_amount:,}円</div>',
        unsafe_allow_html=True
    )

    if next_shift is None:
        st.markdown(
            '<div style="text-align: center; font-size: 28px; font-weight: bold;">次回の出勤予定なし</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            f'<div style="text-align: center; font-size: 28px; font-weight: bold;">次回の出勤日は{next_shift.strftime("%Y/%m/%d")}</div>',
            unsafe_allow_html=True
        )

    if session_shifts:
        st.write('')
        st.dataframe(place_df, use_container_width=True, hide_index=True)


def _get_date_period(today: datetime, closing_day: int) -> tuple[datetime, datetime]:
    """指定された締め日から、開始日と終了日を計算"""
    year = today.year
    month = today.month

    if today.day <= closing_day:
        last_day_this_month = calendar.monthrange(year, month)[1]
        end_day = min(closing_day, last_day_this_month)
        end_datetime = datetime(today.year, today.month, end_day, 23, 59, 59)

        if month == 1:
            prev_year = year - 1
            prev_month = 12
        else:
            prev_year = year
            prev_month = month - 1

        last_day_prev_month = calendar.monthrange(prev_year, prev_month)[1]

        if closing_day + 1 > last_day_prev_month:
            start_month = month
            start_day = 1
        else:
            start_month = prev_month
            start_day = closing_day + 1

        start_datetime = datetime(prev_year, start_month, start_day, 0, 0, 0)
    else:
        last_day_this_month = calendar.monthrange(year, month)[1]
        start_day = min(closing_day + 1, last_day_this_month)
        start_datetime = datetime(year, month, start_day, 0, 0, 0)

        if month == 12:
            next_year = year + 1
            next_month = 1
        else:
            next_year = year
            next_month = month + 1

        last_day_next_month = calendar.monthrange(next_year, next_month)[1]
        end_day = min(closing_day, last_day_next_month)
        end_datetime = datetime(next_year, next_month, end_day, 23, 59, 59)

    return start_datetime, end_datetime


def _caliculate_amount(shifts: list[ShiftSchema], start_datetime: datetime, end_datetime: datetime) -> int:
    """指定された期間の金額を計算"""
    amount = 0
    for shift in shifts:
        if start_datetime < shift.end_datetime <= end_datetime:
            amount += shift.amount

    return amount


def _get_next_shift(shifts: list[ShiftSchema], today: datetime, place_id: int = None) -> datetime | None:
    """次回の出勤日を取得"""
    for shift in shifts:
        if place_id is None or shift.place_id == place_id:
            if shift.start_datetime > today:
                return shift.start_datetime

    return None


def _display_pie_chart(
    current_amount: int,
    goal_amount: int,
    start_datetime: datetime,
    end_datetime: datetime,
    pie_fontpath: str,
) -> None:
    """円グラフを表示"""
    achievement_rate = (current_amount / goal_amount) * 100

    achievement_rate = 100 if achievement_rate > 100 else achievement_rate

    sizes = [achievement_rate, 100 - achievement_rate]
    colors = ['#52b338', '#e2e9d9']
    wedge = {'width' : 0.1}

    plt.pie(sizes, colors=colors, wedgeprops=wedge, startangle=90, counterclock=False)

    fontpath = pie_fontpath
    font_prop = fm.FontProperties(fname=fontpath)

    plt.text(0, 0.5, f"{start_datetime.strftime('%Y/%m/%d')} - {end_datetime.strftime('%Y/%m/%d')}", fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, 0.35, f'目標金額 {goal_amount:,}円', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, 0, '今日までの給料', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=10)
    plt.text(0, -0.2, f'{current_amount:,}円', fontproperties=font_prop, horizontalalignment='center', verticalalignment='center', fontsize=20)

    st.pyplot(plt)
