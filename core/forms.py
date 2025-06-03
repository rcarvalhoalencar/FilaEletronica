from django import forms
from .models import Ticket, Sala

class TicketForm(forms.ModelForm):
    class Meta:
        model = Ticket
        # Campos que o usuário irá preencher ao emitir uma senha:
        fields = ['patient_name', 'ticket_type', 'room']
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'placeholder': 'Nome completo do paciente',
                'class': 'mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'ticket_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'room': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
        }
