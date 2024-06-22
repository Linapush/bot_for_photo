# from src.state.login import LoginState
from aiogram.fsm.state import StatesGroup, State

class FilesStates(StatesGroup):
    
    waiting_for_year = State()

    waiting_for_month = State()
    
    waiting_for_day = State()