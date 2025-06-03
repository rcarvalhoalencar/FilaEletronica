# fila_ubs/urls.py

from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from core import views

urlpatterns = [
    # 1. Raiz: home redireciona conforme role (ou para login, se não autenticado)
    path('', views.home, name='home'),

    # 2. Rotas da Recepção
    path('recepcao/dashboard/',                views.recepcao_dashboard,     name='recepcao_dashboard'),
    path('recepcao/cadastrar-especialidade/',  views.cadastrar_especialidade, name='cadastrar_especialidade'),
    path('recepcao/cadastrar-sala/',           views.cadastrar_sala,          name='cadastrar_sala'),
    path('recepcao/editar-sala/<int:sala_id>/',views.editar_sala,            name='editar_sala'),
    path('recepcao/emitir-senha/',             views.emitir_senha,            name='emitir_senha'),

    # 3. Rotas do Médico
    path('medico/dashboard/',       views.medico_dashboard, name='medico_dashboard'),
    path('medico/sala/<int:sala_id>/', views.sala_tickets,    name='sala_tickets'),
    path('medico/chamar/<int:ticket_id>/', views.chamar_ticket, name='chamar_ticket'),

    # 4. Tela pública de últimas chamadas
    path('publico/ultimas-chamadas-json/', views.publico_ultimas, name='publico_ultimas'),
    path('publico/painel/',               views.publico_painel,   name='publico_painel'),

    # 5. URLs de autenticação (login/logout)
    path('accounts/', include('django.contrib.auth.urls')),

    # 6. Rotas da Triagem
    path('triagem/dashboard/',          views.triagem_dashboard,   name='triagem_dashboard'),
    path('triagem/reenviar/<int:ticket_id>/', views.triagem_reenviar, name='triagem_reenviar'),

    # 7. Admin
    path('admin/', admin.site.urls),
]