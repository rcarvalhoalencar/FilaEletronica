from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone

class Usuario(AbstractUser):
    ROLE_CHOICES = (
        ('recepcao', 'Recepção'),
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
    room = models.ForeignKey(Sala, on_delete=models.CASCADE)
    is_called = models.BooleanField(default=False)

    class Meta:
        ordering = ['issued_at']

    def __str__(self):
        return f"{self.code} - {self.get_ticket_type_display()} - {self.patient_name}"

    def save(self, *args, **kwargs):
        # Se não tiver código, gera um novo para hoje
        if not self.code:
            hoje = timezone.localdate()
            count_same_type = Ticket.objects.filter(
                ticket_type=self.ticket_type,
                issued_at__date=hoje
            ).count() + 1
            prefix = self.ticket_type
            self.code = f"{prefix}{str(count_same_type).zfill(4)}"
        super().save(*args, **kwargs)
