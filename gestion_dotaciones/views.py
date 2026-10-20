import base64
import io
import uuid
from datetime import timedelta

from django.contrib import messages
from django.core.mail import send_mail
from django.db import transaction
from django.db.models import F, Sum
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import UsuarioForm, PerfilForm, ReservaForm, AlertaPreventivaForm, InventarioForm, DevolucionForm, OperadorForm
from .models import Usuario, Perfil, Dotacion, Bodega, Inventario, Reserva, Entrega, AlertaPreventiva, Devolucion, Operador


def dashboard(request):
    hoy = timezone.localdate()
    proximos_30 = hoy + timedelta(days=30)
    usuarios = Usuario.objects.filter(activo=True)
    reservas_pendientes = Reserva.objects.filter(estado='pendiente').count()
    reservas_recientes = Reserva.objects.select_related('usuario', 'dotacion')[:5]
    alerta_dotacion = Dotacion.objects.first()
    stock_bajo = [item for item in Dotacion.objects.all() if item.stock_total <= item.punto_reorden]
    alertas = AlertaPreventiva.objects.select_related('usuario', 'dotacion')[:6]
    entregas = Entrega.objects.select_related('reserva__usuario', 'reserva__dotacion')[:6]
    perfiles_sin_fecha = Perfil.objects.filter(proxima_entrega__isnull=False, proxima_entrega__lte=proximos_30).select_related('usuario')
    return render(request, 'gestion_dotaciones/dashboard.html', {
        'usuarios_count': usuarios.count(),
        'operadores_count': Operador.objects.filter(activo=True).count(),
        'reservas_pendientes': reservas_pendientes,
        'reservas': reservas_recientes,
        'alerta_dotacion': alerta_dotacion,
        'stock_bajo_count': len(stock_bajo),
        'actas_count': Entrega.objects.count(),
        'alertas': alertas,
        'entregas': entregas,
        'stock_bajo': stock_bajo[:5],
        'entregas_proximas': perfiles_sin_fecha[:5],
    })



def listar_operadores(request):
    operadores = Operador.objects.all()
    return render(request, 'gestion_dotaciones/listar_operadores.html', {'operadores': operadores})


def crear_operador(request):
    form = OperadorForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Operador creado correctamente.')
        return redirect('listar_operadores')
    return render(request, 'gestion_dotaciones/operador_form.html', {
        'form': form,
        'title': 'Nuevo operador',
        'subtitle': 'Registra el personal autorizado para gestionar DotApp.'
    })


def editar_operador(request, operador_id):
    operador = get_object_or_404(Operador, pk=operador_id)
    form = OperadorForm(request.POST or None, instance=operador)
    if form.is_valid():
        form.save()
        messages.success(request, 'Operador actualizado correctamente.')
        return redirect('listar_operadores')
    return render(request, 'gestion_dotaciones/operador_form.html', {
        'form': form,
        'title': 'Editar operador',
        'subtitle': f'Actualiza la información de {operador.nombre}.'
    })


def cambiar_estado_operador(request, operador_id):
    if request.method != 'POST':
        return redirect('listar_operadores')
    operador = get_object_or_404(Operador, pk=operador_id)
    operador.activo = not operador.activo
    operador.save(update_fields=['activo'])
    estado = 'activado' if operador.activo else 'desactivado'
    messages.success(request, f'Operador {estado} correctamente.')
    return redirect('listar_operadores')


def listar_usuarios(request):
    usuarios = Usuario.objects.all().select_related('perfil')
    return render(request, 'gestion_dotaciones/listar_usuarios.html', {'usuarios': usuarios})


def crear_usuario(request):
    form = UsuarioForm(request.POST or None)
    if form.is_valid():
        usuario = form.save()
        Perfil.objects.create(usuario=usuario)
        messages.success(request, 'Colaborador creado correctamente.')
        return redirect('listar_colaboradores')
    return render(request, 'gestion_dotaciones/form.html', {'form': form, 'title': 'Nuevo colaborador', 'subtitle': 'Registra datos básicos y deja lista su ficha de dotación.'})


def editar_perfil(request, usuario_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    perfil, _ = Perfil.objects.get_or_create(usuario=usuario)
    form = PerfilForm(request.POST or None, instance=perfil)
    if form.is_valid():
        form.save()
        messages.success(request, 'Perfil actualizado correctamente.')
        return redirect('listar_colaboradores')
    return render(request, 'gestion_dotaciones/perfil.html', {'usuario': usuario, 'perfil': perfil, 'form': form})


def reservar_dotacion(request, usuario_id, dotacion_id=None):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    initial = {'dotacion': dotacion_id} if dotacion_id else None
    form = ReservaForm(request.POST or None, initial=initial, usuario=usuario)
    if form.is_valid():
        reserva = form.save(commit=False)
        reserva.usuario = usuario
        reserva.save()
        send_mail(
            subject=f'DotApp - Reserva registrada #{reserva.id}',
            message=f'Se registró la reserva de {reserva.dotacion} para {usuario.nombre}.',
            from_email='dotapp@localhost',
            recipient_list=[usuario.email],
            fail_silently=True,
        )
        messages.success(request, 'Reserva registrada y notificación preparada.')
        return redirect('listar_reservas')
    return render(request, 'gestion_dotaciones/reservar_dotacion.html', {'usuario': usuario, 'form': form})


def listar_reservas(request):
    estado = request.GET.get('estado', '')
    reservas = Reserva.objects.select_related('usuario', 'dotacion').all()
    if estado:
        reservas = reservas.filter(estado=estado)
    return render(request, 'gestion_dotaciones/listar_reservas.html', {'reservas': reservas, 'estado': estado})


def confirmar_reserva(request, reserva_id):
    reserva = get_object_or_404(Reserva, pk=reserva_id)
    reserva.estado = 'confirmada'
    reserva.fecha_confirmacion = timezone.now()
    reserva.save(update_fields=['estado', 'fecha_confirmacion'])
    messages.success(request, 'Reserva confirmada.')
    return redirect('listar_reservas')


def firmar_entrega(request, reserva_id):
    reserva = get_object_or_404(Reserva.objects.select_related('usuario', 'dotacion'), pk=reserva_id)
    if reserva.estado not in {'confirmada', 'pendiente'}:
        messages.warning(request, 'Esta reserva no está disponible para entrega.')
        return redirect('listar_reservas')

    inventarios = Inventario.objects.filter(dotacion=reserva.dotacion).select_related('bodega').order_by('-cantidad')
    if request.method == 'POST':
        firma_data = request.POST.get('firma_data', '')
        if not firma_data.startswith('data:image/'):
            messages.error(request, 'Debes registrar la firma antes de confirmar la entrega.')
            return render(request, 'gestion_dotaciones/firmar_entrega.html', {'reserva': reserva, 'inventarios': inventarios})
        latitud = request.POST.get('latitud') or None
        longitud = request.POST.get('longitud') or None
        identificador = request.POST.get('identificador_receptor') or reserva.usuario.email
        inventario_id = request.POST.get('inventario_id')
        inventario = get_object_or_404(Inventario, pk=inventario_id, dotacion=reserva.dotacion)
        with transaction.atomic():
            inventario = Inventario.objects.select_for_update().get(pk=inventario.pk)
            if inventario.cantidad < 1:
                messages.error(request, 'No hay existencias en la bodega seleccionada.')
                return render(request, 'gestion_dotaciones/firmar_entrega.html', {'reserva': reserva, 'inventarios': inventarios})
            inventario.cantidad = F('cantidad') - 1
            inventario.save(update_fields=['cantidad'])
            entrega = Entrega.objects.create(
                reserva=reserva,
                firma_data=firma_data,
                latitud=latitud,
                longitud=longitud,
                identificador_receptor=identificador,
                acta_numero=f'ACT-{timezone.now():%Y%m%d}-{uuid.uuid4().hex[:6].upper()}',
                ip_receptor=request.META.get('REMOTE_ADDR'),
            )
            reserva.estado = 'entregada'
            reserva.fecha_confirmacion = timezone.now()
            reserva.save(update_fields=['estado', 'fecha_confirmacion'])
        messages.success(request, f'Entrega registrada. Acta {entrega.acta_numero} generada.')
        return redirect('acta_pdf', entrega_id=entrega.id)
    return render(request, 'gestion_dotaciones/firmar_entrega.html', {'reserva': reserva, 'inventarios': inventarios})


def acta_pdf(request, entrega_id):
    entrega = get_object_or_404(Entrega.objects.select_related('reserva__usuario', 'reserva__dotacion'), pk=entrega_id)
    try:
        from reportlab.lib.pagesizes import letter
        from reportlab.lib.utils import ImageReader
        from reportlab.pdfgen import canvas
    except ImportError:
        return HttpResponse('Instala reportlab para generar actas PDF: pip install reportlab', status=500)

    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    pdf.setTitle(f'Acta {entrega.acta_numero}')
    pdf.setFont('Helvetica-Bold', 18)
    pdf.drawString(55, height - 65, 'DotApp - Acta de Entrega de Dotación')
    pdf.setFont('Helvetica', 10)
    pdf.drawString(55, height - 85, f'Acta: {entrega.acta_numero}')
    pdf.line(55, height - 96, width - 55, height - 96)
    y = height - 130
    rows = [
        ('Receptor', entrega.reserva.usuario.nombre),
        ('Correo', entrega.reserva.usuario.email),
        ('Cargo', entrega.reserva.usuario.cargo),
        ('Dotación', str(entrega.reserva.dotacion)),
        ('Fecha y hora', timezone.localtime(entrega.fecha_entrega).strftime('%Y-%m-%d %H:%M:%S')),
        ('ID receptor', entrega.identificador_receptor or 'N/A'),
        ('Geolocalización', f'{entrega.latitud}, {entrega.longitud}' if entrega.latitud and entrega.longitud else 'No disponible'),
    ]
    for label, value in rows:
        pdf.setFont('Helvetica-Bold', 10)
        pdf.drawString(55, y, f'{label}:')
        pdf.setFont('Helvetica', 10)
        pdf.drawString(145, y, value[:90])
        y -= 22
    pdf.setFont('Helvetica-Bold', 11)
    pdf.drawString(55, y - 5, 'Firma digitalizada del receptor')
    try:
        raw = base64.b64decode(entrega.firma_data.split(',', 1)[1])
        pdf.drawImage(ImageReader(io.BytesIO(raw)), 55, y - 145, width=220, height=100, preserveAspectRatio=True, mask='auto')
    except Exception:
        pdf.setFont('Helvetica-Oblique', 9)
        pdf.drawString(55, y - 35, 'Firma registrada, pero no pudo representarse en este PDF.')
    pdf.setFont('Helvetica-Oblique', 8)
    pdf.drawString(55, 45, 'Documento generado por DotApp para trazabilidad de la entrega.')
    pdf.save()
    response = HttpResponse(buffer.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{entrega.acta_numero}.pdf"'
    return response


def inventario(request):
    inventarios = Inventario.objects.select_related('dotacion', 'bodega').order_by('dotacion__nombre', 'bodega__nombre')
    form = InventarioForm(request.POST or None)
    if form.is_valid():
        bodega = form.cleaned_data['bodega']
        dotacion = form.cleaned_data['dotacion']
        cantidad = form.cleaned_data['cantidad']
        item, _ = Inventario.objects.get_or_create(bodega=bodega, dotacion=dotacion, defaults={'cantidad': 0})
        item.cantidad = F('cantidad') + cantidad
        item.save(update_fields=['cantidad'])
        messages.success(request, f'Se agregaron {cantidad} unidades a {bodega}.')
        return redirect('inventario')
    dotaciones = Dotacion.objects.all()
    return render(request, 'gestion_dotaciones/inventario.html', {'inventarios': inventarios, 'form': form, 'dotaciones': dotaciones})


def emitir_alerta_preventiva(request, usuario_id, dotacion_id):
    usuario = get_object_or_404(Usuario, pk=usuario_id)
    dotacion = get_object_or_404(Dotacion, pk=dotacion_id)
    initial_message = f'Recuerda revisar tu entrega programada de {dotacion}.'
    form = AlertaPreventivaForm(request.POST or None, initial={'mensaje': initial_message, 'fecha_programada': timezone.localdate()})
    if form.is_valid():
        alerta = form.save(commit=False)
        alerta.usuario = usuario
        alerta.dotacion = dotacion
        alerta.save()
        send_mail(
            subject='DotApp - Alerta preventiva de dotación',
            message=alerta.mensaje,
            from_email='dotapp@localhost',
            recipient_list=[usuario.email],
            fail_silently=True,
        )
        alerta.enviada = True
        alerta.save(update_fields=['enviada'])
        messages.success(request, 'Alerta registrada y enviada al correo de prueba (consola).')
        return redirect('dashboard')
    return render(request, 'gestion_dotaciones/emitir_alerta_preventiva.html', {'usuario': usuario, 'dotacion': dotacion, 'form': form})


def devoluciones(request):
    devoluciones_qs = Devolucion.objects.select_related('usuario', 'dotacion', 'bodega')
    labels = dict(Devolucion.CAUSALES)
    causal_counts = [{'value': value, 'label': labels[value], 'count': devoluciones_qs.filter(causal=value).count()} for value, _ in Devolucion.CAUSALES]
    form = DevolucionForm(request.POST or None)
    if form.is_valid():
        with transaction.atomic():
            devolucion = form.save()
            item, _ = Inventario.objects.get_or_create(bodega=devolucion.bodega, dotacion=devolucion.dotacion, defaults={'cantidad': 0})
            item.cantidad = F('cantidad') + 1
            item.save(update_fields=['cantidad'])
        messages.success(request, 'Devolución registrada y stock actualizado.')
        return redirect('devoluciones')
    return render(request, 'gestion_dotaciones/devoluciones.html', {'devoluciones': devoluciones_qs, 'form': form, 'causal_counts': causal_counts})
