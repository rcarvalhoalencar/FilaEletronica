from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .decorators import recepcao_required, medico_required
from .models import Especialidade, Sala, Ticket, Usuario
from django import forms
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_GET
from django.views.generic import TemplateView
from .forms import TicketForm


# core/views.py

from django.shortcuts import get_object_or_404, redirect
from django.utils import timezone
from django.http import HttpResponseForbidden
from .models import Ticket
from .decorators import medico_required

# Import extra para Channels
from asgiref.sync import async_to_sync

# ----------------------
# FORMS de Recepção
# ----------------------
class EspecialidadeForm(forms.ModelForm):
    class Meta:
        model = Especialidade
        fields = ['name']
        widgets = {'name': forms.TextInput(attrs={'placeholder': 'Nome da especialidade'})}

class SalaForm(forms.ModelForm):
    class Meta:
        model = Sala
        fields = ['name', 'especialidade']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Ex: Sala 01'}),
            'especialidade': forms.Select()
        }

class EmitirTicketForm(forms.Form):
    patient_name = forms.CharField(max_length=200, label="Nome completo do paciente")
    ticket_type = forms.ChoiceField(choices=Ticket.TICKET_TYPES, label="Tipo de senha")
    room = forms.ModelChoiceField(queryset=Sala.objects.all(), label="Sala (especialidade)")

# ----------------------
# VIEWS
# ----------------------
@login_required
def home(request):
    if request.user.role == 'recepcao':
        return redirect('recepcao_dashboard')
    elif request.user.role == 'medico':
        return redirect('medico_dashboard')
    else:
        return redirect('login')


# ---- RECEPÇÃO ----
@recepcao_required
def recepcao_dashboard(request):
    """
    Dashboard da recepção:
    - Lista de especialidades
    - Lista de salas
    - Link para emissão de nova senha
    - Tabela com todas as senhas emitidas hoje e seu status.
    """
    # 1. Consulta de especialidades e salas (como antes)
    especialidades = Especialidade.objects.all().order_by('name')
    salas = Sala.objects.select_related('especialidade').all().order_by('name')

    # 2. Filtrar tickets emitidos hoje (usando issued_at)
    hoje = timezone.localdate()
    tickets_hoje = Ticket.objects.filter(
        issued_at__date=hoje
    ).select_related('room', 'room__especialidade').order_by('-issued_at')

    context = {
        'especialidades': especialidades,
        'salas': salas,
        'tickets_hoje': tickets_hoje,
    }
    return render(request, 'recepcao/dashboard.html', context)
@recepcao_required
def cadastrar_especialidade(request):
    if request.method == 'POST':
        form = EspecialidadeForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Especialidade cadastrada com sucesso.")
            return redirect('recepcao_dashboard')
    else:
        form = EspecialidadeForm()
    return render(request, 'recepcao/cadastrar_especialidade.html', {'form': form})

@recepcao_required
def cadastrar_sala(request):
    if request.method == 'POST':
        form = SalaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Sala cadastrada com sucesso.")
            return redirect('recepcao_dashboard')
    else:
        form = SalaForm()
    return render(request, 'recepcao/cadastrar_sala.html', {'form': form})

@recepcao_required
def editar_sala(request, sala_id):
    """
    View para editar uma Sala existente.
    Carrega a instância, pré-preenche o formulário e salva as alterações.
    """
    sala = get_object_or_404(Sala, id=sala_id)

    if request.method == 'POST':
        form = SalaForm(request.POST, instance=sala)
        if form.is_valid():
            form.save()
            messages.success(request, f"Sala '{sala.name}' atualizada com sucesso.")
            return redirect('recepcao_dashboard')
    else:
        form = SalaForm(instance=sala)

    return render(request, 'recepcao/editar_sala.html', {'form': form, 'sala': sala})


@recepcao_required
def emitir_senha(request):
    """
    View que emite uma nova senha. Após salvar, notifica o grupo do médico
    via channel_layer.group_send().
    """
    if request.method == 'POST':
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save()  # Isso já atribui code, issued_at, etc.

            # Monta o dicionário que vamos enviar ao consumer
            ticket_data = {
                "id": ticket.id,
                "code": ticket.code,
                "patient_name": ticket.patient_name,
                "ticket_type": ticket.get_ticket_type_display(),
                "issued_at": ticket.issued_at.strftime("%H:%M:%S"),
                "room": ticket.room.name,
                "especialidade": ticket.room.especialidade.name,
            }

            # Pega o canal layer
            channel_layer = get_channel_layer()
            group_name = f"medico_sala_{ticket.room.id}"

            # Dispara o evento "new_ticket" para todos os médicos naquela sala
            async_to_sync(channel_layer.group_send)(
                group_name,
                {
                    "type": "new_ticket",     # Vai chamarMedicoConsumer.new_ticket()
                    "ticket": ticket_data
                }
            )

            messages.success(request, f"Senha {ticket.code} emitida com sucesso.")
            return redirect('recepcao_dashboard')
    else:
        form = TicketForm()

    return render(request, 'recepcao/emitir_senha.html', {'form': form})

# ---- MÉDICO ----
@medico_required
def medico_dashboard(request):
    salas = Sala.objects.all()
    context = {'salas': salas}
    return render(request, 'medico/dashboard.html', context)

@medico_required
def sala_tickets(request, sala_id):
    # 1. Busca a instância da sala
    sala = get_object_or_404(Sala, id=sala_id)

    # 2. Tickets pendentes: todos os tickets desta sala com is_called=False
    tickets_pendentes = Ticket.objects.filter(
        room=sala,
        is_called=False
    ).order_by("issued_at")

    # 3. Tickets já chamados (opcional, se você quiser exibir)
    tickets_chamados = Ticket.objects.filter(
        room=sala,
        is_called=True
    ).order_by("-called_at")[:10]

    return render(request, 'medico/sala_tickets.html', {
        'sala': sala,
        'tickets_pendentes': tickets_pendentes,
        'tickets_chamados': tickets_chamados,
    })

# Import extra para Channels
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

@medico_required
@medico_required
def chamar_ticket(request, ticket_id):
    ticket = get_object_or_404(Ticket, id=ticket_id)
    if ticket.is_called:
        # “Rechamar” opcionalmente não bloqueia; aqui apenas reagendamos a chamada:
        # return HttpResponseForbidden("Ticket já foi chamado.")
        # Para atualização em tempo real, podemos deixar atualizar o called_at de novo.
        pass

    # Atualiza o ticket no banco
    ticket.called_at = timezone.now()
    ticket.is_called = True
    ticket.save()

    # Agora vamos enviar mensagem ao grupo 'painel_tickets'
    channel_layer = get_channel_layer()
    
    # Prepara os dados: buscamos as últimas 3 chamadas diretamente
    latest_three = []
    chamados = Ticket.objects.filter(is_called=True).order_by('-called_at')[:3]
    for t in chamados:
        latest_three.append({
            'code': t.code,
            'patient_name': t.patient_name,
            'type': t.get_ticket_type_display(),
            'called_at': t.called_at.strftime("%H:%M:%S"),
            'sala': t.room.name,
            'especialidade': t.room.especialidade.name,
        })

    # Dispara o evento sincronicamente (por causa da view ser síncrona)
    async_to_sync(channel_layer.group_send)(
        'painel_tickets',  # grupo que criamos no consumer
        {
            'type': 'ticket_chamado',   # deve bater com o nome do método no consumer
            'last_three': latest_three, # payload que será enviado ao JS
        }
    )

    # Redireciona de volta para a lista de tickets da mesma sala
    return redirect('sala_tickets', sala_id=ticket.room.id)

# ---- PÚBLICO ----
@require_GET
def publico_ultimas(request):
    last_three = Ticket.objects.filter(is_called=True).order_by('-called_at')[:3]
    data = []
    for t in last_three:
        data.append({
            'code': t.code,
            'patient_name': t.patient_name,
            'type': t.get_ticket_type_display(),
            'called_at': t.called_at.strftime("%H:%M:%S"),
            'sala': t.room.name,
            'especialidade': t.room.especialidade.name,
        })
    return JsonResponse({'last_three': data})

# View que apenas renderiza o template do painel público
class PublicoPainelView(TemplateView):
    template_name = 'publico/ultimas_chamadas.html'

# Se preferir função em vez de classe, basta:
# def publico_painel(request):
#     return render(request, 'publico/ultimas_chamadas.html')

from django.shortcuts import render

def publico_painel(request):
    return render(request, 'publico/ultimas_chamadas.html')
