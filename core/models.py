from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('recepcao', 'Recepção'),
        ('triagem',  'Triagem'),
        ('medico', 'Médico'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES)

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"


class Especialidade(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Sala(models.Model):
    name = models.CharField(max_length=50, unique=True)
    especialidade = models.ForeignKey(Especialidade, on_delete=models.CASCADE)

    def __str__(self):
        return f"Sala {self.name} - {self.especialidade.name}"


# core/models.py

from django.db import models
from django.utils import timezone

class Ticket(models.Model):
    TICKET_TYPES = (
        ('U', 'Urgência'),
        ('P', 'Prioridade'),
        ('N', 'Normal'),
    )
    code = models.CharField(max_length=5, unique=True)
    patient_name = models.CharField(max_length=200)
    ticket_type = models.CharField(max_length=1, choices=TICKET_TYPES)
    issued_at = models.DateTimeField(default=timezone.now)
    called_at = models.DateTimeField(null=True, blank=True)
    room = models.ForeignKey('Sala', on_delete=models.CASCADE)
    is_called = models.BooleanField(default=False)

    class Meta:
        ordering = ['issued_at']

    def __str__(self):
        return f"{self.code} - {self.get_ticket_type_display()} - {self.patient_name}"

    def save(self, *args, **kwargs):
        # Só gera código se ainda não houver code atribuído
        if not self.code:
            hoje = timezone.localdate()

            # Busca o último ticket de mesmo tipo emitido hoje, ordenando pelo issued_at desc
            ultimo = (
                Ticket.objects
                .filter(ticket_type=self.ticket_type, issued_at__date=hoje)
                .order_by('-issued_at')
                .first()
            )

            if ultimo:
                # extrai a parte numérica do código anterior (ex.: 'U0005' -> 5)
                try:
                    ultimo_num = int(ultimo.code[1:])
                except ValueError:
                    ultimo_num = 0
                proximo_num = ultimo_num + 1
            else:
                proximo_num = 1

            # Monta o código, sempre com 4 dígitos depois da letra
            self.code = f"{self.ticket_type}{str(proximo_num).zfill(4)}"

            # Caso, ainda assim, ocorra colisão (raro), faz uma tentativa extra:
            # (Isso serve de “plano B” se outro save simultâneo surgir exatamente no mesmo instante.)
            # Tenta reaplicar o código até que seja único:
            tentativas = 0
            while Ticket.objects.filter(code=self.code).exists():
                tentativas += 1
                proximo_num += 1
                self.code = f"{self.ticket_type}{str(proximo_num).zfill(4)}"
                if tentativas > 10:
                    # Se por algum motivo ainda assim falhar repetidamente, interrompe
                    raise Exception("Falha ao gerar código único para Ticket após múltiplas tentativas.")

        super().save(*args, **kwargs)
