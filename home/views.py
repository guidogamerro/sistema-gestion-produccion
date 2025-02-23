from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from gestion_lotes.models import Lote, Mezcla, Despacho
import json
from django.db.models import Sum, Count
from django.utils.dateparse import parse_date

@login_required
def pagina_inicial(request):
    return render(request, 'home/index.html')


def dashboard(request):

    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    lotes = Lote.objects.all()
    mezclas = Mezcla.objects.all()
    total_lotes = Lote.objects.count()
    cantidad_producida = lotes.aggregate(Sum('cantidad'))['cantidad__sum']
    #total_mezclas = Mezcla.objects.count()
    stock_total = sum(lote.stock for lote in Lote.objects.all())
    despachos = Despacho.objects.all()
    total_despachos = Despacho.objects.count()
    cantidad_despachada = despachos.aggregate(Sum('cantidad'))['cantidad__sum']
    
    if start_date and end_date:
        start_date = parse_date(start_date)
        end_date = parse_date(end_date)
        lotes = lotes.filter(fecha_inicio__range=(start_date, end_date))
        despachos = despachos.filter(ffecha_despacho__range=(start_date, end_date))
        #mezclas = mezclas.filter(fecha_creacion__gte=start_date, fecha_creacion__lte=end_date)
        total_lotes = Lote.objects.filter(fecha_inicio__range=(start_date, end_date)).count()
        cantidad_producida = lotes.aggregate(Sum('cantidad'))['cantidad__sum']
        total_despachos = Despacho.objects.filter(fecha_despacho__range=(start_date, end_date)).count()
        cantidad_despachada = despachos.aggregate(Sum('cantidad'))['cantidad__sum']
    elif start_date:
            start_date = parse_date(start_date)
            lotes = lotes.filter(fecha_inicio__gte=start_date)
            despachos = despachos.filter(fecha_despacho__gte=start_date)
            total_lotes = Lote.objects.filter(fecha_inicio__gte=start_date).count()
            cantidad_producida = lotes.aggregate(Sum('cantidad'))['cantidad__sum']
            total_despachos = Despacho.objects.filter(fecha_despacho__gte=start_date).count()
            cantidad_despachada = despachos.aggregate(Sum('cantidad'))['cantidad__sum']
    elif end_date:
        end_date = parse_date(end_date)
        lotes = lotes.filter(fecha_inicio__lte=end_date)
        despachos = despachos.filter(fecha_despacho__lte=end_date)
        total_lotes = Lote.objects.filter(fecha_inicio__lte=end_date).count()
        cantidad_producida = lotes.aggregate(Sum('cantidad'))['cantidad__sum']
        total_despachos = Despacho.objects.filter(fecha_despacho__lte=end_date).count()
        cantidad_despachada = despachos.aggregate(Sum('cantidad'))['cantidad__sum']

    ppp = (
        lotes.values('producto')
        .annotate(cantidad_total=Sum('cantidad'),  lotes_totales=Count('id'))
        .order_by('producto')
    )

    ppp_serie = [
        {
            'producto': i['producto'],
            'cantidad_total': float(i['cantidad_total']) if i['cantidad_total'] else 0.0,
            'lotes_totales': i['lotes_totales']
        }
        for i in ppp
    ]

    despacho_por_cliente = (
         despachos.values('cliente')
         .annotate(cantidad_total=Sum('cantidad'), lotes_totales=Count('id'))
         .order_by('-cliente')
    )

    mezclas_por_producto = (
        mezclas.values('producto')
        .annotate(total_mezclas=Sum('cantidad_total'))
        .order_by('producto')
    )

    productos = Lote.objects.values('producto').distinct()
    produccion_por_producto = [
        {
            'producto': p['producto'],
            'cantidad': Lote.objects.filter(producto=p['producto']).count(),
        }
        for p in productos
    ]

    context = {
        'total_lotes': total_lotes,
        'cantidad_producida': cantidad_producida,
        'stock_total': stock_total,
        'produccion_por_producto': json.dumps(produccion_por_producto),
        'mezclas_por_producto': json.dumps(list(mezclas_por_producto)),
        'ppp_serie': json.dumps(ppp_serie),
        'total_despachos': total_despachos,
        'cantidad_despachada': cantidad_despachada,
        'despacho_por_cliente': json.dumps(list(despacho_por_cliente))
    }

    return render(request, 'home/dashboard.html', context)