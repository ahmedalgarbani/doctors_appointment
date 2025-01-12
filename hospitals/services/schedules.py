from doctors.models import DoctorSchedules

def get_doctor_schedules(hospital):
    schedules = DoctorSchedules.objects.filter(hospital=hospital).select_related('doctor')
    doctor_schedules = {}
    for schedule in schedules:
        if schedule.doctor_id not in doctor_schedules:
            doctor_schedules[schedule.doctor_id] = {}
        shifts = []
        for shift in schedule.shifts.all():
            shifts.append({
                'id': shift.id,
                'start_time': shift.start_time.strftime('%I:%M %p'),
                'end_time': shift.end_time.strftime('%I:%M %p'),
                'available_slots': shift.available_slots,
                'booked_slots': shift.booked_slots if hasattr(shift, 'booked_slots') else 0
            })
        doctor_schedules[schedule.doctor_id][schedule.day] = shifts
    return doctor_schedules
