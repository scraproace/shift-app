import streamlit as st

from module.db import DBController
from schemas.user import InsertUserSchema


def show_create_account_page(db: DBController) -> None:
    """アカウント作成ページを表示"""
    st.subheader('アカウント作成')

    with st.form('create_account_form', border=False):
        username = st.text_input('ユーザー名を入力してください', key='username')
        password = st.text_input('パスワードを入力してください', type='password', key='password')

        if st.form_submit_button('作成', type='primary'):
            if len(username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(password) == 0:
                st.error('パスワードが入力されていません')
            else:
                insert_user = InsertUserSchema(
                    username=username,
                    password=password,
                )
                if db.add_user(insert_user):
                    st.success(f'ユーザー名{username}が登録されました')
                else:
                    st.error(f'ユーザー名{username}は既に存在します')
