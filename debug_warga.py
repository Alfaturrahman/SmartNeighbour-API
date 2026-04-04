from core.models import User, Resident, RT, RW, SecuritySchedule
from datetime import date

# Check warga user
warga = User.objects.filter(email='warga@test.com').first()
print('=== WARGA USER ===')
print(f'User: {warga}')
print(f'Email: {warga.email if warga else None}')
print(f'Role: {warga.role if warga else None}')
print()

# Check resident profile
print('=== RESIDENT PROFILE ===')
if warga:
    try:
        resident = warga.resident_profile
        print(f'Resident: {resident}')
        print(f'Resident RT: {resident.rt}')
        print(f'Resident RT ID: {resident.rt.id if resident.rt else None}')
        print(f'Resident RW: {resident.rt.rw if resident.rt else None}')
        print(f'Resident RW ID: {resident.rt.rw.id if resident.rt else None}')
    except Exception as e:
        print(f'Error getting resident: {e}')
        print(f'Error type: {type(e).__name__}')
print()

# Check security schedules
print('=== SECURITY SCHEDULES ===')
if warga:
    try:
        resident = warga.resident_profile
        rw = resident.rt.rw
        print(f'Looking for schedules in RW: {rw.name} (ID: {rw.id})')
        
        all_schedules = SecuritySchedule.objects.filter(rw=rw)
        print(f'Total schedules for this RW: {all_schedules.count()}')
        
        active_schedules = all_schedules.filter(status='aktif')
        print(f'Active schedules: {active_schedules.count()}')
        
        # Check today's schedules
        today = date.today()
        print(f'Today: {today}')
        
        today_schedules = active_schedules.filter(
            start_date__lte=today,
            end_date__gte=today
        )
        print(f'Schedules active today: {today_schedules.count()}')
        
        print('\nAll active schedules:')
        for s in active_schedules:
            print(f'  - ID: {s.id} | {s.name} | {s.shift} | {s.start_date} to {s.end_date} | Personnel: {s.personnel}')
            
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()
else:
    print('Warga user not found!')

# Check all RWs
print('\n=== ALL RWs ===')
all_rws = RW.objects.all()
for rw in all_rws:
    print(f'RW: {rw.name} (ID: {rw.id})')
    schedule_count = SecuritySchedule.objects.filter(rw=rw).count()
    print(f'  Schedules: {schedule_count}')
