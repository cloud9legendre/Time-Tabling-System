from ics import Calendar, Event
from datetime import datetime
import io
from reportlab.pdfgen import canvas

def generate_ics(bookings, email):
    c = Calendar()
    for b in bookings:
        e = Event()
        e.name = f"{b.module_code} - {b.purpose}"
        e.begin = datetime.combine(b.booking_date, b.start_time)
        e.end = datetime.combine(b.booking_date, b.end_time)
        c.events.add(e)
    return str(c)

def generate_pdf(bookings, name):
    buffer = io.BytesIO()
    p = canvas.Canvas(buffer)
    p.drawString(100, 800, f"Timetable for {name}")
    y = 750
    for b in bookings:
        p.drawString(100, y, f"{b.booking_date}: {b.module_code} in {b.lab.name}")
        y -= 20
    p.showPage()
    p.save()
    buffer.seek(0)
    return buffer
