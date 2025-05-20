from datetime import time

import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from module.db import DBController
from schemas.place import PlaceSchema
from schemas.template import TemplateSchema, InsertTemplateSchema


def show_template_page(db: DBController) -> None:
    """テンプレートページを表示します。"""
    session_templates: list[TemplateSchema] = st.session_state['templates']

    if session_templates:
        template_df = pd.DataFrame([
            {
                '名称': template.name,
                '勤務先名': template.place,
                '開始時刻': template.start_time.strftime('%H:%M'),
                '終了時刻': template.end_time.strftime('%H:%M'),
                '休憩時間': template.break_time.strftime('%H:%M'),
            }
            for template in session_templates
        ])

    st.subheader('テンプレート')

    if st.button('追加', type='primary', key='add_btn'):
        _show_add_form(db)

    if st.session_state['templates']:
        gb = GridOptionsBuilder.from_dataframe(template_df)
        gb.configure_selection('single')
        grid_options = gb.build()

        grid_response = AgGrid(
            template_df,
            gridOptions=grid_options,
            enable_enterprise_modules=False,
            fit_columns_on_grid_load=True,
            height=300,
            width='100%',
            theme='streamlit',
        )

        selected_rows = grid_response['selected_rows']
        if selected_rows is not None:
            selected_index = int(selected_rows.index[0])
            selected_template = st.session_state['templates'][selected_index]
            _show_detail(selected_template, db)


@st.dialog('テンプレート追加')
def _show_add_form(db: DBController) -> None:
    """テンプレート追加ダイアログを表示"""
    session_places: list[PlaceSchema] = st.session_state['places']

    if session_places:
        with st.form('template_form', border=False):
            name = st.text_input('名称を入力してください', key='name', max_chars=8)
            selected_place = st.selectbox('勤務先名を選択してください', options=[place.name for place in session_places], key='selected_place')
            start_time = st.time_input('開始時刻を入力してください', value=time(9, 0), key='start_time', step=300)
            end_time = st.time_input('終了時刻を入力してください', value=time(17, 0), key='end_time', step=300)
            break_time = st.time_input('休憩時間を入力してください', value=time(0, 0), key='break_time', step=300)

            if st.form_submit_button('追加', type='primary'):
                if len(name) == 0:
                    st.error('名称が入力されていません')
                elif len(name) > 8:
                    st.error('名称は8文字以内で入力してください')
                else:
                    place_id = [place.id for place in session_places if place.name == selected_place][0]

                    insert_template = InsertTemplateSchema(
                        user_id=st.session_state['user_id'],
                        place_id=place_id,
                        name=name,
                        start_time=start_time.isoformat(timespec='seconds'),
                        end_time=end_time.isoformat(timespec='seconds'),
                        break_time=break_time.isoformat(timespec='seconds'),
                    )

                    if db.add_template(insert_template):
                        st.session_state['templates'] = db.get_templates(st.session_state['user_id'])
                        st.rerun()
                    else:
                        st.error(f'名称{name}は既に存在します')
    else:
        st.error('勤務先が登録されていません')

@st.dialog('テンプレート詳細')
def _show_detail(template: TemplateSchema, db: DBController) -> None:
    """テンプレート詳細ダイアログを表示"""
    st.write(f'名称：{template.name}')
    st.write(f'勤務先名：{template.place}')
    st.write(f'開始時刻：{template.start_time.strftime("%H:%M")}')
    st.write(f'終了時刻：{template.end_time.strftime("%H:%M")}')
    st.write(f'休憩時間：{template.break_time.strftime("%H:%M")}')

    if st.button('削除', type='primary', key='delete_btn'):
        db.delete_template(template.id)
        st.session_state['templates'] = db.get_templates(st.session_state['user_id'])
        st.rerun()
