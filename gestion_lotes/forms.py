from django import forms
from .models import Lote, Mezcla, Despacho

class LoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nombre_lote', 'fecha_inicio', 'estado', 'producto', 'tipo', 'fecha_fin', 'cantidad']
        widgets = {
            'fecha_inicio': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'fecha_fin': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'})
        }
        error_messages = {'nombre_lote': {'unique': "Ya existe un lote con este nombre."}}

class LoteFiltroForm(forms.Form):
    nombre_lote = forms.CharField(max_length=100, required=False, label='Nombre del lote')
    producto = forms.ChoiceField(choices=[('','Todos')] + Lote._meta.get_field('producto').choices, required=False, label='Producto')
    fecha_inicio = forms.DateField(label="Fecha de Inicio", widget=forms.DateInput(attrs={'type': 'date'}), required=False)
    estado = forms.ChoiceField(label='Estado', choices=[('', '---'), ('iniciado', 'Iniciado'), ('finalizado', 'Finalizado')], required=False)
    fecha_inicio_desde = forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False, label='Fecha de inicio desde:')
    fecha_inicio_hasta= forms.DateField(widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=False, label='Fecha de inicio hasta:')
    stock = forms.IntegerField(required=False)
    tipo_modelo = forms.ChoiceField(
        required=False,
        choices=[('todos', 'Todos'), ('lote', 'Lote'), ('mezcla', 'Mezcla')],
        label='Modelo'
    )

class DetalleLoteForm(forms.ModelForm):
    class Meta:
        model = Lote
        fields = ['nombre_lote', 'fecha_inicio', 'estado', 'producto', 'tipo', 'fecha_fin', 'cantidad', 'calidad1', 'calidad2', 'stock']

class MezclaForm(forms.ModelForm):
    class Meta:
        model = Mezcla
        fields = ['nombre_mezcla']


class DespachoForm(forms.ModelForm):
    class Meta:
        model = Despacho
        fields = ['mezcla','cliente', 'cantidad', 'fecha_despacho']
        widget = {'fecha_despacho': forms.DateInput(attrs={'type':'date'})}

    def clean_cantidad(self):
        cantidad = self.cleaned_data.get('cantidad')
        if cantidad <= 0:
            raise forms.ValidationError("La cantidad debe ser mayor a 0.")
        return cantidad
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['mezcla'].queryset = Mezcla.objects.filter(stock_restante__gt=0)

    
class DetalleMezclaForm(forms.ModelForm):
    class Meta:
        model = Mezcla
        fields = ['nombre_mezcla', 'cantidad_total', 'lotes', 'destino', 'stock_restante']