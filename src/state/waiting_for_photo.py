from aiogram.fsm.state import StatesGroup, State

class UploadPhoto(StatesGroup):
    
    waiting_for_photo = State()