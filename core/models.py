from django.db import models


# Create your models here.

class LogSimples(models.Model):
    # Campo para a mensagem principal do log
    mensagem = models.TextField(
        verbose_name='Mensagem do Log'
    )

    # Campo para registrar o horário exato do evento
    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Data/Hora'
    )

    # Campo para categorizar o evento (ex: 'Alerta', 'Erro', 'Info')
    categoria = models.CharField(
        max_length=50,
        default='INFO',
        verbose_name='Categoria'
    )

    class Meta:
        verbose_name = 'Log Simples'
        verbose_name_plural = 'Logs Simples'
        # Garante que os logs mais recentes apareçam primeiro
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.categoria}] {self.timestamp.strftime('%Y-%m-%d %H:%M')} - {self.mensagem[:50]}..."

class ModelBase(models.Model):
    id = models.BigAutoField(
        db_column='id',
        null=False,
        primary_key=True
    )
    created = models.DateTimeField(
        db_column='dt_created',
        auto_now_add=True,
        null=True
    )
    modified_at = models.DateTimeField(
        db_column='dt_modified',
        auto_now=True,
        null=True
    )
    active = models.BooleanField(
        db_column='cs_active',
        null=False,
        default=True
    )

    class Meta:
        abstract = True
        managed = True


class Product(ModelBase):
    description = models.TextField(
        db_column='description',
        null=False
    )

    quantity = models.IntegerField(
        db_column='quantity',
        null=False,
        default=0
    )

    def __str__(self):
        return self.description

    class Meta:
        db_table = 'product'


class Client(ModelBase):
    name = models.CharField(
        db_column='description',
        max_length=70,
        null=False
    )

    age = models.IntegerField(
        db_column='age',
        null=False
    )

    rg = models.CharField(
        db_column='rg',
        max_length=12,
        null=False
    )

    cpf = models.CharField(
        db_column='cpf',
        max_length=12,
        null=False
    )

    def __str__(self):
        return '{} - {}'.format(self.cpf, self.name)

    class Meta:
        db_table = 'client'


class Employee(ModelBase):
    name = models.CharField(
        db_column='name',
        max_length=70,
        null=False
    )

    registration = models.CharField(
        db_column='registration',
        max_length=15,
        null=False,
        default=0
    )

    def __str__(self):
        return self.name

    class Meta:
        db_table = 'employee'


class Sale(ModelBase):
    product = models.ForeignKey(
        Product,
        db_column='id_product',
        null=False,
        on_delete=models.DO_NOTHING
    )

    client = models.ForeignKey(
        Client,
        db_column='id_client',
        null=False,
        on_delete=models.DO_NOTHING
    )

    employee = models.ForeignKey(
        Employee,
        db_column='id_employee',
        null=False,
        on_delete=models.DO_NOTHING
    )

    nrf = models.CharField(
        db_column='nrf',
        max_length=255,
        null=False
    )

    class Meta:
        db_table = 'sale'

    #Mudança na feat/logs
