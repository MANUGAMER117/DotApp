from django import forms
from .models import Usuario, Perfil, Dotacion, Bodega, Inventario, Reserva, AlertaPreventiva, Devolucion, Operador


class StyledFormMixin:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            css = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = f'{css} form-control'.strip()


class UsuarioForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Usuario
        fields = ['nombre', 'email', 'cargo', 'fecha_contratacion', 'activo']
        widgets = {'fecha_contratacion': forms.DateInput(attrs={'type': 'date'})}


class PerfilForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Perfil
        fields = ['talla_vestido', 'talla_calzado', 'preferencia_ergonomica', 'requerimientos', 'proxima_entrega']
        widgets = {
            'requerimientos': forms.Textarea(attrs={'rows': 3}),
            'proxima_entrega': forms.DateInput(attrs={'type': 'date'}),
        }


class ReservaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['dotacion', 'fecha_programada', 'observaciones']
        widgets = {
            'fecha_programada': forms.DateInput(attrs={'type': 'date'}),
            'observaciones': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, usuario=None, **kwargs):
        super().__init__(*args, **kwargs)
        self.usuario = usuario
        self.fields['dotacion'].queryset = Dotacion.objects.all()


class AlertaPreventivaForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = AlertaPreventiva
        fields = ['fecha_programada', 'mensaje']
        widgets = {'fecha_programada': forms.DateInput(attrs={'type': 'date'}), 'mensaje': forms.Textarea(attrs={'rows': 4})}


class InventarioForm(StyledFormMixin, forms.Form):
    bodega = forms.ModelChoiceField(queryset=Bodega.objects.all())
    dotacion = forms.ModelChoiceField(queryset=Dotacion.objects.all())
    cantidad = forms.IntegerField(min_value=1, initial=1)


class DevolucionForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Devolucion
        fields = ['usuario', 'dotacion', 'bodega', 'causal', 'observaciones']
        widgets = {'observaciones': forms.Textarea(attrs={'rows': 3})}


class OperadorForm(StyledFormMixin, forms.ModelForm):
    class Meta:
        model = Operador
        fields = ['nombre', 'email', 'rol', 'activo', 'fecha_alta']
        widgets = {
            'fecha_alta': forms.DateInput(attrs={'type': 'date'}),
        }
