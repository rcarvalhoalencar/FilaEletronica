# core/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ticket
from django.utils import timezone
from asgiref.sync import sync_to_async

class PainelConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Cada consumidor entra no “grupo” chamado 'painel_tickets'
        await self.channel_layer.group_add('painel_tickets', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove do grupo ao desconectar
        await self.channel_layer.group_discard('painel_tickets', self.channel_name)

    # Este método será chamado por outra parte do código quando um ticket for chamado
    async def ticket_chamado(self, event):
        """
        Event structure:
        {
            'type': 'ticket_chamado',
            'last_three': [ {…}, {…}, {…} ]
        }
        """
        # Envia pelo WebSocket o JSON já preparado
        await self.send(text_data=json.dumps({
            'last_three': event['last_three']
        }))

    @sync_to_async
    def get_last_three(self):
        """
        Pega as últimas 3 senhas chamadas no banco, formata como lista de dicts.
        """
        queryset = Ticket.objects.filter(is_called=True).order_by('-called_at')[:3]
        data = []
        for t in queryset:
            data.append({
                'code': t.code,
                'patient_name': t.patient_name,
                'type': t.get_ticket_type_display(),
                'called_at': t.called_at.strftime("%H:%M:%S"),
                'sala': t.room.name,
                'especialidade': t.room.especialidade.name,
            })
        return data

    async def receive(self, text_data=None, bytes_data=None):
        """
        Se o cliente WebSocket enviar alguma mensagem (por exemplo, 'get_initial'),
        retornamos as últimas 3 chamadas já no connect ou sob demanda.
        Opcional: poderíamos ignorar, pois vamos somente “pushar” updates.
        """
        # Exemplo para retornar as últimas 3 chamadas assim que o painel se conecta
        # ('text_data' não é usado aqui, mas poderia controlar pipes diferentes)
        last_three = await self.get_last_three()
        await self.send(text_data=json.dumps({
            'last_three': last_three
        }))

# core/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from .models import Ticket

class MedicoConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        """
        Ao conectar, recebemos o parâmetro 'room_id' na URL do WebSocket.
        Entramos no grupo 'medico_sala_<room_id>'.
        """
        # Ex: path(ws/medico/sala/5/) => room_id = '5'
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.group_name = f"medico_sala_{self.room_id}"

        # Adiciona este canal ao grupo
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        # Remove do grupo
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def receive(self, text_data=None, bytes_data=None):
        """
        Opcional: podemos ignorar mensagens enviadas pelo cliente,
        pois só faremos “push” de novas senhas do servidor → cliente.
        """
        pass

    async def new_ticket(self, event):
        """
        Este método é chamado quando o servidor faz:
            channel_layer.group_send(
                "medico_sala_<room_id>",
                {"type": "new_ticket", "ticket": {…}}
            )
        """
        # 'event["ticket"]' já deve estar serializado como dict com campos que interessam
        await self.send(text_data=json.dumps({
            "ticket": event["ticket"]
        }))

    @sync_to_async
    def get_tickets_for_room(self):
        """
        Retorna lista de tickets pendentes (ou seja,
        is_called=False) para esta sala.
        Pode ser usado via JS inicial para renderizar a lista toda.
        (Opcional: se já carregamos no template, talvez não precise.)
        """
        # Filtra tickets não chamados (se quiser mostrar só pendentes)
        return list(
            Ticket.objects.filter(
                room_id=self.room_id, 
                is_called=False
            ).order_by("issued_at")
            .values(
                "id", "code", "patient_name",
                "ticket_type", "issued_at"
            )
        )

# core/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from .models import Ticket
from asgiref.sync import sync_to_async

class TriagemConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Grupo “triagem”
        await self.channel_layer.group_add('triagem', self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard('triagem', self.channel_name)

    # Recebe do server quando um novo ticket chega à triagem
    async def new_ticket_triagem(self, event):
        await self.send(text_data=json.dumps({
            'ticket': event['ticket']
        }))

    @sync_to_async
    def get_pendentes(self):
        """
        Retorna todos os tickets pendentes na Sala Triagem
        (is_called=False e room=triagem).
        """
        triagem_room = Ticket.objects.filter(room__name__icontains="Triagem").first().room
        qs = Ticket.objects.filter(room=triagem_room, is_called=False).order_by('issued_at')
        data = []
        for t in qs:
            data.append({
                'id': t.id,
                'code': t.code,
                'patient_name': t.patient_name,
                'ticket_type': t.get_ticket_type_display(),
                'issued_at': t.issued_at.strftime("%H:%M:%S"),
            })
        return data

    # Opcional: quando o cliente enviar “get_initial”, retornamos lista inicial
    async def receive(self, text_data=None, bytes_data=None):
        pendentes = await self.get_pendentes()
        await self.send(text_data=json.dumps({
            'initial': pendentes
        }))
