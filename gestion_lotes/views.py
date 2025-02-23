from django.shortcuts import render, get_object_or_404, redirect
from .models import Lote, Mezcla, LoteEnMezcla, Despacho
from .forms import LoteForm, LoteFiltroForm, DetalleLoteForm, MezclaForm, DespachoForm, DetalleMezclaForm
from django.contrib import messages
import openpyxl
from django.http import HttpResponse
from rest_framework import viewsets
from .serializers import LoteSerializer

#probando api rest
class LoteViewSet(viewsets.ModelViewSet):
    queryset = Lote.objects.all()
    serializer_class = LoteSerializer

#Lista de lotes (CRUD --> R|read)
def lista_lotes(request):

    form = LoteFiltroForm(request.GET or None)
    lotes = Lote.objects.all().order_by('-fecha_inicio')
    mezclas = Mezcla.objects.all().order_by('nombre_mezcla')

    if form.is_valid():

        fid = form.cleaned_data.get('fecha_inicio_desde')
        fih = form.cleaned_data.get('fecha_inicio_hasta')
        nombre = form.cleaned_data['nombre_lote']
        producto = form.cleaned_data['producto']
        estado = form.cleaned_data['estado']

        if nombre:
            lotes = lotes.filter(nombre_lote__icontains=nombre)
            mezclas = mezclas.filter(nombre_mezcla__icontains=nombre)
        if producto:
            lotes = lotes.filter(producto=producto)
            mezclas = mezclas.filter(producto=producto)
        if estado == 'iniciado':
            mezclas = Mezcla.objects.none()
            lotes = lotes.filter(estado=estado)
        if estado =='finalizado':
            lotes = lotes.filter(estado=estado)
        if fid and fih:
            lotes = lotes.filter(fecha_inicio__range=(fid, fih))
        elif fid:
            lotes = lotes.filter(fecha_inicio__gte=fid)
        elif fih:
            lotes = lotes.filter(fecha_inicio__lte=fih)

    lista_total = list(lotes) + list(mezclas)

    lista_total.sort(key=lambda x: getattr(x, 'fid', getattr(x, 'nombre_mezcla', '')))

    ctx = {'form': form, 'lista_total': lista_total}

    return render(request, 'gestion_lotes/lista_lotes.html', ctx)

#Crear lote (C|create)
def crear_lote(request):
    if request.method == 'POST':
        form = LoteForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('gestion_lotes:lista_lotes')
    else:
        form = LoteForm()
    return render(request, 'gestion_lotes/crear_lote.html', {'form':form})

#Actualizar un lote (U|update)
def editar_lote(request, lote_id):
    lote = get_object_or_404(Lote, pk=lote_id)
    if request.method =='POST':
        form = LoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            return redirect('gestion_lotes:lista_lotes')
    else:
        form = LoteForm(instance = lote)
    return render(request, 'gestion_lotes/editar_lote.html', {'form':form})

#Elimnar lote (D|delete)
def eliminar_lote(request, lote_id):
    lote = get_object_or_404(Lote, pk=lote_id)
    if request.method == 'POST':
        lote.delete()
        return redirect('gestion_lotes:lista_lotes')
    return render(request, 'gestion_lotes/eliminar_lote.html', {'lote':lote})


#Detalles del lote
def detalle_lote(request, pk):
    lote = get_object_or_404(Lote, pk=pk)
    mezclas_usadas = LoteEnMezcla.objects.filter(lote=lote).select_related('mezcla')

    if request.method == 'POST':
        form = DetalleLoteForm(request.POST, instance=lote)
        if form.is_valid():
            form.save()
            return redirect('gestion_lotes:lista_lotes')
    else:
        form = DetalleLoteForm(instance=lote)
        
    ctx = {'lote': lote, 'mezclas_usadas': mezclas_usadas, 'form': form}

    return render(request, 'gestion_lotes/detalle_lote.html', ctx)

#Stock de productos
def stock_producto(request):
    lotes_stock = Lote.objects.filter(estado = 'finalizado', stock__gt=0, state = 'Activo').order_by('producto')
    mezclas_stock = Mezcla.objects.filter(stock_restante__gt=0)

    form = LoteFiltroForm(request.GET or None)

    if form.is_valid():
        nombre = form.cleaned_data.get('nombre_lote')
        producto = form.cleaned_data.get('producto')
        tipo_modelo = form.cleaned_data.get('tipo_modelo')

        if nombre:
            lotes_stock = lotes_stock.filter(nombre_lote__icontains=nombre)
            mezclas_stock = mezclas_stock.filter(nombre_mezcla__icontains=nombre)
        if producto:
            lotes_stock = lotes_stock.filter(producto__icontains=producto)
            mezclas_stock = mezclas_stock.filter(producto__icontains=producto)
        if tipo_modelo == 'lote':
            mezclas_stock = Mezcla.objects.none()  # No mostrar mezclas
        elif tipo_modelo == 'mezcla':
            lotes_stock = Lote.objects.none()

    stock_total = list(lotes_stock) + list(mezclas_stock)

    stock_total.sort(key=lambda x: getattr(x, 'nombre_lote', getattr(x, 'nombre_mezcla', '')))

    ctx = {'form': form, 'stock_total': stock_total}

    return render(request, 'gestion_lotes/stock_producto.html', ctx)


def crear_mezcla(request):
    lotes = Lote.objects.filter(stock__gt=0, estado='finalizado')

    if request.method == 'POST':
        form = MezclaForm(request.POST)

        if form.is_valid():
            nombre_mezcla = form.cleaned_data['nombre_mezcla']
            mezcla = Mezcla(nombre_mezcla = nombre_mezcla, cantidad_total=0)
            mezcla.save()
            lotes = request.POST.getlist('lmez')
            cantidades = request.POST.getlist('cant')
            cantidad_total = 0

            lotesp = Lote.objects.filter(id__in=lotes)
            productos = set(lote.producto for lote in lotesp)
            if len(productos) > 1:
                messages.error(request, "No se puede crear la mezcla con lotes de diferentes productos.")
                mezcla.delete()
                return redirect('gestion_lotes:crear_mezcla')
            mezcla.producto = productos.pop()

            for lmez, cant  in zip(lotes,cantidades):
                if cant:
                    cantidad = int(cant)
                    lote = Lote.objects.get(id=lmez)
                        
                    if lote.stock >= cantidad:
                        LoteEnMezcla.objects.create(mezcla=mezcla, lote=lote, cantidad=cantidad)
                        lote.stock -= cantidad
                        lote.usado = True
                        lote.save()
                    else:
                        messages.error(request, f"No hay suficiente stock en el lote {lote.nombre_lote}")
                        mezcla.delete()
                        return redirect('gestion_lotes:crear_mezcla')
                cantidad_total += cantidad
            mezcla.cantidad_total = cantidad_total
            mezcla.stock_restante = cantidad_total  
            mezcla.save()  
            messages.success(request, 'Mezcla creada exitosamente.')
            return redirect('gestion_lotes:stock_producto')
        else:
            messages.error(request, 'Error en el formulario.')
    else:
        form = MezclaForm()
    return render(request, 'gestion_lotes/crear_mezcla.html', {'form': form, 'lotes': lotes})


def despachos(request):
    despachos = Despacho.objects.all().order_by('-fecha_despacho')

    form = LoteFiltroForm(request.GET or None)

    if form.is_valid():

        nombre = form.cleaned_data.get('nombre_lote')
        producto = form.cleaned_data.get('producto')
        fid = form.cleaned_data.get('fecha_inicio_desde')
        fih = form.cleaned_data.get('fecha_inicio_hasta')
        cliente = form.cleaned_data.get('cliente')

        if nombre:
            despachos = despachos.filter(mezcla__nombre_mezcla=nombre)
        if producto:
            despachos = despachos.filter(mezcla__producto=producto)
        if cliente:
            despachos = despachos.filter(cliente__icontains=cliente)
        if fid and fih:
            despachos = despachos.filter(fecha_despacho__range=(fid, fih))
        elif fid:
            despachos = despachos.filter(fecha_despacho__gte=fid)
        elif fih:
            despachos = despachos.filter(fecha_despacho__lte=fih)

    ctx = {'despachos': despachos, 'form': form}
    return render(request, 'gestion_lotes/lista_despachos.html', ctx)


def nuevo_despacho(request):
    mezclas = Mezcla.objects.filter(stock_restante__gt=0)

    if request.method == 'POST':
        form = DespachoForm(request.POST)

        if form.is_valid():
            despacho = form.save(commit=False)
            cantidad = despacho.cantidad
            mezcla = despacho.mezcla

            if cantidad > mezcla.stock_restante:
                messages.error(request, "La cantidad a despachar excede el stock disponible.")
                return redirect('gestion_lotes:nuevo_despacho')
            
            despacho.save()

            mezcla.stock_restante -= cantidad
            mezcla.save()

            return redirect('gestion_lotes:stock_producto')

    else:
        form = DespachoForm()

    return render(request, 'gestion_lotes/nuevo_despacho.html', {'mezclas': mezclas, 'form': form})

def registrar_despacho(request, pk):
    mezcla = get_object_or_404(Mezcla, pk=pk)
    
    if request.method == 'POST':
        form = DespachoForm(request.POST)

        if form.is_valid():
            despacho = form.save(commit=False)
            cantidad = despacho.cantidad

            if cantidad > mezcla.stock_restante:
                messages.error(request, "La cantidad a despachar excede el stock disponible.")
                return redirect('gestion_lotes:stock_producto')

            despacho.mezcla = mezcla
            despacho.save()

            mezcla.stock_restante -= cantidad
            mezcla.save()

            messages.success(request, f"Se ha registrado el despacho de {cantidad} unidades a {despacho.cliente}.")
            return redirect('gestion_lotes:lista_despachos')
        
    else:
        form = DespachoForm()

    return render(request, 'gestion_lotes/registrar_despacho.html', {'mezcla': mezcla, 'form': form})


def detalle_mezcla(request, pk):
    mezcla = get_object_or_404(Mezcla, pk=pk)

    if request.method == 'POST':
        form = DetalleMezclaForm(request.POST, instance=mezcla)
        if form.is_valid():
            form.save()
            return redirect('gestion_lotes:detalle_mezcla')
    else:
        form = DetalleMezclaForm

    despachos = mezcla.despachos.all()
    lotes = LoteEnMezcla.objects.filter(mezcla=mezcla)
    ctx = {'mezcla': mezcla, 'form': form, 'despachos': despachos, 'lotes': lotes}

    return render(request, 'gestion_lotes/detalle_mezcla.html', ctx)

#Exporta en excel no funciona bien los filtros pero aqui esta la idea principal. Igual, se como arreglarlo.
def exportar_excel(request):
    nombre_lote = request.GET.get('nombre_lote')
    producto = request.GET.get('producto')
    fecha_inicio = request.GET.get('fecha_inicio')
    fecha_fin = request.GET.get('fecha_fin')

    lotes = Lote.objects.all()

    if nombre_lote:
        lotes = lotes.filter(nombre_lote__icontains=nombre_lote)
    if producto:
        lotes = lotes.filter(producto__icontains=producto)
    if fecha_inicio:
        lotes = lotes.filter(fecha_inicio__gte=fecha_inicio)
    if fecha_fin:
        lotes = lotes.filter(fecha_fin__lte=fecha_fin)

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = 'Lotes Filtrados'

    headers = ['ID', 'Nombre Lote', 'Producto', 'Fecha Inicio', 'Fecha Fin', 'Cantidad', 'Stock']
    ws.append(headers)

    for lote in lotes:
        ws.append([
            lote.id,
            lote.nombre_lote,
            lote.producto,
            lote.fecha_inicio,
            lote.fecha_fin,
            lote.cantidad,
        ])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=lotes_filtrados.xlsx'
    wb.save(response)

    return response