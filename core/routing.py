# core/routing.py

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    # Já existia para o Painel: ws/painel/
    re_path(r'ws/painel/$', consumers.PainelConsumer.as_asgi()),

    # Novo: Rota para médico por sala
    # Ex.: ws/medico/sala/5/ → MedicoConsumer(room_id=5)
    re_path(r'ws/medico/sala/(?P<room_id>\d+)/$', consumers.MedicoConsumer.as_asgi()),
]
