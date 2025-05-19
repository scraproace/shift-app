import streamlit as st

from module.db import DBController
from module.page import show_home_page, show_place_page, show_shift_page, show_setting_page, show_login_page, show_create_account_page


def main():
    """
    メイン関数。シフト管理アプリケーションのエントリーポイント。
    この関数は、データベースコントローラを初期化し、ユーザーのログイン状態に応じて
    適切なメニューを表示します。選択されたメニューに基づいて、対応するページを表示します。
    """
    db = DBController()

    st.title('シフト管理')

    if 'user_id' in st.session_state:
        menu = {
            'ホーム': show_home_page,
            '勤務先': show_place_page,
            'シフト': show_shift_page,
            '設定': show_setting_page,
        }
    else:
        menu = {
            'ログイン': show_login_page,
            'アカウント作成': show_create_account_page,
        }

    choice = st.sidebar.selectbox('メニュー', list(menu.keys()))
    menu[choice](db)


if __name__ == '__main__':
    main()
