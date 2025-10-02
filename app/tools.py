from __future__ import annotations

import json
from typing import Any, Dict, List, Optional

from .memory import store


# Chat Completions-compatible tool schemas
TOOLS: List[Dict[str, Any]] = [
    {
        "type": "function",
        "function": {
            "name": "list_doctors",
            "description": "List doctors filtered by optional specialty and location.",
            "parameters": {
                "type": "object",
                "properties": {
                    "specialty": {"type": "string", "description": "Desired specialty, e.g. cardiology"},
                    "location": {"type": "string", "description": "Preferred location"},
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_availability",
            "description": "Get upcoming availability slots for a doctor (ISO-8601 UTC).",
            "parameters": {
                "type": "object",
                "properties": {
                    "doctor_id": {"type": "string"},
                    "days": {"type": "integer", "minimum": 1, "maximum": 30, "default": 7},
                },
                "required": ["doctor_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "book_appointment",
            "description": "Book an appointment for a patient with a doctor.",
            "parameters": {
                "type": "object",
                "properties": {
                    "patient_name": {"type": "string"},
                    "doctor_id": {"type": "string"},
                    "datetime": {"type": "string", "description": "ISO-8601 UTC timestamp"},
                    "reason": {"type": "string"},
                },
                "required": ["patient_name", "doctor_id", "datetime", "reason"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "reschedule_appointment",
            "description": "Reschedule an existing appointment to a new time.",
            "parameters": {
                "type": "object",
                "properties": {
                    "appointment_id": {"type": "string"},
                    "new_datetime": {"type": "string", "description": "ISO-8601 UTC timestamp"},
                },
                "required": ["appointment_id", "new_datetime"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "cancel_appointment",
            "description": "Cancel an appointment by ID.",
            "parameters": {
                "type": "object",
                "properties": {"appointment_id": {"type": "string"}},
                "required": ["appointment_id"],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "get_appointment_details",
            "description": "Get details for an appointment.",
            "parameters": {
                "type": "object",
                "properties": {"appointment_id": {"type": "string"}},
                "required": ["appointment_id"],
                "additionalProperties": False,
            },
        },
    },
]


# Python implementations backing the tools

def list_doctors(specialty: Optional[str] = None, location: Optional[str] = None) -> Dict[str, Any]:
    return {"doctors": store.list_doctors(specialty=specialty, location=location)}


def get_availability(doctor_id: str, days: int = 7) -> Dict[str, Any]:
    return {"slots": store.get_availability(doctor_id=doctor_id, days=days)}


def book_appointment(patient_name: str, doctor_id: str, datetime: str, reason: str) -> Dict[str, Any]:
    appt = store.book_appointment(patient_name=patient_name, doctor_id=doctor_id, dt_iso=datetime, reason=reason)
    return {"appointment": appt}


def reschedule_appointment(appointment_id: str, new_datetime: str) -> Dict[str, Any]:
    appt = store.reschedule_appointment(appointment_id=appointment_id, new_dt_iso=new_datetime)
    return {"appointment": appt}


def cancel_appointment(appointment_id: str) -> Dict[str, Any]:
    appt = store.cancel_appointment(appointment_id=appointment_id)
    return {"appointment": appt}


def get_appointment_details(appointment_id: str) -> Dict[str, Any]:
    appt = store.get_appointment(appointment_id)
    if not appt:
        raise ValueError("Unknown appointment_id")
    return {"appointment": appt}


FUNCTION_MAP = {
    "list_doctors": list_doctors,
    "get_availability": get_availability,
    "book_appointment": book_appointment,
    "reschedule_appointment": reschedule_appointment,
    "cancel_appointment": cancel_appointment,
    "get_appointment_details": get_appointment_details,
}