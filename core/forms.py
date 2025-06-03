from django import forms
from .models import Ticket, Sala

class TicketFormRecepcao(forms.ModelForm):
    class Meta:
        model = Ticket
        fields = ['patient_name', 'ticket_type']  # sem 'room'
        widgets = {
            'patient_name': forms.TextInput(attrs={
                'placeholder': 'Nome completo do paciente',
                'class': 'mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
            'ticket_type': forms.Select(attrs={
                'class': 'mt-1 block w-full px-3 py-2 bg-gray-50 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-green-500'
            }),
        }

    def save(self, commit=True):
        instance = super().save(commit=False)
        try:
            sala_triagem = Sala.objects.get(name__icontains="Triagem")
        except Sala.DoesNotExist:
            raise forms.ValidationError("Sala de Triagem não cadastrada.")
        instance.room = sala_triagem
        if commit:
            instance.save()
        return instance
