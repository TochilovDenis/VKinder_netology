# Токен для fronted (токен сообщества)
community_token = ''
# Токен для backend (токен пользовательского приложения)
access_token = ''

vkapi_version = '5.131'
redirect_uri = 'http://localhost/callback'
scope = 'photos, wall, groups, offline'
base_url = 'https://api.vk.com/method/'
base_profile_url = "https://vk.com/id"

# Соединение БД
db_url_object = "postgresql://postgres: @localhost:5432/vkinder"