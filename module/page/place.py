import pandas as pd
import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder

from module.db import DBController
from schemas.place import PlaceSchema, InsertPlaceSchema


def show_place_page(db: DBController) -> None:
    """勤務先ページを表示します。"""
    session_places: list[PlaceSchema] = st.session_state['places']

    if session_places:
        place_df = pd.DataFrame([
            {
                '勤務先名': place.name,
                '時給': f'{place.wage:,}円',
                '深夜給': '有' if place.has_night_wage else '無',
                '締め日': f'{place.closing_day}日',
                '給料日': f'{place.pay_day}日',
            }
            for place in session_places
        ])

    st.subheader('勤務先')

    if st.button('追加', type='primary', key='add_place_btn'):
        _show_add_form(db)

    if st.session_state['places']:
        gb = GridOptionsBuilder.from_dataframe(place_df)
        gb.configure_selection('single')
        grid_options = gb.build()

        grid_response = AgGrid(
            place_df,
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
            selected_place = st.session_state['places'][selected_index]
            _show_detail(selected_place, db)


@st.dialog('勤務先追加')
def _show_add_form(db: DBController) -> None:
    """勤務先追加ダイアログを表示"""
    with st.form('place_form', border=False):
        name = st.text_input('勤務先名を入力してください', key='name')
        wage = st.number_input('時給(円)を入力してください', value=1000, key='wage', step=1)
        has_night_wage = st.checkbox('深夜手当あり', value=False, key='has_night_wage')
        closing_day = st.number_input('締め日を入力してください', value=15, min_value=1, max_value=31, key='closing_day', step=1)
        pay_day = st.number_input('給料日を入力してください', value=25, min_value=1, max_value=31, key='pay_day', step=1)

        if st.form_submit_button('追加', type='primary'):
            if len(name) == 0:
                st.error('勤務先名が入力されていません')
            else:
                insert_place = InsertPlaceSchema(
                    user_id=st.session_state['user_id'],
                    name=name,
                    wage=wage,
                    has_night_wage=has_night_wage,
                    closing_day=closing_day,
                    pay_day=pay_day,
                )

                if db.add_place(insert_place):
                    st.session_state['places'] = db.get_places(st.session_state['user_id'])
                    st.rerun()
                else:
                    st.error(f'勤務先{name}は既に存在します')


@st.dialog('勤務先詳細')
def _show_detail(place: PlaceSchema, db: DBController):
    """勤務先詳細ダイアログを表示"""
    st.write(f'勤務先名：{place.name}')
    st.write(f'時給: {place.wage:,}円')
    st.write(f"深夜給: {'有' if place.has_night_wage else '無'}")
    st.write(f'締め日：{place.closing_day}日')
    st.write(f'給料日：{place.pay_day}日')

    if st.button('削除', type='primary', key='delete_shift_btn'):
        db.delete_place(place.id)
        st.session_state['places'] = db.get_places(st.session_state['user_id'])
        st.rerun()
