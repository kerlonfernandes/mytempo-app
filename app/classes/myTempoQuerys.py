from app.classes.QueryClasses import MySQLQuerys, LocalBaseQuerys, LOCAL_QUERY
from app.configs.config import HOST, USER, PASSWORD, DATABASE, localDatabaseDir, FormatarHora, format_timedelta
import mysql.connector

    

class MyTempoQuerys(MySQLQuerys, LocalBaseQuerys):
    
    def __init__(self, host, user, password, database, localDatabase=None):
        super().__init__(host, user, password, database)

        self.MySQLQueries = MySQLQuerys(host, user, password, database)
        
        self.LocalBaseQuery = LocalBaseQuerys(localDatabase)        

        self.LocalBaseQuery = LocalBaseQuerys(localDatabase)
    
        #dados pegos no servidor
        self.idEquipamento = []
        self.idCheckpoint = []
        self.idProva  = []
        self.horaDaProva = []
        self.identificacao = []
        self.nomeProva = []
        self.nomeCheck = []
        self.nomeEquipamento = []
        self.ultimaAtualizacao = []
        self.descricaoCheck = []
        self.tituloProva = []
        self.status = ''
        

        #dados pegos no local

        self.idEquipamentoOff = []
        self.idCheckpointOff = []
        self.idProvaOff = []
        self.horaDaProvaOff = []
        self.identificacaoOff = []
        self.nomeProvaOff = []
        self.nomeCheckOff = []
        self.nomeEquipamentoOff = []
        self.ultimaAtualizacaoOff = []
        

        #dados gerais        
        self.dadosEquip = []   

    
    
    def getAllDataOfBase(self, nomeEquipamento):
        query = f"""SELECT *, eck.id AS ideq_chek FROM equipamentos_do_check AS eck
                            INNER JOIN equipamentos AS eq
                            ON eck.equipamento = eq.id
                            WHERE nomeequipamento = "{nomeEquipamento}"
                        """
        self.cursor.execute(query)
        self.dados = self.cursor.fetchall()
        
        for row in self.dados:
                            
            self.idEquipamento= row[2]

            self.idProva = row[3]
            self.nomeEquipamento = row[5]
            self.idCheckpoint = row[1]
        
        print(
            self.idProva,
            self.nomeEquipamento,
            self.idCheckpoint
        )

        print(self.dados)
        return self.dados
        
    def getLocalData(self):
        query = self.LocalBaseQuery.select('*', 'checkpoints') 
        return query


    def limpaBase(self):
        self.LocalBaseQuery.offDelete("equipamentoffline")

    def pegaEquipamentos(self):
        query = self.LocalBaseQuery.select('*', 'equipamentos')
        return query

    def getEquip(self, nome_equipamento):
        query = self.LocalBaseQuery.offSelect('*', 'equipamentos', f'NomeEquipamento = "{nome_equipamento}"')
        return query
    
    def apagaConfigProva(self):

        query = self.LocalBaseQuery.delete('prova_config')
        return query
    
    def getToLocal(self): 
        # este método deverá salvar na base de dados local, os dados do equipamento

        # self.LocalBaseQuery.insert('equipamentos', 'equipamento, checkpoint, idprova, hora, identificacao, NomeProva, NomeCheck, NomeEquipamento, atualizacao_hora', self.idEquipamentoLocal, self.idCheckpoint, self.idProva, self., 0, 'TESTE EQUIPAMENTO', 'LARGADA', 'READER 1', '13:52:15 26/06/2023')

        
        pass

    def equipData(self, nome_equipamento):
        try: 

            
            #FAZ UMA CONSULTA EM UMA TABELA RELACIONADA NO BANCO DE DADOS
            query = f"""SELECT eck.*, eq.*, checkpoint.*, provas.tituloprova, provas.hora
                        FROM equipamentos_do_check AS eck
                        INNER JOIN equipamentos AS eq ON eck.equipamento = eq.id
                        JOIN checkpoint ON eck.idcheck = checkpoint.id
                        JOIN provas ON provas.id = eck.idprova
                        WHERE eq.nomeequipamento = "{nome_equipamento}";
            """

            #CRIA CURSOR E EXECUTA O COMANDO
            if not self.conn.is_connected():
                self.cursor = self.conn.cursor()
                self.cursor.execute(query)
                dados = self.cursor.fetchall()

                #PEGA AS PRINCIPAIS COLUNAS DA TABELA
            else:
                self.conn = mysql.connector.connect(host=HOST,
                                                    user=USER,
                                                    password=PASSWORD,
                                                    database=DATABASE)
                self.cursor = self.conn.cursor()    
                self.cursor.execute(query)
                dados = self.cursor.fetchall()
                self.dadosEquip.append(dados)
                print(self.conn)

            for linha in dados:
                

                self.idEquipamento.append(linha[2])
                self.idProva.append(linha[3])
                self.idCheckpoint.append(linha[1])
                self.descricaoCheck.append(linha[10])
                self.identificacao.append(linha[12])
                self.tituloProva.append(linha[13])
                horaProva = format_timedelta(linha[14])
                self.horaDaProva.append(horaProva)
                
            return dados
        except Exception as e:
            print("Error -> ", e)

    def getEspecificEquipData(self, nome_equipamento, idcheck, idprova):
        try: 

            
            #FAZ UMA CONSULTA EM UMA TABELA RELACIONADA NO BANCO DE DADOS
            query = f"""SELECT eck.*, eq.*, checkpoint.*, provas.tituloprova, provas.hora
                        FROM equipamentos_do_check AS eck
                        INNER JOIN equipamentos AS eq ON eck.equipamento = eq.id
                        JOIN checkpoint ON eck.idcheck = checkpoint.id
                        JOIN provas ON provas.id = eck.idprova
                        WHERE eq.nomeequipamento = "{nome_equipamento}" AND eck.idcheck = {idcheck} AND eck.idprova = {idprova};
            """

            #CRIA CURSOR E EXECUTA O COMANDO
            if not self.conn.is_connected():
                self.cursor = self.conn.cursor()
                self.cursor.execute(query)
                dados = self.cursor.fetchall()

                #PEGA AS PRINCIPAIS COLUNAS DA TABELA
            else:
                self.conn = mysql.connector.connect(host=HOST,
                                                    user=USER,
                                                    password=PASSWORD,
                                                    database=DATABASE)
                self.cursor = self.conn.cursor()    
                self.cursor.execute(query)
                dados = self.cursor.fetchall()
                self.dadosEquip.append(dados)
                print(self.conn)
            if dados:
                self.idEquipamento = []
                self.idProva = []
                self.idCheckpoint = []
                self.descricaoCheck = []
                self.identificacao = []
                self.tituloProva = []
                horaProva = []
                self.horaDaProva = []
                for linha in dados:
                    

                    self.idEquipamento.append(linha[2])
                    self.idProva.append(linha[3])
                    self.idCheckpoint.append(linha[1])
                    self.descricaoCheck.append(linha[10])
                    self.identificacao.append(linha[12])
                    self.tituloProva.append(linha[13])
                    horaProva = format_timedelta(linha[14])
                    self.horaDaProva.append(horaProva)
                    
                return dados
        except Exception as e:
            print("Error -> ", e)


    def getOffline(self, nome_equipamento):
        row = LOCAL_QUERY.offSelect('*', 'equipamentos', f'NomeEquipamento = "{nome_equipamento}"')
        if len(row) > 1:
            row = row[-1]
        

        self.dadosEquip = row
        self.idEquipamento  = row[1]
        self.idCheckpoint = row[2]
        self.idProva = row[3]
        self.horaDaProva = row[4]
        self.identificacao = row[5]
        self.nomeProva = row[6]
        self.nomeCheck = row[7]
        self.nomeEquipamento = row[8]
        self.ultimaAtualizacaoOff = row[9]

        return row
                    
    def saveEquipamentos(self, nome_equipamento, id_equipamento, id_checkpoint, hora_prova, nome_prova, local, nome_checkpoint):
        val = nome_equipamento, id_equipamento, id_checkpoint, hora_prova, nome_prova, local, nome_checkpoint
        try:
            self.LocalBaseQuery.offInsert('equipamentoffline','nome_equipamento, id_equipamento, id_checkpoint, hora_prova, nome_prova, local, nome_checkpoint', *val)
        except Exception as e:
            print("Error -> ", e)

            
    def Pega_Dados(self, nomeequipamento):   
        try: 

            
            #FAZ UMA CONSULTA EM UMA TABELA RELACIONADA NO BANCO DE DADOS
            query = f"""SELECT *, eck.id AS ideq_chek FROM equipamentos_do_check AS eck
                    INNER JOIN equipamentos AS eq
                    ON eck.equipamento = eq.id
                    WHERE nomeequipamento = "{nomeequipamento}"
            """

            #CRIA CURSOR E EXECUTA O COMANDO
            if not self.conn.is_connected():
                self.cursor = self.conn.cursor()
                self.cursor.execute(query)
                dados = self.cursor.fetchall()
                print(self.conn)
                #PEGA AS PRINCIPAIS COLUNAS DA TABELA
            else:
                self.conn = mysql.connector.connect(host=HOST,
                                                    user=USER,
                                                    password=PASSWORD,
                                                    database=DATABASE)
                self.cursor = self.conn.cursor()    
                self.cursor.execute(query)
                dados = self.cursor.fetchall()
                print(self.conn)

            for linha in dados:
                
                self.idEquipamento.append(linha[2])
                self.idProva.append(linha[3])
                self.nomeEquipamento.append(linha[5])
                self.idCheckpoint.append(linha[1])

            
            #CONSULTA A HORA DA LARGADA E DEFINE COMO HORA BASE
            # query = f"SELECT horalargada FROM `percurso` WHERE `idprova` = '{self.idProvaOn[0]}'"
            # self.cursor.execute(query)
            # linhas_hora_base = self.cursor.fetchall()

            linhas_hora_base = self.MySQLQueries.select('horalargada', 'percurso', f'idprova = "{self.idProva[0]}" ')
            for linha in linhas_hora_base:

                
                self.horaDaProva.append(linha[0])
                  
                self.horaDaProva = self.horaDaProva[0]
                print(self.horaDaProva) 

            #CONSULTA O CHECKPOINT (CHEGADA OU LARGADA) 
            # query = f"SELECT identificacao FROM `checkpoint` WHERE `id` = '{self.idCheckpointOn[0]}'"
            # self.cursor.execute(query)
            # linhas_identificacao = self.cursor.fetchall()
            linhas_identificacao = self.MySQLQueries.select('identificacao', 'checkpoint', f'id = "{self.idCheckpoint[0]}"')
            for linha in linhas_identificacao:
            
                self.identificacao.append(linha[0])  
                print(self.identificacao)     
                self.status = 'ONLINE'
                
        except Exception as e:
        
            # self.dadosEquip = self.getOffline(nomeequipamento)
            # print(self.dadosEquip)
            self.status = 'OFFLINE'
            print(f'Ocorreu um erro! : -> {e}; STATUS = {self.status}')

        #RETORNA OS DADOS 
        print(self.horaDaProva)
        try:
            self.horaDaProva = format_timedelta(self.horaDaProva)
        except:
            self.horaDaProva = self.horaDaProva

        return self.idEquipamento, self.idCheckpoint, self.idProva, self.horaDaProva, self.identificacao

                
app  = MyTempoQuerys(HOST, USER, PASSWORD, DATABASE, localDatabaseDir)


