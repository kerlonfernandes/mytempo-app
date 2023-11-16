from app.configs.config import HOST, USER, PASSWORD, DATABASE, localDatabaseDir, FormatarHora, format_timedelta
import mysql.connector
import sqlite3


class MySQLQuerys:
    def __init__(self, host, user, password, database) -> None:
        
        try:
            self.conn = mysql.connector.connect(host=host,
                                                user=user,
                                                password=password,
                                                database=database)
            self.cursor = self.conn.cursor()    
            self.conditions = []
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)
            

    def select(self, col=None, table=None, condition=None, andcondition=None):
        try:
            selectAllQuery = f"SELECT {col} FROM {table}"

            if condition:
                selectAllQuery += f" WHERE {condition}"
                if andcondition:
                    selectAllQuery += f" AND {andcondition}"

            # try:
            self.cursor.execute(selectAllQuery)
            rows = self.cursor.fetchall()
            return rows
        
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)
        
        
    def insert(self, table=None, fields=None ,*values):
        try:
            if table is None or len(values) == 0:
                return
            values_str = ", ".join(f"'{value}'" for value in values)

            query = f"INSERT INTO {table} ({fields}) VALUES ({values_str})"
            self.cursor.execute(query)
            # self.conn.commit()
            print('Dado inserido com sucesso!', values_str)
            print("Query:", query)
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)
        
    def delete(self, table, condition=None, andcondition=None):
        try:
            query = f"DELETE FROM {table}"
            
            if condition is not None:
                query+= f' WHERE {condition}'
                if andcondition is not None:
                    query += f" AND {andcondition}"
                    
            self.cursor.execute(query)
            # self.conn.commit()
            print("Deletado com sucesso!")
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)
       
        
    def update(self, table, campo, newValue , condition):
        query = f"UPDATE {str(table)} SET {str(campo)} = '{str(newValue)} WHERE {condition}'"
        self.cursor.execute(query)
        print("alterado com sucesso!")
        


# SELECT * FROM `equipamentos` WHERE `id` = 99 AND idprova = 75;


class LocalBaseQuerys:
    def __init__(self, database):
        self.conn = sqlite3.connect(database)
        self.cursor = self.conn.cursor()
        self.conditions = []

    def offSelect(self, col=None, table=None, condition=None, andcondition=None):
        try:
            selectAllQuery = f"SELECT {col} FROM {table}"

            if condition:
                selectAllQuery += f" WHERE {condition}"
                if andcondition:
                    selectAllQuery += f" AND {andcondition}"

            # try:
            self.cursor.execute(selectAllQuery)
            rows = self.cursor.fetchall()

            return rows
        
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)

    def offInsert(self, table=None, fields=None ,*values):
        try:
            if table is None or len(values) == 0:
                return
            values_str = ", ".join(f"'{value}'" for value in values)

            query = f"INSERT INTO {table} ({fields}) VALUES ({values_str})"
            self.cursor.execute(query)
            self.conn.commit()
            print('Dado inserido com sucesso!', values_str)
            print("Query:", query)
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)

    #FORMATO DA QUERY DE INSERT

    # querySqlite = LOCAL_QUERY.insert('equipamentos', 'equipamento, checkpoint, idprova, hora, identificacao, NomeProva, NomeCheck, NomeEquipamento, atualizacao_hora', 96, 185, 99, '08:00:00', 0, 'TESTE EQUIPAMENTO', 'LARGADA', 'READER 1', '13:52:15 26/06/2023')


    def offUpdate(self, table, campo, newValue, condition):
        query = f"UPDATE {table} SET {campo} = '{newValue}' WHERE {condition}"
        self.cursor.execute(query)
        print("Alterado com sucesso!")


    def offDelete(self, table, condition=None, andcondition=None):
        try:
            query = f"DELETE FROM {table}"
            
            if condition is not None:
                query+= f' WHERE {condition}'
                if andcondition is not None:
                    query += f" AND {andcondition}"
                    
            self.cursor.execute(query)
            self.conn.commit()
            print("Deletado com sucesso!")
        except Exception as e:
            print('Ocorreu um erro! Err: ->', e)

    def offUpdate(self, table, campo, newValue, condition):
        query = f"UPDATE {table} SET {campo} = '{newValue}' WHERE {condition}"
        self.cursor.execute(query)
        print("Alterado com sucesso!")



LOCAL_QUERY = LocalBaseQuerys(localDatabaseDir)
MYSQL_QUERY = MySQLQuerys(HOST, USER, PASSWORD, DATABASE) 
