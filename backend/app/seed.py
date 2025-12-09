from sqlalchemy.orm import Session
from .database import engine, SessionLocal, Base
from .models.client import Client, SubscriptionPlan
from .models.pet import Pet
from .models.user import User, Role
from .models.appointment import Appointment
from .models.invoice import Invoice
from .models.payment import Payment
from .models.history import History
from .utils.security import hash_password
from datetime import datetime, timedelta

def create_all():
    """
    Crea las tablas (usa el Base de app.database).
    """
    Base.metadata.create_all(bind=engine)

def seed():
    """
    Inserta datos mínimos para pruebas manuales y automáticas.
    Diseñado para ejecutarse varias veces: si ya existen filas únicas
    el script intenta no duplicar (comprobaciones básicas).
    """
    db: Session = SessionLocal()

    try:
        # ---------- ROLES ----------
        existing = {r.name for r in db.query(Role).all()}
        roles_to_add = []
        if "admin" not in existing:
            roles_to_add.append(Role(name="admin"))
        if "receptionist" not in existing:
            roles_to_add.append(Role(name="receptionist"))
        if "veterinarian" not in existing:
            roles_to_add.append(Role(name="veterinarian"))
        if roles_to_add:
            db.add_all(roles_to_add)
            db.commit()

        # refresh roles map
        roles = {r.name: r for r in db.query(Role).all()}

        # ---------- USERS ----------
        # usuarios: admin y recepcionista (para pruebas)
        def ensure_user(email, password, full_name, role_name):
            u = db.query(User).filter_by(email=email).first()
            if u:
                return u
            hashed = hash_password(password)
            user = User(email=email, hashed_password=hashed, full_name=full_name, role_id=roles[role_name].id)
            db.add(user)
            db.commit()
            db.refresh(user)
            return user

        admin = ensure_user("admin@example.com", "adminpass", "Admin Clinica", "admin")
        recep = ensure_user("recep@example.com", "receppass", "Recepcion", "receptionist")
        vet = ensure_user("vet@example.com", "vetpass", "Dr. Veterinario", "veterinarian")

        # ---------- SUBSCRIPTION PLANS ----------
        existing_plans = {p.name for p in db.query(SubscriptionPlan).all()}
        plans = []
        if "free" not in existing_plans:
            plans.append(SubscriptionPlan(name="free", price=0.0, description="Plan de prueba gratuito"))
        if "standard" not in existing_plans:
            plans.append(SubscriptionPlan(name="standard", price=9.99, description="Plan estándar"))
        if plans:
            db.add_all(plans)
            db.commit()

        # map plans
        plans_map = {p.name: p for p in db.query(SubscriptionPlan).all()}

        # ---------- CLIENTS ----------
        def ensure_client(dni, name, email, phone=None, address=None, plan_name="free"):
            c = db.query(Client).filter_by(dni=dni).first()
            if c:
                return c
            client = Client(dni=dni, name=name, email=email, phone=phone, address=address,
                            subscription_id=plans_map[plan_name].id if plan_name in plans_map else None)
            db.add(client)
            db.commit()
            db.refresh(client)
            return client

        c1 = ensure_client("11111111A", "Carlos Perez", "carlos@example.com", phone="600111222", address="C/ Mayor 1", plan_name="free")
        c2 = ensure_client("22222222B", "Lucia Gomez", "lucia@example.com", phone="600333444", address="C/ Real 2", plan_name="standard")
        c3 = ensure_client("33333333C", "Miguel Ruiz", "miguel@example.com", phone="600555666", address="C/ Luna 3")

        # ---------- PETS ----------
        def ensure_pet(name, species, breed, age, owner_id):
            p = db.query(Pet).filter_by(name=name, owner_id=owner_id).first()
            if p:
                return p
            pet = Pet(name=name, species=species, breed=breed, age=age, owner_id=owner_id)
            db.add(pet)
            db.commit()
            db.refresh(pet)
            return pet

        pet1 = ensure_pet("Toby", "Perro", "Labrador", 4, c1.id)
        pet2 = ensure_pet("Misu", "Gato", "Europeo", 2, c2.id)

        # ---------- APPOINTMENTS ----------
        def ensure_appointment(date_dt, reason, veterinarian, pet_id, client_id):
            # simple uniqueness by date+pet
            ap = db.query(Appointment).filter_by(date=date_dt, pet_id=pet_id).first()
            if ap:
                return ap
            a = Appointment(date=date_dt, reason=reason, veterinarian=veterinarian, pet_id=pet_id, client_id=client_id)
            db.add(a)
            db.commit()
            db.refresh(a)
            return a

        now = datetime.utcnow()
        ap1 = ensure_appointment(now + timedelta(days=1), "Consulta general", "Dr. Veterinario", pet1.id, c1.id)
        ap2 = ensure_appointment(now + timedelta(days=2, hours=2), "Revisión vacuna", "Dr. Veterinario", pet2.id, c2.id)

        # ---------- INVOICES & PAYMENTS ----------
        def ensure_invoice(client_id, date_dt, total, paid=False):
            inv = db.query(Invoice).filter_by(client_id=client_id, date=date_dt, total=total).first()
            if inv:
                return inv
            invoice = Invoice(client_id=client_id, date=date_dt, total=total, paid=paid)
            db.add(invoice)
            db.commit()
            db.refresh(invoice)
            return invoice

        def ensure_payment(invoice_id, amount, date_dt, method="cash"):
            pay = db.query(Payment).filter_by(invoice_id=invoice_id, amount=amount, date=date_dt).first()
            if pay:
                return pay
            payment = Payment(invoice_id=invoice_id, amount=amount, date=date_dt, method=method)
            db.add(payment)
            # mark invoice paid if amounts cover total (simple approach)
            db.commit()
            db.refresh(payment)
            return payment

        inv1 = ensure_invoice(c1.id, now.date(), 120.50, paid=False)
        # example payment (partial/full)
        pay1 = ensure_payment(inv1.id, 120.50, now, method="card")
        # If you want invoice marked paid automatically:
        inv1.paid = True
        db.add(inv1)
        db.commit()

        # ---------- HISTORY (event log) ----------
        def add_history(client_id, pet_id, event, ts=None):
            h = History(client_id=client_id, pet_id=pet_id, event=event, timestamp=ts or datetime.utcnow())
            db.add(h)
            db.commit()
            return h

        add_history(c1.id, pet1.id, "Creada cita inicial")
        add_history(c2.id, pet2.id, "Vacunación registrada")

        print("Seed finished")

    except Exception as e:
        db.rollback()
        print("Seed failed:", e)
        raise
    finally:
        db.close()

if __name__ == "__main__":
    create_all()
    seed()