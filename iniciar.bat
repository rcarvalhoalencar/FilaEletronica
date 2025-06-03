@echo off
REM Vai para o diretório do projeto (ajuste se necessário)
cd /d "%~dp0"

REM Ativa o ambiente virtual
call venv\Scripts\activate.bat

color F2
echo ************************************************************************************************************
echo ****   SETOR DE TECNOLOGIA DA INFORMACAO - STI / PREFEITURA MUNICIPAL DE LAGOA DO BARRO DO PIAUI - PI
echo ************************************************************************************************************
echo ****   ATENCAO: NAO FECHA ESTA JANELA. SOMENTE QUANDO FOR DESLIGAR O COMPUTADOR.
echo ************************************************************************************************************

REM Inicia o servidor Django (HTTP + Channels)
python manage.py runserver

REM Pausa para manter a janela aberta, caso o servidor seja interrompido

pause
