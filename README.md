# eed-backend2
Перепроектированный eed-backaend

Для запуска проекта требуется:
1. прописать в консоли команду: pip install -r requirements.txt
2. если используется прокси, то не установившиеся пакеты установить с помощью команды: pip install --proxy http://адрес:порт название_библиотеки --no-build-isolation --no-use-pep517 -vv
3. запустить проект с помощью команды python server.py (если появилась надпись "SERVER ON", то все верно)
4. для возможности работы с БД, необходимо в папке configs создать файл db_connection.yaml и заполнить по следущей структуре: 

connect_params:
	user: "postgres" 			# имя пользователя
	database: "eed_backend_2"	# имя базы данных
	password: "postgres"		# пароль от базы данных	
	host: "localhost"			# адрес хоста	
	port: 5432					# порт 	