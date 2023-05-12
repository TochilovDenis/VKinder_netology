import vk_apps
import vk_interface
import vk_models
from vk_api.longpoll import VkEventType
from datetime import datetime as dt


def main():
    dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
    print(f'\n{dtime}: Vkinder service started...', end='')

    vk_api = vk_apps.VKTools()
    vkbot = vk_interface.VkBotInterface()

    bot_profile_info = {}
    stack = []

    print('OK')

    def add_user_to_db(bot_user_id, flag_list):
        """
        Добавляет информацию о пользователе в Избранное или Черный список
        flag_list True - добавляет в Избранное
        flag_list False - добавляет в Черный список
        :param bot_user_id: bot_user_id
        :param flag_list: Boolean
        :return: Boolean
        """

        first_name, last_name, url, user_attachment = stack.pop()
        vk_user_id = int(url.split('id')[1])

        if flag_list and vk_models.check_if_match_exists(vk_user_id)[0] is None:

            vk_models.add_new_match_to_favorites(
                vk_user_id,
                bot_user_id,
                first_name,
                last_name, url
            )
            vk_models.add_photo_of_the_match(
                user_attachment,
                vk_user_id,
                bot_user_id
            )

            d_time = dt.now().strftime('%d.%m.%Y %H:%M:%S')

            print(f'{d_time}: пользователь id{event.user_id} '
                  f'добавлен id{vk_user_id} в Избранное')

            vkbot.message_send(event.user_id, "Добавлено в Избранное")

            return True

        elif not flag_list and \
                vk_models.check_if_match_exists(vk_user_id)[1] is None:

            vk_models.add_new_match_to_black_list(
                vk_user_id,
                bot_user_id,
                first_name,
                last_name, url
            )
            vk_models.add_photo_of_the_match(
                user_attachment,
                vk_user_id,
                bot_user_id
            )

            vkbot.message_send(event.user_id, "Добавлено в Черный список")

            d_time = dt.now().strftime('%d.%m.%Y %H:%M:%S')
            print(f'{d_time}: пользователь id{event.user_id} '
                  f'добавлен id{vk_user_id} в Черный список')

            return True
        return False

    for event in vkbot.longpoll.listen():
        if event.type == VkEventType.MESSAGE_NEW:
            if event.to_me:
                message = event.text.lower()

                if message in ('привет', 'старт'):
                    dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                    print(f'{dtime}: пользователь id{event.user_id} подключен.')

                    # запросить всю информацию от пользователя бота
                    res = vk_api.get_profile_info(event.user_id)
                    name_bot_user, sex, bdate, relation, city = res

                    # заполняем словарь для поиска
                    bot_profile_info['sex'] = sex
                    bot_profile_info['bdate'] = bdate
                    bot_profile_info['relation'] = relation
                    bot_profile_info['city'] = city

                    vkbot.message_send(event.user_id, f'Привет, {name_bot_user}!\n'
                                                      f'Наберите "help"')

                    # добавляем пользователя в БД, если его там нет
                    if vk_models.check_if_bot_user_exists(event.user_id) is None:
                        vk_models.add_bot_user(event.user_id)

                    # если отсутствуют город и дата рождения
                    if not city:
                        # проверяем city в словаре
                        city = bot_profile_info.get('city')
                        if not city:
                            vkbot.message_send(
                                event.user_id,
                                f'Не указан город в Вашем профиле.\n'
                                f'Наберите "город название_города".\n'
                                f'Или укажите его в Вашем профиле ВК.'
                            )
                    elif not bdate:
                        # проверяем День Рождения в словаре
                        bdate = bot_profile_info.get('bdate')
                        if not bdate:
                            vkbot.message_send(
                                event.user_id,
                                f'Не указана дата рождения в Вашем профиле.\n'
                                f'Наберите "год рождения год_рождения "'
                                f'(4 цифры).\n'
                                f'Или укажите его в Вашем профиле ВК')
                    else:
                        vkbot.message_send(event.user_id,
                                           f'Нажми "Поиск" для старта.')

                elif message == "избранное":
                    for user in vk_models.show_all_favorites(event.user_id):
                        msg = f'{user[0]} {user[1]}\n{user[2]}'

                        vkbot.message_send(event.user_id,
                                           message=msg,
                                           attachment=user[3])

                elif message == "черный список":
                    for user in vk_models.show_all_blacklisted(event.user_id):
                        msg = f'{user[0]} {user[1]}\n{user[2]}'

                        vkbot.message_send(event.user_id,
                                           message=msg,
                                           attachment=user[3])

                elif message == "в избранное":
                    add_user_to_db(event.user_id, True)

                elif message == "игнорировать":
                    add_user_to_db(event.user_id, False)

                elif message == "поиск":
                    # читаем данные пользователя из словаря,
                    # созданного при старте бота
                    city = bot_profile_info.get('city')
                    sex = bot_profile_info.get('sex')
                    bdate = bot_profile_info.get('bdate')
                    relation = bot_profile_info.get('relation')

                    # поиск людей в соответствии с данными
                    # пользователя бота
                    data = vk_api.search_users(city, sex, bdate, relation)

                    if data:
                        stack.append(data)
                        dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                        print(f'{dtime}: '
                              f'пользователь id{event.user_id} '
                              f'результат поиска: {data}')

                        msg = f'{data[0]} {data[1]}\n{data[2]}'

                        vkbot.message_send(event.user_id,
                                           message=msg,
                                           attachment=data[3])

                    elif not data:
                        # если данных нет (пришел пустой список)
                        dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                        print(f'{dtime}: Поиск завершен, количество записей 0')
                        vkbot.message_send(event.user_id,
                                           message='Поиск завершен, количество записей 0')

                    elif 'Error' in data:
                        dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                        print(f'{dtime}: Ошибка сервиса VK')
                        vkbot.message_send(event.user_id,
                                           message='Ошибка сервиса VK')

                elif message == 'удалить черный список':
                    vk_models.delete_match_from_black_list(event.user_id)
                    dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                    print(f'{dtime}: пользователь id{event.user_id} '
                          f'очищен от Черного списка')
                    vkbot.message_send(event.user_id, 'Черный список очищен')

                elif message == 'удалить избранное':
                    vk_models.delete_match_from_favorites_list(event.user_id)
                    datatime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
                    print(f'{datatime}: пользователь id{event.user_id} '
                          f'очищен от Избранного списка')
                    vkbot.message_send(event.user_id, 'Избранное очищен')

                elif message.startswith('город '):
                    city = message.split()[1]
                    bot_profile_info['city'] = city.title()
                    vkbot.message_send(event.user_id,
                                       f'Ваш город {city.title()}\n'
                                       f'Нажмите "Поиск" для продолжения')

                elif message.startswith('год рождения'):
                    bdate = message.split()[2]
                    bot_profile_info['bdate'] = int(bdate)
                    vkbot.message_send(event.user_id,
                                       f'Год вашего рождения: {bdate}\n'
                                       f'Нажмите "Поиск" для продолжения')

                elif message.startswith('help'):
                    vkbot.message_send(event.user_id, 'Поиск - ищем партнера.\n'
                                                      'В избранное - добавляем в избранное партнера.\n'
                                                      'Игнорировать - добавляем партнер в игнор.\n'
                                                      'Избранное - посмотреть избранного партнера.\n'
                                                      'Черный список - посмотреть черного списка.\n'
                                                      'Удалить Избранное - удаляем из избранного.\n'
                                                      'Удалить Черный список - удаляем черного списка.\n')

                elif message in ('Пока', 'пока'):
                    vkbot.message_send(event.user_id, 'Пока!')
                else:
                    vkbot.message_send(event.user_id, "Не опознана команда")


if __name__ == '__main__':
    main()
