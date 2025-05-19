import streamlit as st

from module.db import DBController
from schemas.user import UpdateUserSchema


def show_setting_page(db: DBController) -> None:
    """設定ページを表示"""
    st.subheader('アカウント')

    with st.form('account_form', border=False):
        username = st.text_input('ユーザー名', value=st.session_state['user'].username, key='username')
        password = st.text_input('パスワード', value=st.session_state['user'].password, type='password', key='password')
        goal_amount = st.number_input('目標金額(円)', value=st.session_state['user'].goal_amount, key='goal_amount')

        if st.form_submit_button('変更', type='primary'):
            if len(username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(password) == 0:
                st.error('パスワードが入力されていません')
            else:
                update_user = UpdateUserSchema(
                    id=st.session_state['user_id'],
                    username=username,
                    password=password,
                    goal_amount=goal_amount,
                )

                if db.update_user(update_user):
                    st.session_state['user'] = db.get_user(st.session_state['user_id'])
                    st.success(f'ユーザー名{username}の登録情報が変更されました')
                else:
                    st.error(f'ユーザー名{username}は既に存在します')
