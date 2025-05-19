import streamlit as st

from module.db import DBController


def show_login_page(db: DBController) -> None:
    """ログインページを表示"""
    st.subheader('ログイン画面')

    with st.form('login_form', border=False):
        username = st.text_input('ユーザー名を入力してください', key='username')
        password = st.text_input('パスワードを入力してください', type='password', key='password')

        if st.form_submit_button('ログイン', type='primary'):
            if len(username) == 0:
                st.error('ユーザー名が入力されていません')
            elif len(password) == 0:
                st.error('パスワードが入力されていません')
            else:
                user = db.login(username, password)

                if user is not None:
                    st.session_state['user_id'] = user.id
                    st.session_state['user'] = user
                    st.session_state['places'] = db.get_places(user.id)
                    st.session_state['shifts'] = db.get_shifts(user.id)
                    st.rerun()
                else:
                    st.error('ユーザー名またはパスワードが間違っています')
