from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count
from django.utils import timezone
from bookings.models import Booking
from payments.models import Payment
from datetime import datetime, timedelta
from django.db.models.functions import TruncDate


@login_required
def booking_reports_data(request):
    """
    Vista para obtener datos de reportes de reservas según filtros de fecha y estado.
    Retorna datos JSON con estadísticas y lista de reservas para la página de informes.
    """
    if request.method == "GET":
        date_from = request.GET.get("date_from")
        date_to = request.GET.get("date_to")
        status = request.GET.get("status")
        
        # Validar fechas
        try:
            date_from = datetime.strptime(date_from, "%Y-%m-%d").date() if date_from else None
            date_to = datetime.strptime(date_to, "%Y-%m-%d").date() if date_to else None
        except ValueError:
            return JsonResponse({
                'error': 'صيغة التاريخ غير صحيحة. استخدم التنسيق YYYY-MM-DD'
            }, status=400)
        
        # Construir consulta
        bookings_query = Booking.objects.all()
        
        # Filtrar por hospital si el usuario es un administrador de hospital
        if hasattr(request.user, 'hospital'):
            bookings_query = bookings_query.filter(hospital=request.user.hospital)
        
        # Aplicar filtros de fecha
        if date_from:
            bookings_query = bookings_query.filter(booking_date__gte=date_from)
        if date_to:
            bookings_query = bookings_query.filter(booking_date__lte=date_to)
        
        # Aplicar filtro de estado
        if status:
            bookings_query = bookings_query.filter(status=status)
        
        # Calcular estadísticas
        total_bookings = bookings_query.count()
        
        # Calcular ingresos totales (si hay relación con pagos)
        total_revenue = 0
        try:
            # Intentar obtener la suma de pagos relacionados con las reservas
            payment_data = Payment.objects.filter(booking__in=bookings_query, payment_status=1)
            if payment_data.exists():
                payment_sum = payment_data.aggregate(Sum('payment_totalamount'))
                total_revenue = payment_sum['payment_totalamount__sum'] or 0
            else:
                # Si no hay pagos, usar el campo 'amount' de las reservas
                amount_sum = bookings_query.aggregate(Sum('amount'))
                total_revenue = amount_sum['amount__sum'] or 0
        except Exception:
            # Fallback: usar el campo amount de las reservas si hay error
            try:
                amount_sum = bookings_query.aggregate(Sum('amount'))
                total_revenue = amount_sum['amount__sum'] or 0
            except Exception:
                total_revenue = 0
        
        # Distribución de estados
        status_distribution = {
            'pending': bookings_query.filter(status='pending').count(),
            'confirmed': bookings_query.filter(status='confirmed').count(),
            'completed': bookings_query.filter(status='completed').count(),
            'cancelled': bookings_query.filter(status='cancelled').count()
        }
        
        # Distribución diaria
        daily_data = {}
        date_range = None
        
        if date_from and date_to:
            date_range = (date_to - date_from).days + 1
            
            # Si el rango de fechas es razonable, obtener distribución diaria
            if date_range <= 90:  # Limitar a 90 días para evitar consultas pesadas
                daily_bookings = bookings_query.annotate(
                    date=TruncDate('booking_date')
                ).values('date').annotate(count=Count('id')).order_by('date')
                
                # Crear diccionario de fechas
                for i in range(date_range):
                    current_date = date_from + timedelta(days=i)
                    daily_data[current_date.strftime('%Y-%m-%d')] = 0
                
                # Rellenar con datos reales
                for item in daily_bookings:
                    if item['date']:
                        date_str = item['date'].strftime('%Y-%m-%d')
                        daily_data[date_str] = item['count']
            else:
                # Para rangos muy grandes, devolver mensaje informativo
                daily_data = {'message': 'النطاق الزمني كبير جدًا لعرض البيانات اليومية'}
        
        # Preparar datos para el gráfico diario
        dates = list(daily_data.keys()) if isinstance(daily_data, dict) and 'message' not in daily_data else []
        counts = list(daily_data.values()) if isinstance(daily_data, dict) and 'message' not in daily_data else []
        
        # Preparar datos de reservas para la tabla
        bookings_data = []
        for booking in bookings_query.order_by('-booking_date')[:100]:  # Limitar a 100 reservas para rendimiento
            try:
                # Intentar obtener información relacionada
                patient_name = booking.patient.user.get_full_name() if hasattr(booking.patient, 'user') else str(booking.patient)
                doctor_name = booking.doctor.user.get_full_name() if hasattr(booking.doctor, 'user') else str(booking.doctor)
                try:
                    speciality = booking.doctor.speciality.name if hasattr(booking.doctor, 'speciality') else ''
                except AttributeError:
                    speciality = ''
                
                # Obtener hora del turno
                try:
                    time_str = f"{booking.appointment_time.start_time.strftime('%I:%M %p')} - {booking.appointment_time.end_time.strftime('%I:%M %p')}"
                    time_str = time_str.replace('AM', 'ص').replace('PM', 'م')
                except AttributeError:
                    time_str = str(booking.appointment_time)
                
                # Obtener monto (de pago o reserva)
                try:
                    payment = Payment.objects.filter(booking=booking).first()
                    amount = payment.payment_totalamount if payment else booking.amount
                except Exception:
                    amount = booking.amount
                
                bookings_data.append({
                    'id': f"BOOK-{booking.id}",
                    'patient_name': patient_name,
                    'doctor_name': doctor_name,
                    'speciality': speciality,
                    'date': booking.booking_date.strftime('%Y-%m-%d'),
                    'time': time_str,
                    'status': booking.status,
                    'amount': float(amount) if amount else 0
                })
            except Exception as e:
                # Omitir registros con errores para evitar fallos en el informe
                continue
        
        # Retornar respuesta JSON con todos los datos
        return JsonResponse({
            'total_appointments': total_bookings,
            'total_revenue': float(total_revenue),
            'appointments': bookings_data,
            'daily_distribution': {
                'dates': dates,
                'counts': counts
            },
            'status_distribution': status_distribution
        })
    
    return JsonResponse({'error': 'طريقة غير مسموح بها'}, status=405)


@login_required
def booking_reports_page(request):
    """
    Vista para renderizar la página de reportes de reservas.
    """
    return render(request, 'frontend/dashboard/hospitals/sections/booking-reports.html')
