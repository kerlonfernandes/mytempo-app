
#kivy libs
from kivy.app import App
from kivy.uix.gridlayout import GridLayout
from kivy.properties import ObjectProperty
from kivy.clock import Clock
from kivy.lang import Builder
from kivy.uix.spinner import Spinner
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.button import Button
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout  # Importe a classe BoxLayout
from kivy.config import Config


#other libs
import socket
import time
import sqlite3

#Classes
from app.classes.queryConstructorClass import Database
from app.classes.queryConstructorSqlite import Local_Database
from app.classes.helpersClass import *
from app.classes.readfiles import *

#configurações
from app.configs.config import __DIR__
from app.configs.config import _APLICATION_NAME

#config App interface
Config.set('graphics', 'width', '800')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'backend', 'sdl2')

class MyGridLayout(GridLayout):
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.conn = mysql.connector.connect(host=HOST,
                                            user=USER,
                                            password=PASSWORD,
                                            database=DATABASE)
        self.cursor = self.conn.cursor()


        self.offDatabase = sqlite3.connect(localDatabaseDir)
        self.offCursor = self.offDatabase.cursor()
        self.nomeEquipamento = ''
        self.idEquipamento = []
        self.idCheckpoint = []
        self.idProva  = []
        self.horaDaProva = []
        self.identificacao = []
        self.nomeProva = []
        self.nomeCheck = []
        self.ultimaAtualizacao = []
        self.descricaoCheck = []
        self.tituloProva = []
        self.status = ''
        self.dadosEquip = []
        self.dadosCheckpoint = []
        self.timeNow = datetime.datetime.now()
        self.dateToday = str(date.today()) 
        self.arquivo = ''
        self.nome_arquivo = ''
        self.primeiros_tempos_minerados = []
        self.ultimos_tempos_minerados = []
        self.thread_processamento_ativo = False
        self.thread = None
        self.thread_ativa = False
        self.internet_status = ''
        self.antena = 0
        self.entrada = 0
        self.idstaff = 9
        self.aplicacao = False
        self.tempos = {}
        self.qtd_total = []
        self.qtd_atletas = []
        self.tempos_apurados = []
        self.helper = Helpers()
        self.SQL_exec = Database(HOST, USER, PASSWORD, DATABASE, True)
        self.SQLITE_exec = Local_Database(localDatabaseDir)
        self.temposDados = []
        self.tamanho_atual = 0
        self.row_qtd = 0
        self.thread_envio = False
        self.thread_if_exists = True        
        self.trasmissao_btn_state = False
        
        #outros processos

        self.thread_internet = threading.Thread(target=self.checkInternetStatus)
        self.thread_internet.start()
        self.create_dir(_APLICATION_NAME)
        self.getStartEquip()

    def createNewDir(self):
        import os
        
        
        diretorio = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))

        # Verifica se o diretório não existe antes de criar
        if not os.path.exists(__DIR__):
            os.makedirs(diretorio)

    def getStartEquip(self):

        res = self.SQLITE_exec.executeQuery("SELECT nome_equipamento FROM equipamentoffline ORDER BY id DESC")
        if(self.SQLITE_exec.info['affected_rows'] != ''):
            label = self.ids.nome_equipamento
            label.text = str(res[0][0])
        else:
            label = self.ids.nome_equipamento
            label.text = ""
    
    
    def mostrar_popup(self, instance=None):
        self.popup = Popup(title="Selecione um arquivo", size=(400, 400), auto_dismiss=False)

        file_chooser = FileChooserListView()
        initial_directory = self.get_default_directory()
        file_chooser.path = initial_directory
        file_chooser.size_hint_y = 1 # Ajuste a altura conforme necessário

        file_chooser.bind(on_submit=self.abrir_arquivo_selecionado)

        self.popup.content = file_chooser

        self.popup.open()

    
    def uploadTempos(self):
        
        temposLidos = self.SQLITE_exec.executeQuery(f"SELECT DISTINCT idprova, idcheck, idequipamento, numero, tempo, calculo, antena, local, entrada, idstaff FROM tempos WHERE idprova = {self.idProva} AND idcheck = '{self.idCheckpoint}' AND idequipamento = {self.idEquipamento} AND local = '{self.identificacao}'")
        if self.idProva and self.idCheckpoint and self.idEquipamento and self.identificacao:
            try:
                for tempo in temposLidos:
                    self.SQL_exec.executeNonQuery(f"INSERT INTO tempos (idprova, idcheck, idequipamento, numero, tempo, calculo, antena, local, entrada, idstaff) VALUES {tempo}")
            except:
                self.show_error(message="Você precisa selecionar um checkpoint.")
                self.trasmissao_btn_state = False
        valores = ()
    

   
    def abrir_arquivo_selecionado(self, instance, selection, touch=None):
        
        arquivo_selecionado = selection[0]
        self.arquivo = arquivo_selecionado
        label = self.ids.selected_file_label 
        label.text = str(self.arquivo)
        self.thread_ativa = True
        self.tamanho_atual = os.path.getsize(self.arquivo)
        self.thread = threading.Thread(target=self.monitorar_arquivo)
        
        try:
            self.readFiles(self.arquivo)
            self.thread.start()
            self.popup.dismiss()
        except FileNotFoundError:
            print("Arquivo não encontrado.")

    def readFiles(self, file):
        try:
            file = file
            with open(file) as arq:
                # Lê o conteúdo do arquivo como uma string e divide em linhas
                rows = arq.read().splitlines()
                self.row_qtd = len(rows)

                # Percorre as linhas do arquivo
                for row in rows:
                    # Extrai o número do atleta e o tempo da linha
                    numero_atleta = int(row[8:19])
                    tempo_atleta = str(row[19:31])

                    # Adiciona o tempo do atleta ao dicionário
                    self.tempos.setdefault(numero_atleta, []).append(tempo_atleta)
                    label = self.ids.arquivo_de_leitura
                    label.text = str(self.row_qtd)
        except FileNotFoundError:
            print("Arquivo não encontrado")
        except ValueError:
                print("Erro ao ler o arquivo: valor inválido encontrado", ValueError)
        
        self.tempos = self.tempos
        return self.tempos


    def create_dir(self, app_name):
        sistema_operacional = os.name

        # Diretório padrão no Windows (C:\)
        if sistema_operacional == 'nt':
            diretorio_raiz = 'C:\\'
        # Diretório padrão no Linux (/)
        elif sistema_operacional == 'posix':
            diretorio_raiz = '/'
        else:
            print("Sistema operacional não suportado.")
            return

        app_name = _APLICATION_NAME

        caminho_completo = os.path.join(diretorio_raiz, app_name)

        if not os.path.exists(caminho_completo):
            try:
                # Cria o diretório
                os.makedirs(caminho_completo)
                print(f"Diretório '{caminho_completo}' criado com sucesso.")
            except Exception as e:
                print(f"Erro ao criar o diretório: {e}")
        else:
            print(f"Diretório '{caminho_completo}' já existe.")



    def get_default_directory(self):
        if os.name == 'posix':  # Linux
            return os.path.expanduser('~/Desktop')
        elif os.name == 'nt':  # Windows
            return "C:\\MyTempo - Arquivo"
        else:
            return os.getcwd()

    
    def show_error(self, instance=None, message=""):
        error_message = message
        Clock.schedule_once(lambda dt: self.show_error_popup(error_message))

    def show_error_popup(self, error_message):
        content = BoxLayout(orientation='vertical', padding=50, spacing=20)
        self.error_label = Label(text=error_message)
        close_button = Button(text="Fechar",size=(100, 50))
        content.add_widget(self.error_label)
        content.add_widget(close_button)

        popup = Popup(title="Ocorreu um erro!", content=content, size_hint=(None, None), size=(450, 250))
        close_button.bind(on_release=popup.dismiss)

        popup.open()


    def atualizarEquipamento(self):
        checkpoint_values = []
        if(self.internet_status == True):
            self.nomeEquipamento = self.ids.nome_equipamento.text
            dados_equipamento = self.equipData(self.nomeEquipamento)
            for dado in dados_equipamento:
                print(dado)
                time = format_timedelta(dado[14])
                
                equip_check = f"{str(dado[5])} | {str(dado[10])} | {str(dado[13]) } | {str(dado[1])} | {str(dado[3])} | {str(dado[12])} | {str(time)} | {str(dado[4])}"
                checkpoint_values.append(equip_check)
            print(checkpoint_values)

            checkpoint_spinner = self.ids.checkpoint_spinner
            checkpoint_spinner.values = checkpoint_values
        else: 
            self.show_error(message="Você precisa ter conexão com a internet \npara executar esta ação.")

    def checkpoint_selecionado(self):
        spinner = self.ids.checkpoint_spinner 
        valor_selecionado = spinner.text
        if valor_selecionado:
            try:
                self.dadosCheckpoint = valor_selecionado.split(" | ")
                self.dadosCheckpoint = eval(str(self.dadosCheckpoint))
                print(self.row_qtd)
                self.dadosEquip = self.getEspecificEquipData(self.nomeEquipamento, self.dadosCheckpoint[3], self.dadosCheckpoint[4])
                if (self.dadosCheckpoint[3]):
                    label = self.ids.checkpoint_ativo
                    label.text = f"CHECKPOINT ATIVO: {str(self.dadosCheckpoint[3])}"
                if(self.dadosCheckpoint[2]):
                    label = self.ids.nome_prova
                    label.text = f"NOME PROVA: {str(self.dadosCheckpoint[2])}"
                if(self.dadosCheckpoint[1]):
                    label = self.ids.nome_checkpoint
                    label.text = f"NOME DO CHECKPOINT: {str(self.dadosCheckpoint[1])}"
                if(self.dadosCheckpoint[4]):
                    label = self.ids.id_prova
                    label.text = f"ID DA PROVA: {str(self.dadosCheckpoint[4])}"

                self.idProva = self.dadosCheckpoint[4]
                self.idCheckpoint = self.dadosCheckpoint[3]
                self.idEquipamento = self.dadosCheckpoint[7]
                self.identificacao = self.dadosCheckpoint[5]

                self.saveEquipamentos(self.nomeEquipamento, self.idEquipamento[0], self.dadosCheckpoint[3], self.dadosCheckpoint[6], self.dadosCheckpoint[2], self.dadosCheckpoint[5], self.dadosCheckpoint[1], self.dadosCheckpoint[4])

            except:
                self.show_error(message="Você precisa Buscar um equipamento.")

     
        #atualiza labels 

    def checkInternetStatus(self):
      
            while True:
                try:
                    # Tenta conectar-se ao servidor do Google (8.8.8.8) na porta 53 (DNS)
                    socket.create_connection(("8.8.8.8", 53), timeout=5)
                    self.internet_status = True

                    label = self.ids.internet_status 
                    label.text = "Status: Conectado à internet"
                except OSError:
                    label = self.ids.internet_status
                    label.text = "Status: Sem conexão com a internet"
                    self.internet_status = False

                time.sleep(5)



    def equipData(self, nome_equipamento):
        # self.nomeEquipamento = ''
        self.idEquipamento = []
        self.idCheckpoint = []
        self.idProva  = []
        self.horaDaProva = []
        self.identificacao = []
        self.nomeProva = []
        self.nomeCheck = []
        self.ultimaAtualizacao = []
        self.descricaoCheck = []
        self.tituloProva = []
        self.status = ''
        self.dadosEquip = []
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
   
    def saveEquipamentos(self, nome_equipamento, id_equipamento, id_checkpoint, hora_prova, nome_prova, local, nome_checkpoint, idprova):
        try:
            self.offCursor.execute(f"INSERT INTO equipamentoffline (nome_equipamento, id_equipamento, id_checkpoint, hora_prova, nome_prova, local, nome_checkpoint, idprova) VALUES ('{nome_equipamento}', {id_equipamento}, {id_checkpoint}, '{hora_prova}', '{nome_prova}', '{local}', '{nome_checkpoint}', {idprova})")
            print("inserido com sucesso!")
            self.offDatabase.commit()
            print(self.tempos)
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
    def parar_monitoramento(self):
        self.thread_ativa = False
        if self.thread is not None:
            self.thread.join()

    def monitorar_arquivo(self):
        self.SQLITE_exec.executeNonQuery("DELETE FROM tempos")
        while self.thread_ativa:
            time.sleep(1)
            novo_tamanho = os.path.getsize(self.arquivo)
            
            if novo_tamanho != self.tamanho_atual:
                print("Arquivo foi modificado! Executando ação...")
                self.tamanho_atual = novo_tamanho

                print(self.tamanho_atual)
                self.tentativas_sem_alteracao = 0
                 
                self.processaDados()
                self.monitorar_arquivo()
                
            else:
                pass
    
    def Tempos(self, local, hora_da_prova):

        lista = []
        tempos = self.readFiles(self.arquivo)
        if local == '0':
            tempo = self.getFirstTime(hora_da_prova)
            return tempo

        elif local == '1':
            tempo = self.getLastTime()
            return tempo
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
            tempos = self.readFiles(self.arquivo)
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
        tempos = self.readFiles(self.arquivo)
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

    def ativarTransmissão(self):
        self.SQL_exec.createConn()
        self.trasmissao_btn_state = True
        self.thread_processamento_ativo = True
        self.thread_processamento = threading.Thread(target=self.processaDados)
        self.thread_processamento.start()
    
    def enviaTempos(self):

        if (self.dadosCheckpoint):
            self.processaDados()
        else:
            self.show_error(message="Você precisa selecionar um Equipamento")
            self.trasmissao_btn_state = False
                
        self.verifyIfExistsAthlete()
        self.uploadTempos()

    def prepareIfExists(self):
        self.thread_if_exists = True
        self.thread_if_exists = threading.Thread(target=self.verifyIfExistsAthlete)
        self.thread_if_exists.start()

    def verifyIfExistsAthlete(self):
        try:
            results = self.SQL_exec.executeQuery(f"SELECT numero FROM tempos WHERE idprova = {self.idProva} AND idcheck = {self.idCheckpoint} AND idequipamento = {self.idEquipamento} AND local = {self.identificacao};")
            label = self.ids.transmitido
            label.text = str(self.SQL_exec.info['affected_rows'])
            print(self.SQL_exec.info['affected_rows'])
        
            self.atletas_base = []
            for numero in results:
                self.atletas_base.append(numero[0])
                
            self.atletas_base = tuple(self.atletas_base)
            if(results):
                self.offDatabase = sqlite3.connect(localDatabaseDir)
                self.offCursor = self.offDatabase.cursor()
                self.offCursor.execute(f"SELECT numero FROM tempos WHERE idprova = {self.idProva} AND idcheck = {self.idCheckpoint} AND idequipamento = {self.idEquipamento} AND local = {self.identificacao} AND numero NOT IN {self.atletas_base}")
                res_off = self.offCursor.fetchall()
                
                            

        except Exception as e: 
            print(e)


        # SELECT * FROM `tempos` WHERE idprova = 99 AND idcheck = 186 AND idequipamento = 96 AND local = 1;
 
    def prepareToSend(self):
        if (self.trasmissao_btn_state == False):
            if(self.dadosCheckpoint):
                self.trasmissao_btn_state = True
                if (self.trasmissao_btn_state == True):
                    self.thread_envio = True 
                    self.SQL_exec.createConn()
                    self.thread_envio = threading.Thread(target=self.enviaTempos)
                    self.thread_envio.start()
                    label = self.ids.inicia_transmissao
                    label.text = "TRANSMITINDO"
            else:
                self.show_error(message="Você precisa selecionar um Checkpoint!")   

        elif (self.trasmissao_btn_state == True):
            self.trasmissao_btn_state = False
            self.thread_envio.join()
            self.thread_envio = None
            self.SQL_exec.killConnection()
            label = self.ids.inicia_transmissao
            label.text = "ATIVAR TRANSMISSÃO"
    
    def processaDados(self):
        self.temposDados = []
        label = label = self.ids.atletas_mineirados
        if (self.dadosCheckpoint):
            try:
                if(self.dadosCheckpoint[5] and self.dadosCheckpoint[6]):

                    tempos = self.Tempos(self.dadosCheckpoint[5], self.dadosCheckpoint[6])
                    for tempo in tempos:
                        tempo_formatado = f"{today} {tempo[1]}"
                        calculo = self.helper.sanitizeTimeInput(tempo_formatado)
                        
                        self.temposDados.append((self.idProva, self.idCheckpoint, self.idEquipamento, tempo[0], tempo_formatado, calculo, self.antena, self.identificacao, self.entrada, self.idstaff))
                    
                    label.text = str(len(set(self.temposDados)))

                    self.salvaTemposApurados()
                    print(self.temposDados)
                    self.verifyIfExistsAthlete()
                    return self.temposDados
            except: 
                print('hf')
    def salvaTemposApurados(self):
        self.offDatabase = sqlite3.connect(localDatabaseDir)
        self.offCursor = self.offDatabase.cursor()
        for valores in self.temposDados:
            self.offCursor.execute("INSERT INTO tempos (idprova, idcheck, idequipamento, numero, tempo, calculo, antena, local, entrada, idstaff) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    valores)
        self.offDatabase.commit()


class MyTempoApp(App):
    def build(self):
        return MyGridLayout()

if __name__ == "__main__":
    MyTempoApp().run()

