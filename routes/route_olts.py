from aiogram import F, types, Router
from aiogram.filters import Command, or_f

from decorators.auth import user_required
from services.logger import log_write
from services.backend_api_connect import get_api
from variables.users import oltshub_tokens
from kbds.inline import get_callback_btns
from kbds import reply
from services.olt_info import get_port_status, get_olts_list, get_olt_info

olts_router = Router()


@olts_router.message(or_f(Command('olts_list'), (F.text.lower() == 'список олтов')))
@user_required
async def olts_list(message: types.Message):
    
    olts_list = get_olts_list(oltshub_tokens[str(message.from_user.id)])

    for o in olts_list:
        await message.answer(o, reply_markup=reply.del_kbd)

    await message.answer('Для просмотра информации об ОЛТе, введите <code>/olt_info (id)</code>')


@olts_router.message(or_f(Command('olt_info'), (F.text.lower() == 'olt_info')))
@user_required
async def olt_info(message: types.Message):
    '''
    Команда просмотра информации об ОЛТе
    '''
    result = ''
    try:
        olt_id = message.text.split()[-1]

        result = get_olt_info(olt_id, oltshub_tokens[str(message.from_user.id)])

        await message.answer(result, reply_markup=get_callback_btns(btns={
            'Опросить ОЛТ': f'update_{olt_id}',
            'Показать порты': f'showports_{olt_id}',
            })
        )
    except:
        await message.answer('Ошибка! Введите ID ОЛТа.')


@olts_router.message(or_f(Command('ports_list'), (F.text.lower() == 'ports_list')))
@user_required
async def ports_list(message: types.Message):
    '''
    Команда просмотра портов
    '''
    result = ''
    oltid = message.text.split()[-1]
    URL = f"/api/oltinfo/{oltid}"
    olt_info = get_api(URL, oltshub_tokens[str(message.from_user.id)])

    result += f'''
<b>ID:</b> {olt_info['id']}
<b>Hostname:</b> {olt_info['hostname']}
<b>IP Address:</b> {olt_info['ip_address']}
<b>Описание:</b> {olt_info['descr']}

<b>Порты:</b>
'''

    btns = {}
    for p in olt_info['ports']:
        btns.update({p: f'portstatus'})

    await message.answer(result, reply_markup=get_callback_btns(btns=btns)
    )


@olts_router.callback_query(F.data.startswith('showports_'))
async def ports_list_btn(callback: types.CallbackQuery):
    '''
    Кнопка просмотра портов
    '''
    result = ''
    oltid = callback.data.split('_')[-1]
    URL = f"/api/oltinfo/{oltid}"
    olt_info = get_api(URL, oltshub_tokens[str(callback.from_user.id)])

    result += f'''
<b>ID:</b> {olt_info['id']}
<b>Hostname:</b> {olt_info['hostname']}
<b>IP Address:</b> {olt_info['ip_address']}
<b>Описание:</b> {olt_info['descr']}

<b>Порты:</b>
'''

    btns = {}
    for p in olt_info['ports']:
        btns.update({p: f'portstatus_{oltid}_{p}'})

    await callback.answer()
    await callback.message.answer(result, reply_markup=get_callback_btns(btns=btns))


@olts_router.message(or_f(Command('olt_update'), (F.text.lower() == 'olt_update')))
@user_required
async def olt_update(message: types.Message):
    '''
    Команда проса ОЛТа
    '''
    await message.answer('''
Отправлен запрос на опрос ОЛТа, 
дождитесь завершения команды. 
Время выполнения может быть от 10 секунд, до 3 минут, 
в зависимости от ОЛТа.
''')
    oltid = message.text.split()[-1]
    URL = f"/api/olts/oltupdate/{oltid}"
    result = get_api(URL, oltshub_tokens[str(message.from_user.id)])
    log_write(f'User: {message.from_user.id}; Action: OLT_UPDATE; Message: {result["message"]} (olt id: {oltid})')

    await message.answer(result['message'])


@olts_router.callback_query(F.data.startswith('update_'))
async def olt_update_btn(callback: types.CallbackQuery):
    '''
    Кнопка опроса ОЛТа
    '''
    await callback.message.answer('''
Отправлен запрос на опрос ОЛТа, 
дождитесь завершения команды. 
Время выполнения может быть от 10 секунд, до 3 минут, 
в зависимости от ОЛТа.
''')
    oltid = callback.data.split('_')[-1]
    URL = f"/api/olts/oltupdate/{oltid}"
    result = get_api(URL, oltshub_tokens[str(callback.from_user.id)])

    await callback.answer()
    await callback.message.answer(result['message'])


@olts_router.message(or_f(Command('port_status'), (F.text.lower() == 'port_status')))
@user_required
async def port_status(message: types.Message):
    '''
    Команда просмотра статуса pon порта
    '''
    try:
        await message.answer('''
Отправлен запрос на просмотр статуса pon порта, 
дождитесь завершения команды. 
Время выполнения может быть от 10 секунд, до 3 минут, 
в зависимости от ОЛТа.
''')
        
        oltid = message.text.split()[1]
        port = message.text.split()[2].replace('/', '.')

        port_info = get_port_status(oltid, port, oltshub_tokens[str(message.from_user.id)])

        if len(port_info) == 0:
            await message.answer('На порту нет ОНУ.')
        else:    
            for p in port_info:
                await message.answer(p)

    except:
        await message.answer('Ошибка выполнения команды!')


@olts_router.callback_query(F.data.startswith('portstatus_'))
async def port_status_btn(callback: types.CallbackQuery):
    '''
    Кнопка просмотра статуса pon порта
    '''
    try:
        await callback.answer()
        await callback.message.answer('''
Отправлен запрос на просмотр статуса pon порта, 
дождитесь завершения команды. 
Время выполнения может быть от 10 секунд, до 3 минут, 
в зависимости от ОЛТа.
''')
        oltid = callback.data.split('_')[1]
        port = callback.data.split('_')[2].replace('/', '.')

        port_info = get_port_status(oltid, port, oltshub_tokens[str(callback.from_user.id)])
        if len(port_info) == 0:
            await callback.answer('На порту нет ОНУ.')
        else:
            for p in port_info:
                await callback.message.answer(p)

    except:
        await callback.message.answer('Ошибка выполнения команды!')
