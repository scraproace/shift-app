from datetime import datetime, time, timedelta
import os

# from dotenv import load_dotenv  # ローカルで行う場合
from supabase import create_client, Client

from schemas.user import UserSchema, InsertUserSchema, UpdateUserSchema
from schemas.place import PlaceSchema, InsertPlaceSchema
from schemas.shift import ShiftSchema, InsertShiftSchema


# load_dotenv()  # ローカルで行う場合
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')


class DBController():
    def __init__(self):
        self.supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

    def add_user(self, user: InsertUserSchema) -> bool:
        """ユーザー追加"""
        response = self.supabase.table('users').select('id').eq('username', user.username).eq('is_valid', True).limit(1).execute()
        if response.data:
            return False

        insert_response = self.supabase.table('users').insert(user.model_dump()).execute()
        return bool(insert_response.data)

    def update_user(self, user: UpdateUserSchema) -> bool:
        """ユーザー情報更新"""
        response = self.supabase.table('users').select('id').neq('id', user.id).eq('username', user.username).eq('is_valid', True).limit(1).execute()
        if response.data:
            return False

        self.supabase.table('users').update(user.model_dump()).eq('id', user.id).execute()
        return True

    def get_user(self, id: int) -> UserSchema:
        """ユーザー情報取得"""
        response = self.supabase.table('users').select('*').eq('id', id).limit(1).execute()
        return UserSchema.model_validate(response.data[0])

    def login(self, username: str, password: str) -> UserSchema | None:
        """ユーザーログイン"""
        response = self.supabase.table('users').select('*').eq('username', username).eq('password', password).eq('is_valid', True).limit(1).execute()

        if response.data:
            return UserSchema.model_validate(response.data[0])
        return None

    def add_place(self, place: InsertPlaceSchema) -> bool:
        """勤務先追加"""
        response = self.supabase.table('places').select('id').eq('user_id', place.user_id).eq('name', place.name).eq('is_valid', True).limit(1).execute()
        if response.data:
            return False

        self.supabase.table('places').insert(place.model_dump()).execute()
        return True

    def get_places(self, user_id: int) -> list[PlaceSchema]:
        """勤務先情報取得"""
        response = self.supabase.table('places').select('*').eq('user_id', user_id).eq('is_valid', True).order('id').execute()
        return [PlaceSchema.model_validate(place) for place in response.data]

    def delete_place(self, id: int) -> None:
        """勤務先削除"""
        self.supabase.table('places').update({'is_valid': False}).eq('id', id).execute()

    def add_shift(self, shift: InsertShiftSchema) -> bool:
        """シフト追加"""
        or_condition = (
            f"and(end_datetime.gt.{shift.start_datetime},start_datetime.lt.{shift.end_datetime})"
        )
        response = self.supabase.table('shifts').select('id').eq('user_id', shift.user_id).eq('place_id', shift.place_id).eq('is_valid', True).or_(or_condition).execute()
        if response.data:
            if shift.is_update:
                for delete_target_shift in response.data:
                    self.supabase.table('shifts').update({'is_valid': False}).eq('id', delete_target_shift['id']).execute()
            else:
                return False

        self.supabase.table('shifts').insert(shift.model_dump()).execute()
        return True

    def get_shifts(self, user_id: int) -> list[ShiftSchema]:
        """シフト情報取得"""
        response = self.supabase.table('shifts').select('*, places(name, wage, has_night_wage, closing_day)').eq('user_id', user_id).eq('is_valid', True).order('start_datetime').execute()
        shifts = response.data
        for shift in shifts:
            shift['start_datetime'] = datetime.fromisoformat(shift['start_datetime'])
            shift['end_datetime'] = datetime.fromisoformat(shift['end_datetime'])
            shift['break_time'] = time.fromisoformat(shift['break_time'])
            shift['place'] = shift['places']['name']
            shift['wage'] = shift['places']['wage']
            shift['has_night_wage'] = shift['places']['has_night_wage']
            shift['closing_day'] = shift['places']['closing_day']
            shift['amount'] = self._caliculate_amount(
                shift['start_datetime'],
                shift['end_datetime'],
                shift['break_time'],
                shift['wage'],
                shift['has_night_wage']
            )
            shift.pop('places')

        return [ShiftSchema.model_validate(shift) for shift in shifts]

    def delete_shift(self, id: int) -> None:
        """シフト削除"""
        self.supabase.table('shifts').update({'is_valid': False}).eq('id', id).execute()

    def _caliculate_amount(self, start_datetime: datetime, end_datetime: datetime, break_time: time, wage: int, has_night_wage) -> int:
        """シフトの金額を計算"""
        if has_night_wage:
            day_minutes = 0
            night_minutes = 0
            current_datetime = start_datetime

            while current_datetime < end_datetime:
                if current_datetime.hour >= 22 or current_datetime.hour < 5:
                    night_minutes += 1
                else:
                    day_minutes += 1
                current_datetime += timedelta(minutes=1)

            break_minutes = break_time.hour * 60 + break_time.minute
            if break_minutes > 0:
                if day_minutes > night_minutes:
                    if break_minutes < day_minutes:
                        day_minutes -= break_minutes
                    else:
                        day_minutes = 0
                        night_minutes -= break_minutes - day_minutes
                else:
                    if break_minutes < night_minutes:
                        night_minutes -= break_minutes
                    else:
                        night_minutes = 0
                        day_minutes -= break_minutes - night_minutes

            amount = round(wage * day_minutes / 60 + 1.25 * wage * night_minutes / 60)
        else:
            amount = round(wage * (end_datetime - start_datetime - timedelta(hours=break_time.hour, minutes=break_time.minute)).seconds / 3600)

        return amount
