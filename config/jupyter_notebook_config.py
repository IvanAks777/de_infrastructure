# Configuration file for jupyter-notebook.

c = get_config()

# Отключаем запрос токена (т.е. пустой токен)
c.NotebookApp.token = ''

# Отключаем запрос пароля
c.NotebookApp.password = ''

# Не открывать браузер при запуске (особенно в контейнере)
c.NotebookApp.open_browser = False

# Разрешаем подключения по всем интерфейсам
c.NotebookApp.ip = '0.0.0.0'
