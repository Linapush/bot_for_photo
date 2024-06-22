# from src.state.login import LoginState
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

class FilesStates(StatesGroup):
    
    waiting_for_year = State()

    waiting_for_month = State()
    
    waiting_for_day = State()

async def update_state_with_file_info(state: FSMContext, file_info: dict) -> None:
    await state.update_data(
        files=file_info,
        current_index=0,
    )