from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse, HttpResponse
from django.template.loader import render_to_string
from .models import Advertisement
from .forms import AdvertisementForm
from hospitals.models import Hospital

@login_required(login_url='/user/login')
def advertisement_list(request):
    """View to list all advertisements for a hospital"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        # Get all advertisements for this hospital
        advertisements = Advertisement.objects.filter(hospital=hospital)

        # Filter by status if provided
        status_filter = request.GET.get('status', None)
        if status_filter:
            advertisements = advertisements.filter(status=status_filter)

        # Search functionality
        search_query = request.GET.get('search', '')
        if search_query:
            advertisements = advertisements.filter(
                Q(title__icontains=search_query) |
                Q(description__icontains=search_query)
            )

        # Pagination
        paginator = Paginator(advertisements, 10)  # Show 10 ads per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context = {
            'advertisements': page_obj,
            'status_filter': status_filter,
            'search_query': search_query,
        }
    except Exception as e:
        # En caso de error, mostrar un mensaje y una lista vacía
        messages.error(request, f'Error al cargar los anuncios: {str(e)}')
        context = {
            'advertisements': [],
            'status_filter': None,
            'search_query': '',
        }

    return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_list.html', context)

@login_required(login_url='/user/login')
def add_advertisement(request):
    """View to add a new advertisement"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.hospital = hospital
            advertisement.created_by = user
            advertisement.save()
            messages.success(request, 'تم إضافة الإعلان بنجاح!')

            # إذا كان الطلب من AJAX، أرجع استجابة JSON
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': True, 'message': 'تم إضافة الإعلان بنجاح!'})

            # وإلا، قم بإعادة التوجيه إلى قائمة الإعلانات
            return redirect('advertisements:advertisement_list')
    else:
        form = AdvertisementForm(initial={'start_date': timezone.now().date()})

    context = {
        'form': form,
        'is_add': True,
    }

    # إذا كان الطلب من AJAX، أرجع جزء HTML فقط
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_form.html', context)

    # وإلا، قم بعرض الصفحة الكاملة
    return render(request, 'frontend/dashboard/hospitals/index.html', context)

@login_required(login_url='/user/login')
def edit_advertisement(request, advertisement_id):
    """View to edit an existing advertisement"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        advertisement = get_object_or_404(Advertisement, id=advertisement_id, hospital=hospital)
    except:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Advertisement not found'}, status=404)
        messages.error(request, 'لم يتم العثور على الإعلان المطلوب.')
        return redirect('advertisements:advertisement_list')

    # Verificar que el anuncio tenga un ID válido
    if not advertisement.id:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Invalid advertisement ID'}, status=400)
        messages.error(request, 'معرف الإعلان غير صالح.')
        return redirect('advertisements:advertisement_list')

    if request.method == 'POST':
        form = AdvertisementForm(request.POST, request.FILES, instance=advertisement)
        if form.is_valid():
            advertisement = form.save(commit=False)
            advertisement.updated_by = user
            advertisement.updated_at = timezone.now()
            advertisement.save()

            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'تم تحديث الإعلان بنجاح!',
                    'advertisement': {
                        'id': advertisement.id,
                        'title': advertisement.title,
                        'status': advertisement.status,
                        'start_date': advertisement.start_date.strftime('%Y-%m-%d'),
                        'end_date': advertisement.end_date.strftime('%Y-%m-%d') if advertisement.end_date else None,
                        'views_count': advertisement.views_count,
                        'clicks_count': advertisement.clicks_count,
                    }
                })

            messages.success(request, 'تم تحديث الإعلان بنجاح!')
            return redirect('advertisements:advertisement_list')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Form validation failed', 'errors': form.errors}, status=400)
    else:
        form = AdvertisementForm(instance=advertisement)

    context = {
        'form': form,
        'advertisement': advertisement,
        'is_add': False,
    }

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        html = render_to_string('frontend/dashboard/hospitals/sections/advertisements/advertisement_form_content.html', context, request=request)
        return JsonResponse({'html': html})

    return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_form.html', context)

@login_required(login_url='/user/login')
def delete_advertisement(request, advertisement_id):
    """View to delete an advertisement"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        advertisement = get_object_or_404(Advertisement, id=advertisement_id, hospital=hospital)
    except:
        # Si hay algún error, redirigir a la lista de anuncios
        messages.error(request, 'No se pudo encontrar el anuncio solicitado.')
        return redirect('advertisements:advertisement_list')

    # Verificar que el anuncio tenga un ID válido
    if not advertisement.id:
        messages.error(request, 'El anuncio no tiene un ID válido.')
        return redirect('advertisements:advertisement_list')

    if request.method == 'POST':
        advertisement.delete()
        messages.success(request, 'تم حذف الإعلان بنجاح!')
        return redirect('advertisements:advertisement_list')

    context = {
        'advertisement': advertisement,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_confirm_delete.html', context)

@login_required(login_url='/user/login')
def advertisement_detail(request, advertisement_id):
    """View to see details of an advertisement"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        advertisement = get_object_or_404(Advertisement, id=advertisement_id, hospital=hospital)
    except:
        # Si hay algún error, redirigir a la lista de anuncios
        messages.error(request, 'No se pudo encontrar el anuncio solicitado.')
        return redirect('advertisements:advertisement_list')

    # Verificar que el anuncio tenga un ID válido
    if not advertisement.id:
        messages.error(request, 'El anuncio no tiene un ID válido.')
        return redirect('advertisements:advertisement_list')

    context = {
        'advertisement': advertisement,
    }

    return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_detail.html', context)

@login_required(login_url='/user/login')
def load_advertisement_form(request):
    """View to load the advertisement form via AJAX"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    # Create a new form with initial values
    form = AdvertisementForm(initial={'start_date': timezone.now().date()})

    context = {
        'form': form,
        'is_add': True,
    }

    # Render the form template
    html = render_to_string('frontend/dashboard/hospitals/sections/advertisements/advertisement_form_content.html', context, request=request)

    return JsonResponse({'html': html})

@login_required(login_url='/user/login')
def load_edit_form(request, advertisement_id):
    """View to load the advertisement edit form via AJAX"""
    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        advertisement = get_object_or_404(Advertisement, id=advertisement_id, hospital=hospital)
    except:
        return JsonResponse({'error': 'Advertisement not found'}, status=404)

    # Create a form with the advertisement instance
    form = AdvertisementForm(instance=advertisement)

    context = {
        'form': form,
        'advertisement': advertisement,
        'is_edit': True,
    }

    # Render the form template
    html = render_to_string('frontend/dashboard/hospitals/sections/advertisements/advertisement_form_content.html', context, request=request)

    return JsonResponse({
        'html': html,
        'advertisement_id': advertisement.id,
        'title': advertisement.title,
        'image_url': advertisement.image.url if advertisement.image else None
    })

@login_required(login_url='/user/login')
def ajax_delete_advertisement(request, advertisement_id):
    """View to delete an advertisement via AJAX"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    # طباعة معلومات التصحيح
    print(f"Deleting advertisement {advertisement_id} for hospital {hospital.id}")

    try:
        advertisement = get_object_or_404(Advertisement, id=advertisement_id, hospital=hospital)
        print(f"Found advertisement: {advertisement.title}")
    except Exception as e:
        print(f"Error finding advertisement: {str(e)}")
        return JsonResponse({'error': f'Advertisement not found: {str(e)}'}, status=404)

    try:
        # حفظ اسم الإعلان قبل الحذف للتضمين في الاستجابة
        ad_title = advertisement.title

        # حذف الإعلان
        advertisement.delete()

        print(f"Advertisement {ad_title} deleted successfully")

        # إرجاع استجابة نجاح
        return JsonResponse({
            'success': True,
            'message': 'تم حذف الإعلان بنجاح!',
            'advertisement_id': advertisement_id,
            'title': ad_title
        })
    except Exception as e:
        print(f"Error deleting advertisement: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
