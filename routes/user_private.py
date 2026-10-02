from aiogram import F, types, Router
from aiogram.filters import CommandStart, Command

from decorators.auth import user_required, auth
from services.logger import log_write
from services.backend_api_connect import get_api
from variables.users import oltshub_tokens
from variables.messages import start_message


u_router = Router()


@u_router.message(CommandStart())
async def start_cmd(message: types.Message):
    '''
    Команда /start
    '''
    await message.answer(start_message)


@u_router.message(Command('menu'))
@user_required
async def menu_cmd(message: types.Message):
    await message.answer('Menu:')


@u_router.message(Command('login'))
async def user_login(message: types.Message):
    try:
        user_input = message.text.split()
        result = auth(user_input[1], message.from_user.id)

        if result['result'] == 'error':
            log_write(f"User: {user_input[1]} ({message.from_user.id}); Action: AUTH; Message: {result['message']}")
            await message.answer(f"{result['message']}")
        else:
            oltshub_tokens.update({str(message.from_user.id): result['token']})
            log_write(f'User: {user_input[1]} ({message.from_user.id}); Action: AUTH; Message: Успешный вход в систему')
            await message.answer('Успешный вход в OLTsHUB')

    except IndexError:
        await message.answer('Введите <code>/login ВАШ_ЛОГИН</code>')


@u_router.message(F.text)
@user_required
async def find_onu(message: types.Message):
    user_input = message.text.lower().replace(' ','') \
                                     .replace(':', '') \
                                     .replace('.', '') \
                                     .replace('hwtc', '48575443') \
                                     .replace('-', '')

    result = ''

    if len(user_input) == 12 or len(user_input) == 16:

        #req = findonu(user_input, oltshub_tokens[str(message.from_user.id)])
        URL = f"/api/onuinfo/{user_input}"
        req = get_api(URL, oltshub_tokens[str(message.from_user.id)])
        try:
            if isinstance(req, dict):
                if req['result'] == 'error':
                    await message.answer(req['message'])

                else:
                    for r in req['onu']:
                        result += f'''
<b>ONU:</b> {r['mac/sn']}
<b>Descr:</b> {r['onudescr']}
<b>Статус:</b> {r['iface_state']}
<b>ОЛТ:</b> {r['oltname']}
<b>IP ОЛТа:</b> {r['oltip']}
<b>Порт:</b> {r['iface_name']}<b> ID:</b> {r['onuid']}
<b>ONU RX:</b> {r['level_onu_rx']}
<b>OLT RX:</b> {r['level_olt_rx']}
'''

                    await message.answer(result)

        except KeyError:
            await message.answer(f"У вас нет доступа или ваш токен просрочен. ❌\nВойдите с помощью команды /login ВАШ ЛОГИН")

    else:
        await message.answer("Неправильный Мак или Серийник ONU!")