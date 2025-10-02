from __future__ import annotations

import threading
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional


class InMemoryStore:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self.doctors: Dict[str, Dict] = {}
        self.appointments: Dict[str, Dict] = {}
        self._seed()

    def _seed(self) -> None:
        with self._lock:
            self.doctors = {
                "d-alex": {"id": "d-alex", "name": "Dr. Alex Chen", "specialty": "cardiology", "location": "downtown"},
                "d-priya": {"id": "d-priya", "name": "Dr. Priya Singh", "specialty": "dermatology", "location": "uptown"},
                "d-luis": {"id": "d-luis", "name": "Dr. Luis Gomez", "specialty": "pediatrics", "location": "midtown"},
            }
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            # No initial appointments; availability determined dynamically
            self.appointments = {}

    def list_doctors(self, specialty: Optional[str] = None, location: Optional[str] = None) -> List[Dict]:
        with self._lock:
            result = list(self.doctors.values())
            if specialty:
                result = [d for d in result if d["specialty"].lower() == specialty.lower()]
            if location:
                result = [d for d in result if d["location"].lower() == location.lower()]
            return result

    def get_availability(self, doctor_id: str, days: int = 7) -> List[str]:
        with self._lock:
            # Generate hourly slots next N days 9am-5pm UTC, skip booked
            now = datetime.utcnow().replace(minute=0, second=0, microsecond=0)
            slots: List[str] = []
            for day in range(days):
                start = (now + timedelta(days=day)).replace(hour=9)
                for hour in range(9, 17):
                    slot = start.replace(hour=hour)
                    slot_iso = slot.isoformat() + "Z"
                    if not any(
                        appt["doctor_id"] == doctor_id and appt["datetime"] == slot_iso
                        for appt in self.appointments.values()
                    ):
                        slots.append(slot_iso)
            return slots

    def book_appointment(self, patient_name: str, doctor_id: str, dt_iso: str, reason: str) -> Dict:
        with self._lock:
            if doctor_id not in self.doctors:
                raise ValueError("Unknown doctor_id")
            if any(appt["doctor_id"] == doctor_id and appt["datetime"] == dt_iso for appt in self.appointments.values()):
                raise ValueError("Selected time is no longer available")
            appt_id = str(uuid.uuid4())
            appt = {
                "id": appt_id,
                "patient_name": patient_name,
                "doctor_id": doctor_id,
                "datetime": dt_iso,
                "reason": reason,
                "status": "booked",
            }
            self.appointments[appt_id] = appt
            return appt

    def reschedule_appointment(self, appointment_id: str, new_dt_iso: str) -> Dict:
        with self._lock:
            if appointment_id not in self.appointments:
                raise ValueError("Unknown appointment_id")
            appt = self.appointments[appointment_id]
            if any(a["doctor_id"] == appt["doctor_id"] and a["datetime"] == new_dt_iso for a in self.appointments.values() if a["id"] != appointment_id):
                raise ValueError("New time is not available")
            appt["datetime"] = new_dt_iso
            return appt

    def cancel_appointment(self, appointment_id: str) -> Dict:
        with self._lock:
            if appointment_id not in self.appointments:
                raise ValueError("Unknown appointment_id")
            appt = self.appointments[appointment_id]
            appt["status"] = "cancelled"
            return appt

    def get_appointment(self, appointment_id: str) -> Optional[Dict]:
        with self._lock:
            return self.appointments.get(appointment_id)

    def list_appointments(self) -> List[Dict]:
        with self._lock:
            return list(self.appointments.values())


store = InMemoryStore()