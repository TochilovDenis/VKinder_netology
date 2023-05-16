import vk_apps
import vk_interface
import vk_msg
from datetime import datetime as dt

vk_api = vk_apps.VKTools()
vkbot = vk_interface.VkBotInterface()

bot_profile_info = {}
stack = []


def main():
    dtime = dt.now().strftime('%d.%m.%Y %H:%M:%S')
    print(f'\n{dtime}: Vkinder service started...', end='')

    print('OK')

    vk_msg.vk_message()


if __name__ == '__main__':
    main()
