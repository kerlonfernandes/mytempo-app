import os

# Diretório que você deseja listar
diretorio = 'C:/Users/kerlo/Desktop/MyTempoInterface-Kivy/env/Lib/site-packages'

# Use a função listdir para obter uma lista de todos os arquivos e pastas no diretório
conteudo = os.listdir(diretorio)

# Use uma list comprehension para filtrar apenas os diretórios (pastas)
pastas = [item for item in conteudo if os.path.isdir(os.path.join(diretorio, item))]

# Agora você tem uma lista de nomes de pastas em 'pastas'
print(pastas)
