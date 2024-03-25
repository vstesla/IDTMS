import pymysql
host = "localhost"
user = "root"
password = "123456"
database = "idtms"
charset = "utf8"
port = 3306
db = pymysql.connect(host=host, user=user, password=password, database=database, charset=charset, port=port)
cur = db.cursor()
user_creat ="""
                CREATE TABLE IF NOT EXISTS User(
                  `id` INT auto_increment PRIMARY KEY,
                  `username` varchar(255) DEFAULT '',
                  `password` varchar(255) DEFAULT '',
                  `phone` varchar(255) DEFAULT ''
                ) ENGINE=innodb DEFAULT CHARSET=utf8;
           """
cur.execute(user_creat)
data_creat ="""
                CREATE TABLE IF NOT EXISTS Images(
                `iid` INT auto_increment PRIMARY KEY,
                `date` DATE DEFAULT NULL,
                `time` TIME DEFAULT NULL,
                `iname` VARCHAR(255) DEFAULT '',
                `temp` VARCHAR(255) DEFAULT '',
                `dvcid` VARCHAR(255) DEFAULT '',
                `status` VARCHAR(255) DEFAULT ''
                ) ENGINE=innodb DEFAULT CHARSET=utf8;
            """
cur.execute(data_creat)
