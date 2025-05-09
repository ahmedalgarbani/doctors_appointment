from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils import timezone
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.urls import reverse
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
        advertisements = Advertisement.objects.filter(hospital=hospital).order_by('-created_at')

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
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        # طباعة معلومات التصحيح
        print(f"Search query: {search_query}")
        print(f"Status filter: {status_filter}")
        print(f"Total advertisements: {advertisements.count()}")
        print(f"Current page: {page_obj.number}")
        print(f"Total pages: {paginator.num_pages}")

        # إذا كان الطلب من AJAX، أرجع البيانات بتنسيق JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            ads_data = []
            for ad in page_obj:
                # تحديد حالة الإعلان بالعربية
                status_display = {
                    'active': 'نشط',
                    'inactive': 'غير نشط',
                    'scheduled': 'مجدول',
                    'expired': 'منتهي'
                }.get(ad.status, ad.status)

                # تحديد لون الحالة
                status_color = {
                    'active': 'success',
                    'inactive': 'secondary',
                    'scheduled': 'info',
                    'expired': 'danger'
                }.get(ad.status, 'secondary')

                ad_data = {
                    'id': ad.id,
                    'title': ad.title,
                    'image_url': ad.image.url if ad.image else None,
                    'start_date': ad.start_date.strftime('%Y-%m-%d'),
                    'end_date': ad.end_date.strftime('%Y-%m-%d') if ad.end_date else 'غير محدد',
                    'status': ad.status,
                    'status_display': status_display,
                    'status_color': status_color,
                    'detail_url': reverse('advertisements:advertisement_detail', args=[ad.id]),
                }
                ads_data.append(ad_data)

            # إعداد بيانات التنقل بين الصفحات
            pagination_data = {
                'has_previous': page_obj.has_previous(),
                'has_next': page_obj.has_next(),
                'number': page_obj.number,
                'num_pages': paginator.num_pages,
                'page_range': list(paginator.page_range),
                'previous_page_number': page_obj.previous_page_number() if page_obj.has_previous() else None,
                'next_page_number': page_obj.next_page_number() if page_obj.has_next() else None,
            }

            return JsonResponse({
                'success': True,
                'advertisements': ads_data,
                'pagination': pagination_data,
                'total_count': advertisements.count(),
                'search_query': search_query,
                'status_filter': status_filter,
            })

        context = {
            'advertisements': page_obj,
            'status_filter': status_filter,
            'search_query': search_query,
            'section': 'advertisements_list',  # تعيين القسم النشط
        }
    except Exception as e:
        # En caso de error, mostrar un mensaje y una lista vacía
        error_message = f'خطأ في تحميل الإعلانات: {str(e)}'
        messages.error(request, error_message)
        print(f"Error loading advertisements: {str(e)}")

        # إذا كان الطلب من AJAX، أرجع رسالة خطأ بتنسيق JSON
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': False,
                'error': error_message
            }, status=500)

        context = {
            'advertisements': [],
            'status_filter': None,
            'search_query': '',
            'section': 'advertisements_list',  # تعيين القسم النشط
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
            # حفظ الإعلان
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
                    }
                })

            messages.success(request, 'تم تحديث الإعلان بنجاح!')
            return redirect('advertisements:advertisement_list')
        elif request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'error': 'Form validation failed', 'errors': form.errors}, status=400)
    else:
        form = AdvertisementForm(instance=advertisement)

    # تجهيز الصور الإضافية للعرض في النموذج
    additional_images = []
    if advertisement.image2:
        additional_images.append({'image': advertisement.image2, 'id': 'image2'})
    if advertisement.image3:
        additional_images.append({'image': advertisement.image3, 'id': 'image3'})
    if advertisement.image4:
        additional_images.append({'image': advertisement.image4, 'id': 'image4'})

    context = {
        'form': form,
        'advertisement': advertisement,
        'additional_images': additional_images,
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
        messages.error(request, 'لم يتم العثور على الإعلان المطلوب.')
        return redirect('advertisements:advertisement_list')

    # Verificar que el anuncio tenga un ID válido
    if not advertisement.id:
        messages.error(request, 'معرف الإعلان غير صالح.')
        return redirect('advertisements:advertisement_list')

    # تم إزالة زيادة عداد المشاهدات

    # تجهيز الصور الإضافية
    additional_images = []

    # طباعة معلومات التصحيح
    print(f"Advertisement ID: {advertisement.id}")
    print(f"Advertisement title: {advertisement.title}")
    print(f"Has image2: {bool(advertisement.image2)}")
    print(f"Has image3: {bool(advertisement.image3)}")
    print(f"Has image4: {bool(advertisement.image4)}")

    # إضافة الصور الإضافية إذا كانت موجودة
    if advertisement.image2:
        additional_images.append({'image': advertisement.image2, 'order': 0})
        print(f"Added image2 to additional_images")
    if advertisement.image3:
        additional_images.append({'image': advertisement.image3, 'order': 1})
        print(f"Added image3 to additional_images")
    if advertisement.image4:
        additional_images.append({'image': advertisement.image4, 'order': 2})
        print(f"Added image4 to additional_images")

    print(f"Total additional images: {len(additional_images)}")

    context = {
        'advertisement': advertisement,
        'additional_images': additional_images,
    }

    # استخدام القالب الجديد بدون السايد بار
    return render(request, 'frontend/dashboard/hospitals/sections/advertisements/advertisement_detail_fullwidth.html', context)

@login_required(login_url='/user/login')
def load_advertisement_form(request):
    """View to load the advertisement form via AJAX"""
    user = request.user
    # التحقق من وجود المستشفى فقط
    get_object_or_404(Hospital, user=user)

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

    # تجهيز الصور الإضافية للعرض في النموذج
    additional_images = []
    if advertisement.image2:
        additional_images.append({'image': advertisement.image2, 'id': 'image2'})
    if advertisement.image3:
        additional_images.append({'image': advertisement.image3, 'id': 'image3'})
    if advertisement.image4:
        additional_images.append({'image': advertisement.image4, 'id': 'image4'})

    context = {
        'form': form,
        'advertisement': advertisement,
        'additional_images': additional_images,
        'is_edit': True,
    }

    # Render the form template
    html = render_to_string('frontend/dashboard/hospitals/sections/advertisements/advertisement_form_content.html', context, request=request)

    # تجهيز روابط الصور الإضافية
    additional_image_urls = []
    if advertisement.image2:
        additional_image_urls.append({
            'id': 'image2',
            'url': advertisement.image2.url
        })
    if advertisement.image3:
        additional_image_urls.append({
            'id': 'image3',
            'url': advertisement.image3.url
        })
    if advertisement.image4:
        additional_image_urls.append({
            'id': 'image4',
            'url': advertisement.image4.url
        })

    return JsonResponse({
        'html': html,
        'advertisement_id': advertisement.id,
        'title': advertisement.title,
        'image_url': advertisement.image.url if advertisement.image else None,
        'additional_images': additional_image_urls
    })

@login_required(login_url='/user/login')
def delete_additional_image(request, image_id):
    """View to delete an additional image"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Only POST method is allowed'}, status=405)

    user = request.user
    hospital = get_object_or_404(Hospital, user=user)

    try:
        # التحقق من صحة معرف الصورة
        if image_id not in ['image2', 'image3', 'image4']:
            return JsonResponse({'error': 'Invalid image ID'}, status=400)

        # الحصول على معرف الإعلان من البيانات المرسلة
        ad_id = request.POST.get('advertisement_id')
        if not ad_id:
            return JsonResponse({'error': 'Advertisement ID is required'}, status=400)

        # البحث عن الإعلان
        advertisement = get_object_or_404(Advertisement, id=ad_id, hospital=hospital)

        # حذف الصورة المحددة
        if image_id == 'image2':
            advertisement.image2 = None
        elif image_id == 'image3':
            advertisement.image3 = None
        elif image_id == 'image4':
            advertisement.image4 = None

        # حفظ التغييرات
        advertisement.save(update_fields=[image_id])

        return JsonResponse({
            'success': True,
            'message': 'تم حذف الصورة بنجاح',
            'advertisement_id': ad_id
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


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
