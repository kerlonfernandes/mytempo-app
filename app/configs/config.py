import sqlite3
import re
import mysql.connector
from datetime import date, datetime
import glob
import os
from pathlib import Path
import datetime

HOST =  "162.240.222.71" 
USER = "mytempoesp_base"
PASSWORD = "6*JqY8Xfa}Hf"
DATABASE = "mytempoesp_base"

_APLICATION_NAME = "MyTempo - Arquivo" 

__DIR__ = os.path.abspath(os.path.join(os.path.dirname(__file__)))

#CONFIGURAÇÃO DO LOCALDATABASE
localDatabaseDir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../database/equipamentos.db'))


desktop_path = str(Path.home() / 'Desktop')
leitura_path = os.path.join(desktop_path, 'Leitura')


def FormatarHora(hora):
    dt = datetime.datetime.strptime(hora, "%H:%M:%S")
    return dt.strftime("%H:%M:%S")


# Obter a data e hora atual
agora = datetime.datetime.now()

# Formatar a data e hora
data_formatada = agora.strftime("%d/%m/%Y")
hora_formatada = agora.strftime("%H:%M:%S")

today = str(date.today()) 

def format_timedelta(delta):
    horas = delta.seconds // 3600
    minutos = (delta.seconds // 60) % 60
    segundos = delta.seconds % 60

    formato_tempo = "{:02d}:{:02d}:{:02d}".format(horas, minutos, segundos)
    return formato_tempo

# Exemplo de uso
# delta = datetime.timedelta(seconds=28800)
# tempo_formatado = format_timedelta(delta)

