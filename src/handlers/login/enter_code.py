from aiohttp.client_exceptions import ClientResponseError

from aiogram import types
from aiogram.fsm.context import FSMContext

from conf.config import settings
from src.buttons.actions.getter import get_main_keyboard
from src.handlers.login.router import login_router
from src.logger import logger
from src.state.login import LoginState
from src.utils.request import do_request


@login_router.message(LoginState.enter_code)
async def enter_code(message: types.Message, state: FSMContext) -> None:
    code = message.text
    if message.from_user is None:
        await message.answer('Произошла ошибка. Попробуйте еще раз')
        logger.error('Without user')
        return

    try:
        data = await do_request(
            f'{settings.PHOTO_BACKEND_HOST}/auth/login',
            json={
                'username': message.from_user.id,
                'code': code,
            },
        )
        await state.update_data(access_token=data['access_token'])
        await state.set_state(LoginState.authorized)
        await message.answer(
            'Вы успешно авторизовались', reply_markup=get_main_keyboard(role='user')
        )
        logger.info('Авторизованы, переход к клавиатурам')

    except ClientResponseError:
        await message.answer('Код неверный.')
        logger.error('Code error')
        return
