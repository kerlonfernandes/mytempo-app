from datetime import datetime

class Helpers:

    def __init__(self) -> None:
        self.calculoFormato = ''


    def sanitizeTimeInput(self, calculo):
        try:
            #tira as pontuações
            calculo = calculo.replace('-','')
            calculo = calculo.replace(' ','')
            calculo = calculo.replace(':','')
            calculo = calculo.replace('.','')
            return calculo
        except Exception as e:
            print(f"Erro ao formatar tempo: err -> {e}")
    
    def calculo(self, tempo):
        print(datetime.year)
        # 20220814082915026

    def searchTimestamps(self, search_string, lista):
        return [val for val in lista if val.startswith(search_string)]

helper = Helpers()