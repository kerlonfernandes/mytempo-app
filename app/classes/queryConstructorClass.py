import mysql.connector

#ESTA CLASSE DE CONSULTAS ESTÁ EM DESENVOLVIMENTO, PODE NÃO TER TODOS OS TRATAMENTOS DE ERROS NECESSÁRIOS PARA RETORNAR AS DEVIDAS MENSAGENS PARA IDENTIFICAR OS ERROS

class Database:
    def __init__(self, host, user, password, database, messages=False) -> None:
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.messages = messages
        self.results = []
        self.info = {
            "status": "",
            "connection": "",
            "query": "",
            "affected_rows": "",
            "errors": "",
            "has_changed": ""
        }
        self.conn = None
        self.cursor = None

    def createConn(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )

        except Exception as e:
            if self.messages:
                self.info['status'] = "error"
                self.info['errors'] = str(e)
                print(self.info)
            return None
        
    def executeQuery(self, query):

            if self.conn.is_connected():
                self.cursor = self.conn.cursor()
                self.cursor.execute(query)
                self.results = self.cursor.fetchall()
                self.info['affected_rows'] = self.cursor.rowcount
                self.info['query'] = query
                self.info['connection'] = str(self.conn)
                self.info['status'] = "success"
                self.info['errors'] = None
                self.info['has_changed'] = "not"
                if self.messages == True:
                    print(self.info)
                return self.results

            else:
                self.info['affected_rows'] = self.cursor.rowcount
                self.info['query'] = query
                self.info['connection'] = str(self.conn)
                self.info['status'] = "error"
                self.info['errors'] = "Connection not active. You need to call the func. CreateConn() before."

                if self.messages:
                    print(self.info)
                    
                return None



    def executeNonQuery(self, query):

        try:
            if self.conn:
                if self.conn.is_connected():
                    self.cursor = self.conn.cursor()
                    self.cursor.execute(query)
                    self.info['affected_rows'] = self.cursor.rowcount
                    self.info['query'] = query
                    self.info['connection'] = str(self.conn)
                    self.info['status'] = "success"
                    self.info['errors'] = None
                    self.info['has_changed'] = "yes"
                    self.conn.commit()
                    if self.messages == True:
                        print(self.info)


                else:
                    self.info['affected_rows'] = self.cursor.rowcount
                    self.info['query'] = query
                    self.info['connection'] = str(self.conn)
                    self.info['status'] = "error"
                    self.info['errors'] = "Connection not active."

                    if self.messages:
                        print(self.info)
                        
                    return None
            else:
                if self.cursor:
                    self.info['affected_rows'] = self.cursor.rowcount
                    self.info['query'] = query
                    self.info['connection'] = str(self.conn)
                    self.info['status'] = "error"
                    self.info['errors'] = "You need to call the func. CreateConn() before."

                    if self.messages:
                        print(self.info)
                        
                    return None
                else: 
                    self.info['affected_rows'] = 0
                    self.info['query'] = query
                    self.info['connection'] = str(self.conn)
                    self.info['status'] = "error"
                    self.info['errors'] = "You need to call the func. CreateConn() before."
        except ConnectionError:
            self.info['errors'] = "Connection not active."
            if self.messages:
                    print(self.info['errors'])


        


    def killConnection(self):
        if self.conn.is_connected():
            self.cursor.close()
            self.conn.close()
            self.cursor = None
            self.conn = None
             


