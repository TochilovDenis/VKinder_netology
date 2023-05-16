# импорты
from vk_config import db_url_object
import sqlalchemy as sql
import sqlalchemy.exc
from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import sessionmaker


"""
Создает таблицы в БД
"""

# Подключение к БД

DSN = db_url_object

Base = declarative_base()

engine = sql.create_engine(DSN)
Session = sessionmaker(bind=engine)

try:
    session = Session()
    connection = engine.connect()
except sqlalchemy.exc.OperationalError:
    print('\nОшибка подключения к базе данных!')
    exit('Пожалуйста, проверьте, запущен SQL сервер?')


class BotUser(Base):
    """
    Таблица bot_user - основная
    """
    __tablename__ = "bot_user"
    id_bot_user = sql.Column(sql.Integer,
                             primary_key=True,
                             autoincrement=True,
                             nullable=False)
    bot_user_vk_id = sql.Column(sql.Integer,
                                unique=True,
                                nullable=False)

    def __repr__(self):
        return f'{self.id_bot_user} {self.bot_user_vk_id}'


class FavoriteUser(Base):
    """
    Таблица favorites_list - Избранное
    """
    __tablename__ = 'favorites_list'
    id_favorites = sql.Column(sql.Integer,
                              primary_key=True,
                              autoincrement=True,
                              nullable=False)
    vk_user_id = sql.Column(sql.Integer,
                            unique=True,
                            nullable=False)
    vk_user_url = sql.Column(sql.String)

    bot_user_vk_id = sql.Column(sql.Integer,
                                sql.ForeignKey
                                ('bot_user.bot_user_vk_id',
                                 ondelete='CASCADE')
                                )

    def __repr__(self):
        return f'{self.vk_user_url}'


class BlackList(Base):
    """
    Таблица black_list - Черный список
    """
    __tablename__ = 'black_list'

    id_black_list = sql.Column(sql.Integer,
                               primary_key=True,
                               autoincrement=True,
                               nullable=False)
    vk_user_id = sql.Column(sql.Integer,
                            unique=True,
                            nullable=False)
    vk_user_url = sql.Column(sql.String)

    bot_user_vk_id = sql.Column(sql.Integer,
                                sql.ForeignKey
                                ('bot_user.bot_user_vk_id',
                                 ondelete='CASCADE')
                                )

    def __repr__(self):
        return f'{self.vk_user_url}'


# Функции для работы с БД
def add_bot_user(id_vk):
    """
    Добавляет нового пользователя бота в БД
    :param id_vk: int
    :return: Boolean
    """
    session.add(BotUser(bot_user_vk_id=id_vk))
    session.commit()

    return True


def check_if_bot_user_exists(id_vk):
    """
    Проверяет наличие пользователя бота в БД
    :param id_vk: int
    :return: str
    """
    result = session.query(BotUser).filter_by(bot_user_vk_id=id_vk).first()
    return result


def add_new_match_to_favorites(*args):
    """
    Добавляет пользователя в Избранное
    vk_user_id: int
    vk_user_url: str
    bot_user_vk_id: int
    :return: Boolean
    """
    vk_user_id, bot_user_vk_id, vk_user_url = args

    if check_if_match_exists(vk_user_id)[0] is not None:
        return False

    new_entry = FavoriteUser(
        vk_user_id=vk_user_id,
        vk_user_url=vk_user_url,
        bot_user_vk_id=bot_user_vk_id
    )

    session.add(new_entry)
    session.commit()

    return True


def add_new_match_to_black_list(*args):
    """
    Добавляет пользователя в Черный список
    vk_user_id: int
    vk_user_url: str
    bot_user_vk_id: int
    :return: Boolean
    """
    vk_user_id, bot_user_vk_id, vk_user_url = args

    if check_if_match_exists(vk_user_id)[1] is not None:
        return False

    new_entry = BlackList(
        vk_user_id=vk_user_id,
        vk_user_url=vk_user_url,
        bot_user_vk_id=bot_user_vk_id
    )

    session.add(new_entry)
    session.commit()

    return True


def delete_match_from_black_list(vk_id):
    """
    Удаляет записи из черного списка по bot_user_id
    :param vk_id: int
    """
    session.\
        query(BlackList)\
        .filter_by(bot_user_vk_id=vk_id)\
        .delete(synchronize_session="fetch")

    session.commit()


def delete_match_from_favorites_list(vk_id):
    """
    Удаляет записи из Избранного и Фото по bot_user_id
    :param vk_id: int
    """
    session.\
        query(FavoriteUser)\
        .filter_by(bot_user_vk_id=vk_id)\
        .delete(synchronize_session='fetch')

    session.commit()


def check_if_match_exists(id_vk):
    """
    Проверяет наличие пользователя в избранном и черном списке
    :param id_vk: int
    :return: tuple
    """
    favorite_list = session.query(FavoriteUser.vk_user_id).filter_by(
        vk_user_id=id_vk).first()
    black_list = session.query(BlackList.vk_user_id).filter_by(
        vk_user_id=id_vk).first()
    return favorite_list, black_list


def show_all_favorites(vk_user_id):
    """
    Выводит избранное текущему пользователя бота
    :param vk_user_id: int
    :return: all_favorites: list
    """
    all_favorites = session.\
        query(FavoriteUser.vk_user_url)\
        .filter(vk_user_id == FavoriteUser.bot_user_vk_id).all()

    return all_favorites


def show_all_blacklisted(vk_user_id):
    """
    Выводит черный список текущему пользователю бота
    :param vk_user_id: int
    :return all_blacklisted: list
    """
    all_blacklisted = session.\
        query(BlackList.vk_user_url)\
        .filter(BlackList.bot_user_vk_id == vk_user_id).all()

    return all_blacklisted


if __name__ == '__main__':
    Base.metadata.create_all(engine)