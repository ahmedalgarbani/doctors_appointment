from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Review
from .forms import ReviewForm
from hospitals.models import Hospital
from patients.models import Patients
from bookings.models import Booking

def review_list(request):
    reviews = Review.objects.all()
    return render(request, 'reviews/review_list.html', {'reviews': reviews})

def review_detail(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    return render(request, 'reviews/review_detail.html', {'review': review})

def review_create(request):
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user_id = request.user  
            review.save()
            return redirect('review_list')
    else:
        form = ReviewForm()
    return render(request, 'reviews/review_form.html', {'form': form})

def review_update(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        form = ReviewForm(request.POST, instance=review)
        if form.is_valid():
            form.save()
            return redirect('review_list')
    else:
        form = ReviewForm(instance=review)
    return render(request, 'reviews/review_form.html', {'form': form})

def review_delete(request, review_id):
    review = get_object_or_404(Review, id=review_id)
    if request.method == 'POST':
        review.delete()
        return redirect('review_list')
    return render(request, 'reviews/review_confirm_delete.html', {'review': review})


@login_required(login_url='/user/login')
def add_hospital_review(request, hospital_id):
    """
    دالة لإضافة تقييم جديد للمستشفى
    """
    # التحقق من أن المستخدم مريض
    if request.user.user_type != 'patient':
        messages.error(request, "يجب أن تكون مريضًا لإضافة تقييم")
        return redirect('hospitals:hospital_details', hospital_id=hospital_id)
    
    # الحصول على المستشفى
    hospital = get_object_or_404(Hospital, id=hospital_id)
    
    # الحصول على سجل المريض
    try:
        patient = Patients.objects.get(user=request.user)
    except Patients.DoesNotExist:
        messages.error(request, "لم يتم العثور على سجل المريض")
        return redirect('hospitals:hospital_details', hospital_id=hospital_id)
    
    # التحقق من أن المريض قد قام بحجز في هذا المستشفى من قبل
    has_booking = Booking.objects.filter(
        patient=patient,
        hospital=hospital
    ).exists()
    
    if not has_booking:
        messages.error(request, "يجب أن يكون لديك حجز سابق في هذا المستشفى لتتمكن من إضافة تقييم")
        return redirect('hospitals:hospital_details', hospital_id=hospital_id)
    
    # التحقق من أن المريض لم يقم بتقييم المستشفى من قبل
    existing_review = Review.objects.filter(
        hospital=hospital,
        doctor__isnull=True,
        user=patient
    ).first()
    
    if existing_review:
        messages.error(request, "لقد قمت بتقييم هذا المستشفى من قبل")
        return redirect('hospitals:hospital_details', hospital_id=hospital_id)
    
    if request.method == 'POST':
        # الحصول على بيانات التقييم
        rating = request.POST.get('rating')
        review_text = request.POST.get('review')
        
        # التحقق من صحة البيانات
        if not rating or not review_text:
            messages.error(request, "يرجى ملء جميع الحقول المطلوبة")
            return redirect('hospitals:hospital_details', hospital_id=hospital_id)
        
        try:
            # إنشاء تقييم جديد
            new_review = Review(
                hospital=hospital,
                user=patient,
                rating=int(rating),
                review=review_text,
                status=True,  # نشط بشكل افتراضي
                has_reservation=True  # تم التحقق من وجود حجز مسبقًا
            )
            new_review.save()
            
            messages.success(request, "تم إضافة تقييمك بنجاح")
        except Exception as e:
            messages.error(request, f"حدث خطأ أثناء حفظ التقييم: {str(e)}")
    
    return redirect('hospitals:hospital_details', hospital_id=hospital_id)
