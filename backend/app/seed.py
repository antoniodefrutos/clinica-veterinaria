from sqlalchemy.orm import Session
from .database import engine, SessionLocal
from .models.client import Client, SubscriptionPlan
from .models.pet import Pet
from .models.user import User, Role
from .models.appointment import Appointment
from .models.billing import Invoice, Payment
from datetime import datetime, timedelta

def create_all():
    from .database import Base
    Base.metadata.create_all(bind=engine)

def seed():
    db: Session = SessionLocal()
    try:
        # Roles
        admin_role = Role(name="admin")
        vet_role = Role(name="veterinarian")
        db.add_all([admin_role, vet_role])
        db.commit()

        # Users
        admin = User(email="admin@clinica.local", hashed_password="not_hashed_for_dev",
                     full_name="Admin Clinica", role_id=admin_role.id)
        db.add(admin)
        db.commit()

        # Subscription plans
        basic = SubscriptionPlan(name="Básico", price=2000, duration_days=365)
        premium = SubscriptionPlan(name="Premium", price=5000, duration_days=365)
        db.add_all([basic, premium])
        db.commit()

        # Clients
        clients = [
            Client(dni="11111111A", name="Carlos Perez", email="carlos@example.com",
                   phone="600111222", address="C/ Mayor 1", subscription_id=basic.id),
            Client(dni="22222222B", name="Lucia Gomez", email="lucia@example.com",
                   phone="600333444", address="C/ Real 2", subscription_id=premium.id),
            Client(dni="33333333C", name="Miguel Ruiz", email="miguel@example.com",
                   phone="600555666", address="C/ Luna 3", subscription_id=None),
        ]
        db.add_all(clients)
        db.commit()

        # Pets
        pets = [
            Pet(name="Toby", species="Perro", breed="Labrador", age=5, weight=20, owner_id=clients[0].id),
            Pet(name="Luna", species="Gato", breed="Europeo", age=3, weight=4, owner_id=clients[1].id),
            Pet(name="Nala", species="Perro", breed="Bulldog", age=2, weight=18, owner_id=clients[2].id),
        ]
        db.add_all(pets)
        db.commit()

        # Appointments
        now = datetime.utcnow()
        appts = [
            Appointment(date=now + timedelta(days=1), reason="Vacunación", veterinarian="Dr. Ana",
                        pet_id=pets[0].id, client_id=clients[0].id),
            Appointment(date=now + timedelta(days=2), reason="Revisión", veterinarian="Dr. Pepe",
                        pet_id=pets[1].id, client_id=clients[1].id),
        ]
        db.add_all(appts)
        db.commit()

        # Invoice + Payment
        invoice = Invoice(client_id=clients[0].id, total=50.0, paid=False)
        db.add(invoice)
        db.commit()

        payment = Payment(invoice_id=invoice.id, amount=50.0, method="efectivo")
        invoice.paid = True
        db.add(payment)
        db.commit()

        print("Seed finished")
    finally:
        db.close()

if __name__ == "__main__":
    create_all()
    seed()
