from django.urls import path
from . import views
from django.views.generic import TemplateView


urlpatterns = [
    # home redireciona conforme role
    path('', views.home, name='home'),

    # Recepção
    path('recepcao/dashboard/', views.recepcao_dashboard, name='recepcao_dashboard'),
    path('recepcao/cadastrar-especialidade/', views.cadastrar_especialidade, name='cadastrar_especialidade'),
    path('recepcao/cadastrar-sala/', views.cadastrar_sala, name='cadastrar_sala'),
    path('recepcao/editar-sala/<int:sala_id>/', views.editar_sala, name='editar_sala'),
    path('recepcao/emitir-senha/', views.emitir_senha, name='emitir_senha'),

    # Médico
    path('medico/dashboard/', views.medico_dashboard, name='medico_dashboard'),
    path('medico/sala/<int:sala_id>/', views.sala_tickets, name='sala_tickets'),
    path('medico/chamar/<int:ticket_id>/', views.chamar_ticket, name='chamar_ticket'),

        # Tela pública de últimas chamadas
    path('publico/ultimas-chamadas-json/', views.publico_ultimas, name='publico_ultimas'),
    path('publico/painel/', views.publico_painel, name='publico_painel'),
]
