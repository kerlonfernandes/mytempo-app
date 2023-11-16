from cx_Freeze import setup, Executable

# Defina o executável
exe = Executable(
    script="main.py",
    base=None,
)

# Caminhos para incluir no executável
include_files = [
    (r"C:\Users\kerlo\Desktop\MyTempoInterface-Kivy\env\Lib\site-packages\kivy", "kivy"),
    # Adicione outros caminhos conforme necessário
]

# Configuração do executável
setup(
    name="MyTempo",
    version="1.0",
    description="Projeto MyTempo - Coletor",
    options={
        "build_exe": {
            "include_files": include_files,
            "packages": [
                "asyncio",
                "trio",
                "charset_normalizer",
                "cx_Freeze",
                "cx_Logging",
                "lief",
                "mysql.connector",
                "pygments",
            ],
        },
    },
    executables=[exe]
)
