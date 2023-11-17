from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.filechooser import FileChooserListView
import os

class FileChooserApp(App):
    def build(self):
        layout = BoxLayout(orientation='vertical')

        # Crie uma instância do FileChooserListView
        file_chooser = FileChooserListView()

        # Defina o diretório inicial com base no sistema operacional
        initial_directory = self.get_default_directory()
        file_chooser.path = initial_directory

        # Função chamada quando um arquivo ou diretório é selecionado
        def on_selection(instance, selection, touch):
            print("Seleção:", selection)

        # Adicione a função de seleção ao evento 'on_selection'
        file_chooser.bind(on_selection=on_selection)

        # Adicione o FileChooser ao layout
        layout.add_widget(file_chooser)

        return layout

    def get_default_directory(self):
        # Obtenha o diretório inicial com base no sistema operacional
        if os.name == 'posix':  # Linux
            return os.path.expanduser('~/Desktop')
        elif os.name == 'nt':  # Windows
            return os.path.join(os.path.expanduser('~'), 'Desktop')
        else:
            return os.getcwd()  # Retorna o diretório atual como padrão para outros sistemas

if __name__ == '__main__':
    FileChooserApp().run()
