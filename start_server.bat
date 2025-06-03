@echo off
REM ==============================================
REM 1) Vai para a pasta onde está este .bat
cd /d "%~dp0"

REM ==============================================
REM 2) Verifica se existe a pasta venv; se não, cria
if not exist "venv\Scripts\activate.bat" (
    echo Criando ambiente virtual (venv)...
    py -3 -m venv venv
    if errorlevel 1 (
        echo ERRO: falha ao criar o ambiente virtual. Verifique se o Python 3 esta instalado e no PATH.
        pause
        exit /b 1
    )
)

REM ==============================================
REM 3) Ativa o ambiente virtual recém-criado (ou existente)
echo Ativando o ambiente virtual...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERRO: nao foi possivel ativar o ambiente virtual.
    pause
    exit /b 1
)

REM ==============================================
REM 4) Atualiza pip e instala dependencias
if exist requirements.txt (
    echo Instalando/atualizando dependencias (requirements.txt)...
    pip install --upgrade pip
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERRO: falha ao instalar dependencias. Verifique o requirements.txt.
        pause
        exit /b 1
    )
) else (
    echo AVISO: requirements.txt nao encontrado. Eh necessario instalar Django e Channels manualmente:
    echo        pip install Django channels asgiref
)

REM ==============================================
REM 5) Mensagem de cabecalho (opcional)
color F2
echo ************************************************************************************************************
echo ****   SETOR DE TECNOLOGIA DA INFORMACAO - STI / PREFEITURA MUNICIPAL DE LAGOA DO BARRO DO PIAUI - PI
echo ************************************************************************************************************
echo ****   ATENCAO: NAO FECHA ESTA JANELA. SOMENTE QUANDO FOR DESLIGAR O COMPUTADOR.
echo ************************************************************************************************************

REM ==============================================
REM 6) Inicia o servidor Django (HTTP + Channels)
echo Iniciando o servidor Django (runserver)...
python manage.py runserver

REM ==============================================
REM 7) Mantem a janela aberta apos qualquer er
