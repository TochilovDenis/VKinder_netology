import vk_config
import requests
import vk_models
from vk_models import Session


class VKTools:
    """
    Класс для работы с VKTools
    """

    def __init__(self):
        # Получение данных о пользователе
        self.vkapi = vk_config.access_token
        self.params = {
            'access_token': self.vkapi,
            'v': vk_config.vkapi_version
        }
        self.offset = 0
        self.wish_list = []
        self.black_list = []

    def get_profile_info(self, user_id):
        """
        Информация о пользователя Вконтакте.
        Посылает api запрос, используя метод users.get
        :param user_id: int
        :return: str
        """

        endpoint = f'{vk_config.base_url}users.get'
        params = {
            'user_ids': user_id,
            'fields': 'first_name,'
                      'last_name,'
                      'bdate,'
                      'sex,'
                      'city,'
                      'relation'
        }
        try:
            response = requests.get(url=endpoint,
                                    params={**params,
                                            **self.params})

            if response.status_code != 200:
                raise ConnectionError

        except ConnectionError:
            print('Ошибка соединения!')

        else:
            data = response.json()['response'][0]

            # Имя и Фамилия
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            name = f"{first_name} {last_name}"
            if not name:                        # если нет имена, то ищем фамилию
                name = data.get('last_name')

            # Дата рождения
            bdate = data.get('bdate')
            if len(bdate) > 6:
                bdate = int(bdate[-4:])
            else:
                bdate = None

            # Пол (выбираем противоположный)
            sex = (1, 2)[data.get('sex') == 2]

            # Город
            if data.get('city'):
                city = data.get('city').get('title')
            else:
                city = None

            # Семейное положение
            relation = data.get('relation')

            return name, sex, bdate, relation, city

    def search_users(self, city, sex, bdate, relation, count=30):
        """
        Информация о поиске пользователя Вконтакте.
        Посылает API запрос, используя VK API метод users.search,
        с параметрами 'count', 'sex', 'birth_year', 'has_photo', 'hometown',
        'offset'. Если профиль пользователя закрытый или пользователь находится
        в списке игнорирования (black list) или в избранном, то пользователь
        пропускается.
        Возвращает имя, фамилию, ссылку на профиль и 3 фото (полученных методом
        get_photos())
        """
        endpoint = f'{vk_config.base_url}users.search'

        session = Session()

        params = {
            'count': count,
            'sex': sex,
            'bdate': bdate,
            'has_photo': 1,
            'hometown': city,
            'relation': relation,
            'offset': self.offset
        }

        resp = requests.get(url=endpoint, params={**params,
                                                  **self.params})

        if resp.json().get('error'):
            resp_error = resp.json()['error']['error_code'], \
                resp.json()['error']['error_msg']
            error_msg = f'Код ошибки: {resp_error[0]}\n' \
                        f'Сообщение об ошибке: {resp_error[1]}'
            print(error_msg)
            return 'Ошибка'

        for row in resp.json()['response']['items']:
            self.offset += 1
            # если профиль закрытый, то пропускаем
            if row['is_closed']:
                continue

            # если пользователь в черном списке, то пропускаем
            if session.query(
                    vk_models.BlackList.vk_user_id) \
                    .filter_by(vk_user_id=row['id']) \
                    .first() is not None:
                continue

            # если пользователь в избранном, то пропускаем
            if session.query(
                    vk_models.FavoriteUser.vk_user_id) \
                    .filter_by(vk_user_id=row['id']) \
                    .first() is not None:
                continue

            photo_profile = self.get_photos(row['id'])

            return row['first_name'], row['last_name'], \
                f'{vk_config.base_profile_url}{row["id"]}', \
                photo_profile

    def get_photos(self, user_id):
        """
        Получает user_id и возвращает 3 фото с наибольшим количеством
        лайков и комментариев
        :param user_id: int
        :return: str
        """

        res = []

        endpoint = f'{vk_config.base_url}photos.get'
        params = {'owner_id': user_id,
                  'album_id': 'profile',
                  'extended': 1, }

        try:
            resp = requests.get(endpoint, params={**self.params,
                                                  **self.params,
                                                  **params})
            resp.raise_for_status()

            if resp.status_code != 200:
                raise ConnectionError

        except ConnectionError:
            print('Ошибка соединения!')

        else:
            like_score = 1
            comm_score = 3

            photos_sort = \
                lambda x: (x['likes']['count'], x['comments']['count']
                           )[x['likes']['count'] * like_score <=
                             x['comments']['count'] * comm_score]

            result = sorted(resp.json()['response']['items'],
                            key=photos_sort, reverse=True)

            for photo in result:
                res.append(f"photo{photo['owner_id']}_{photo['id']}")
                if len(res) == 3:
                    break

            return ','.join(res)