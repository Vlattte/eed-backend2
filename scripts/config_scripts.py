import os.path

def config_checker():
    """ проверяет наличие нужных файлов конфигурации """    
    if os.path.exists("configs\db_connection.yaml"):        
        return
    
    print("[ERROR] отсутствует файл конфигурации базы данных db_connection.yaml в папке configs")
    print("[HINT] правило его написание находится в файле README.md")
    with open("configs/db_connection.yaml", encoding="utf-8", mode="w") as db_connection:
        db_connection.write('connect_params:\n') 
        db_connection.write('  user: "vuc" # имя пользователя\n')
        db_connection.write('  database: "vuc" # имя базы данных\n')
        db_connection.write('  password: "123456" # пароль от базы данных\n')
        db_connection.write('  host: "localhost" # адрес хоста\n')
        db_connection.write('  port: 5432 # порт')