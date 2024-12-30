from collections import defaultdict

def group_shifts_by_period(shifts):
    grouped_slots = defaultdict(list)
    
    for slot in shifts:
        if slot.start_time.hour < 12:
            grouped_slots['morning'].append(slot)
        elif 12 <= slot.start_time.hour < 17:
            grouped_slots['afternoon'].append(slot)
        else:
            grouped_slots['evening'].append(slot)
    
    return grouped_slots