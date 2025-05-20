from datetime import datetime, time, timedelta

import streamlit as st
import streamlit_calendar as st_calendar

from module.db import DBController
from schemas.place import PlaceSchema
from schemas.shift import ShiftSchema, InsertShiftSchema
from schemas.template import TemplateSchema


def show_shift_page(db: DBController) -> None:
    """シフトページを表示"""
    session_shifts: list[ShiftSchema] = st.session_state['shifts']
    session_templates: list[TemplateSchema] = st.session_state['templates']

    events = []
    for shift in session_shifts:
        events.append({
            'id': shift.id,
            'title': shift.place,
            'start': shift.start_datetime.isoformat(),
            'end': shift.end_datetime.isoformat(),
        })

    st.subheader('シフト')

    selected_template_option = ['選択なし']
    for template in session_templates:
        selected_template_option.append(template.name)

    selected_template_name = st.selectbox('テンプレートを選択してください', options=selected_template_option, key='selected_template_name')

    if st.button('追加', type='primary', key='add_shift_btn'):
        if selected_template_name == '選択なし':
            _show_add_form(db)
        else:
            selected_template = [template for template in session_templates if template.name == selected_template_name][0]
            _show_add_form(db, selected_template)

    options = {
        'initialView': 'dayGridMonth',
        'titleFormat': {
            'year': 'numeric',
            'month': '2-digit',
            'day': '2-digit'
        },
        'locale': 'ja',
        'height': 'auto',
    }

    calender_event = st_calendar.calendar(events=events, options=options)

    if calender_event:
        if calender_event['callback'] == 'eventClick':
            selected_shift_id = int(calender_event['eventClick']['event']['id'])
            selected_shift = [shift for shift in st.session_state['shifts'] if shift.id == selected_shift_id][0]
            _show_detail(selected_shift, db)


@st.dialog('シフト追加')
def _show_add_form(db: DBController, template: TemplateSchema | None = None) -> None:
    """シフト追加ダイアログを表示"""
    session_places: list[PlaceSchema] = st.session_state['places']

    if session_places:
        is_repeat = st.checkbox('週次登録', key='is_repeat')

        default_value = {
            'selected_place': 0,
            'start_date': datetime.today(),
            'start_time': time(9, 0),
            'end_date': datetime.today(),
            'end_time': time(17, 0),
            'break_time': time(0, 0),
        }

        if template is not None:
            for index, place in enumerate(session_places):
                if place.id == template.place_id:
                    default_value['selected_place'] = index
                    break

            default_value['start_time'] = template.start_time
            default_value['end_time'] = template.end_time
            default_value['break_time'] = template.break_time

        with st.form('add_form', border=False):
            selected_place = st.selectbox('勤務先名を選択してください', options=[place.name for place in session_places], index=default_value['selected_place'], key='selected_place')
            start_date = st.date_input('開始日付を入力してください', value=default_value['start_date'], key='start_date')
            start_time = st.time_input('開始時刻を入力してください', value=default_value['start_time'], key='start_time', step=300)
            end_date = st.date_input('終了日付を入力してください', value=default_value['end_date'], key='end_date')
            end_time = st.time_input('終了時刻を入力してください', value=default_value['end_time'], key='end_time', step=300)

            if is_repeat:
                repeat_end_date = st.date_input('最終日付(週次)を入力してください', value=datetime.today(), key='repeat_end_date')

            break_time = st.time_input('休憩時間を入力してください', value=default_value['break_time'], key='break_time', step=300)

            if st.form_submit_button('追加', type='primary'):
                start_datetime = datetime.combine(start_date, start_time)
                end_datetime = datetime.combine(end_date, end_time)

                if start_datetime >= end_datetime:
                    st.error('開始日時は終了日時よりも早く設定してください')
                elif end_datetime - start_datetime <= (timedelta(hours=break_time.hour, minutes=break_time.minute)):
                    st.error('休憩時間は勤務時間より短く設定してください')
                elif is_repeat and start_date > repeat_end_date:
                    st.error('開始日時は最終日付(週次)よりも早く設定してください')
                else:
                    place_id = [place.id for place in session_places if place.name == selected_place][0]

                    if is_repeat:
                        while start_date <= repeat_end_date:
                            insert_shift = InsertShiftSchema(
                                user_id=st.session_state['user_id'],
                                place_id=place_id,
                                start_datetime=start_datetime.isoformat(timespec='seconds'),
                                end_datetime=end_datetime.isoformat(timespec='seconds'),
                                break_time=break_time.isoformat(timespec='seconds'),
                                is_update=True,
                            )

                            db.add_shift(insert_shift)

                            start_date += timedelta(days=7)
                            end_date += timedelta(days=7)
                            start_datetime = datetime.combine(start_date, start_time)
                            end_datetime = datetime.combine(end_date, end_time)

                        st.session_state['shifts'] = db.get_shifts(st.session_state['user_id'])
                        st.rerun()
                    else:
                        insert_shift = InsertShiftSchema(
                            user_id=st.session_state['user_id'],
                            place_id=place_id,
                            start_datetime=start_datetime.isoformat(timespec='seconds'),
                            end_datetime=end_datetime.isoformat(timespec='seconds'),
                            break_time=break_time.isoformat(timespec='seconds'),
                        )

                        if db.add_shift(insert_shift):
                            st.session_state['shifts'] = db.get_shifts(st.session_state['user_id'])
                            st.rerun()
                        else:
                            st.error('その時間はシフトが既に存在します')
    else:
        st.error('勤務先が登録されていません')


@st.dialog('シフト詳細')
def _show_detail(shift: ShiftSchema, db: DBController) -> None:
    """シフト詳細ダイアログを表示"""
    st.write(f'勤務先：{shift.place}')
    st.write(f'開始日時：{shift.start_datetime.strftime("%Y/%m/%d %H:%M")}')
    st.write(f'終了日時：{shift.end_datetime.strftime("%Y/%m/%d %H:%M")}')
    st.write(f'休憩時間：{shift.break_time.strftime("%H:%M")}')
    st.write(f'時給：{shift.wage:,}円')
    st.write(f'深夜給：{"有" if shift.has_night_wage else "無"}')
    st.write(f'見込額：{shift.amount:,}円')

    if st.button('削除', type='primary', key='delete_btn'):
        db.delete_shift(shift.id)
        st.session_state['shifts'] = db.get_shifts(st.session_state['user_id'])
        st.rerun()
