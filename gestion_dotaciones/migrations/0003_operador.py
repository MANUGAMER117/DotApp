# Generated manually for the Operadores module.
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ('gestion_dotaciones', '0002_bodega_alter_alertapreventiva_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='Operador',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('nombre', models.CharField(max_length=100)),
                ('email', models.EmailField(max_length=254, unique=True)),
                ('rol', models.CharField(choices=[
                    ('administrador', 'Administrador'),
                    ('rh', 'Recursos Humanos'),
                    ('bodega', 'Encargado de Bodega'),
                    ('compras', 'Compras'),
                ], default='bodega', max_length=30)),
                ('activo', models.BooleanField(default=True)),
                ('fecha_alta', models.DateField(default=django.utils.timezone.localdate)),
            ],
            options={
                'verbose_name': 'Operador',
                'verbose_name_plural': 'Operadores',
                'ordering': ['nombre'],
            },
        ),
    ]
