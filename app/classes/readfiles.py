from app.configs.config import *
from app.classes.myTempoQuerys import MyTempoQuerys
import time
import threading
import socket



class MyTempoApp(MyTempoQuerys):
    def __init__(self, desktop_path, leitura_path):
        super().__init__(HOST, USER, PASSWORD, DATABASE, localDatabaseDir)
        
        self.desktop_path = desktop_path
        self.leitura_path = leitura_path
        self.tempos = {}
        self.primeiros_tempos_minerados = []
        self.ultimos_tempos_minerados = []
        self.tamanho_atual = None
        self.tentativas_sem_alteracao = 0
        self.thread = None
        self.thread_ativa = False
        self.internet_status = ''
        self.aplicacao = False
        self.tempos = {}
        self.qtd_total = []
        self.qtd_atletas = []
        self.tempos_apurados = []

        # self.monitor_thread = threading.Thread(target=self.processaArquivo, args=(self.arquivo,))


    def getFile(self):
        try:

            if not os.path.exists(self.leitura_path):
                os.mkdir(self.leitura_path)

            folder_path = self.leitura_path

            files = glob.glob(folder_path + '/*.txt')

            if not files:
                print('Nenhum arquivo encontrado!')
            else:
                try:
                    most_recent_file = files[-1]

                    tag = os.path.basename(most_recent_file)

                    file_path = f'{self.leitura_path}/{tag}'

                    file_title = os.path.basename(file_path)

                    # idprova = int(file_title[0:5])
                    # idcheck = int(file_title[6:10])
                    # idequip = int(file_title[11:15])

                    # idprovastr = str(idprova)
                    # idcheckstr = str(idcheck)
                    # idequipstr = str(idequip)

                    # ids = idprovastr + idcheckstr + idequipstr
                    return most_recent_file
                    

                except IndexError:
                    print('Erro ao processar o título do arquivo.')
        except OSError as e:
            print(f'Erro ao criar diretório: {e}')
        except Exception as e:
            print(f'Erro desconhecido: {e}')
                        

    def readFiles(self):
        try:
            file = self.getFile()
            with open(file) as arq:
                # Lê o conteúdo do arquivo como uma string e divide em linhas
                rows = arq.read().splitlines()

                # Percorre as linhas do arquivo
                for row in rows:
                    # Extrai o número do atleta e o tempo da linha
                    numero_atleta = int(row[8:19])
                    tempo_atleta = str(row[19:31])

                    # Adiciona o tempo do atleta ao dicionário
                    self.tempos.setdefault(numero_atleta, []).append(tempo_atleta)
        except FileNotFoundError:
            print("Arquivo não encontrado")
        except ValueError:
                print("Erro ao ler o arquivo: valor inválido encontrado")
        
        self.tempos = self.tempos
        return self.tempos
    
    def calculoFormat(self, calculo):
        try:
            #tira as pontuações
            calculo = calculo.replace('-','')
            calculo = calculo.replace(' ','')
            calculo = calculo.replace(':','')
            calculo = calculo.replace('.','')
            return calculo
        except Exception as e:
            print(f"Erro ao formatar tempo: err -> {e}")
    def searchTimestamps(self, search_string, lista):
        return [val for val in lista if val.startswith(search_string)]
    

    def getLastTime(self):
        try:
            conn = sqlite3.connect('equipamentos.db')
            cursor = conn.cursor()
            query = """ CREATE TABLE IF NOT EXISTS tempos_first (
                        id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                        atleta TEXT,
                        tempo TEXT
                    );"""
            cursor.execute(query)
            print('Tabela criada com sucesso!')

            lista = []
            tempos = self.readFiles()
            print(tempos)
            for numero_atleta, lista_tempos in tempos.items():
                for tempo in lista_tempos:
                    cursor.execute("INSERT INTO tempos_first (atleta, tempo) VALUES (?, ?)",
                                    (numero_atleta, tempo))

            query = cursor.execute(f"""
                                SELECT atleta, tempo
                                FROM (
                                        SELECT atleta, tempo,
                                            ROW_NUMBER() OVER (PARTITION BY atleta ORDER BY tempo DESC) AS row_num
                                        FROM tempos_first
                                    ) ranked
                                    WHERE row_num = 1;

                                """)
            rows = cursor.fetchall()
            cursor.execute('DROP TABLE tempos_first')
            print("Tabela apagada com sucesso!")
            conn.close()
            for temps in rows:
                self.ultimos_tempos_minerados.append(temps)

            return self.ultimos_tempos_minerados
        except conn as e:
            print("Erro ")
    def getFirstTime(self, tempo_prova):
        conn = sqlite3.connect('equipamentos.db')
        cursor = conn.cursor()
        query = """ CREATE TABLE IF NOT EXISTS tempos_first (
                    id INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
                    atleta TEXT,
                    tempo TEXT
                );"""
        cursor.execute(query)
        print('Tabela criada com sucesso!')

        lista = []
        tempos = self.readFiles()
        print(tempos)
        for numero_atleta, lista_tempos in tempos.items():
            for tempo in lista_tempos:
                cursor.execute("INSERT INTO tempos_first (atleta, tempo) VALUES (?, ?)",
                                (numero_atleta, tempo))

        query = cursor.execute(f"""
                                SELECT atleta, MIN(tempo) AS menor_tempo
                                FROM tempos_first
                                WHERE TIME(tempo) >= TIME('{tempo_prova}')
                                GROUP BY atleta;
                               """)
        rows = cursor.fetchall()
        cursor.execute('DROP TABLE tempos_first')
        print("Tabela apagada com sucesso!")
        conn.close()
        for temps in rows:
            self.primeiros_tempos_minerados.append(temps)
        return self.primeiros_tempos_minerados
    
    def parar_monitoramento(self):
        self.thread_ativa = False
        if self.thread is not None:
            self.thread.join()

    def monitorar_arquivo(self, arq_dir, tempo_espera=1):
        while self.thread_ativa:
            time.sleep(tempo_espera)
            novo_tamanho = os.path.getsize(self.arquivo)
            
            
            
            if novo_tamanho != self.tamanho_atual:
                print("Arquivo foi modificado! Executando ação...")
                self.tamanho_atual = novo_tamanho
                print(self.tamanho_atual)
                self.tentativas_sem_alteracao = 0
                self.processaArquivo()
                self.monitorar_arquivo(1)
            else:
                pass

    def Tempos(self, local, hora_da_prova):

        lista = []
        tempos = self.readFiles()
        if local == '0':
            tempo = self.getFirstTime(hora_da_prova)
            return tempo

        elif local == '1':
            tempo = self.getLastTime()
            return tempo

        
    
    def enviaTempos(self, *val):
        if len(val) > 10:
            print('valor grande demais')
            return
        else:         
            self.querysMyTempo.insert('tempos', 'idprova, idcheck, idequipamento, numero, tempo, calculo, antena, local, entrada, idstaff',*val)
            

    def startApplication(self, arquivo, nome_equipamento, idcheck, idprova, tempo_espera=1):
  
        self.aplicacao = True
        self.internet_thread = threading.Thread(target=self.check_internet_connection)
        self.internet_thread.start()

        if self.internet_status == "OFFLINE":
            data = self.getOffline(nome_equipamento)
    
        else:
            
            equipamento = self.LocalBaseQuery.offSelect("nome_equipamento, id_equipamento, nome_checkpoint, local, id_checkpoint, nome_prova", "equipamentoffline", f"nome_equipamento = '{nome_equipamento}'")
            print(equipamento)

            if equipamento == []:
                data = self.getEspecificEquipData(nome_equipamento, idcheck, idprova)
                for dado in data:
                    self.saveEquipamentos(nome_equipamento, dado[2], dado[1], dado[14], dado[13], dado[12], dado[10])
            else:
                data = self.especificEquipData(nome_equipamento, idcheck, idprova)
                print(data)


        self.arquivo = arquivo
        self.tamanho_atual = os.path.getsize(arquivo)
        self.thread = threading.Thread(target=self.monitorar_arquivo, args=(tempo_espera,))
        self.thread_ativa = True
        self.thread.start()
        
            # except Exception as e:
            #     print(f"Ocorreu um erro: err -> {e} ")
                


            




    def parar_monitoramento(self):
        self.thread_ativa = False
        if self.thread is not None:
            self.thread.join()

    def monitorar_arquivo(self, tempo_espera):
        while self.thread_ativa:
            time.sleep(tempo_espera)
            novo_tamanho = os.path.getsize(self.arquivo)
            
            if novo_tamanho != self.tamanho_atual:
                print("Arquivo foi modificado! Executando ação...")
                self.tamanho_atual = novo_tamanho
                print(self.tamanho_atual)
                self.tentativas_sem_alteracao = 0
                self.process()
                self.monitorar_arquivo(1)
            else:
                print("Nenhum arquivo modificado.")

    

    def check_internet_connection(self):
                while True:
                    
                    try:
                        # Tenta conectar-se a um servidor de domínio conhecido
                        socket.create_connection(("www.google.com", 80))
                        self.internet_status = 'ONLINE'
                        # return True
                    except OSError:
                        self.internet_status = "OFFLINE"
                    print(f"Internet status: {self.internet_status}")
                    time.sleep(2) 
                        # return False    
    

    def check_internet(self):
                    try:
                        # Tenta conectar-se a um servidor de domínio conhecido
                        socket.create_connection(("www.google.com", 80))
                        self.internet_status = 'ONLINE'
                        # return True
                    except OSError:
                        self.internet_status = "OFFLINE"
                    print(f"Internet status: {self.internet_status}")
                    time.sleep(2) 
                        # return False    
                    

    def process(self):
    
        
        
        if self.internet_status == "OFFLINE":

            try:
                self.getOffline()
            except:
                pass

        id_prova = self.idProva
        id_checkpoint = self.idCheckpoint
        id_equipamento = self.idEquipamento
        hora_prova = self.horaDaProva
        print(hora_prova)
        print(self.identificacao)
        local = str(self.identificacao[0])
        # else:
        #     try:
                
        #         self.idProva = []
        #         self.idEquipamento = []
        #         self.idCheckpoint = []
        #         self.horaDaProva = []

                
        #         self.Pega_Dados(nome_equipamento)


        #         id_prova = self.idProva
        #         id_checkpoint = self.idCheckpoint
        #         id_equipamento = self.idEquipamento
        #         hora_prova = self.horaDaProva
        #         local = str(self.identificacao)

            # except Exception as e:
            #     print("erro: -> ", e)


        print(id_prova, id_checkpoint, id_equipamento, hora_prova, local)
        tempos = None
        numero_atleta = []
        tempo_atleta = []

        if local == '0':
            self.getFirstTime(hora_prova)
            tempos = self.primeiros_tempos_minerados

        elif local == '1':
            self.getLastTime()
            tempos = self.ultimos_tempos_minerados

        
        for elemento in tempos:
            numero_atleta = elemento[0]
            tempo_atleta = elemento[1]
            tempo_formatado_envio = f"{today} {tempo_atleta}"
            calculo = self.calculoFormat(tempo_formatado_envio)


