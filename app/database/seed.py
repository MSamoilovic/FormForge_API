"""
Seed script za FormForge API
Popunjava bazu sa test podacima za development
"""
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.infrastructure.database.session import SessionLocal
from app.domain.models.form import Form
from app.domain.models.submission import Submission
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def clear_data(db: Session):
    """Briše sve postojeće podatke iz baze"""
    logger.info("🗑️  Brisanje postojećih podataka...")
    db.query(Submission).delete()
    db.query(Form).delete()
    db.commit()
    logger.info("✅ Podaci obrisani")


def seed_forms(db: Session):
    """Kreira test forme"""
    logger.info("📝 Kreiranje test formi...")
    
    forms = [
        Form(
            id=1,
            name="Kontakt Forma",
            description="Jednostavna kontakt forma za korisnike",
            fields=[
                {
                    "id": "ime",
                    "type": "text",
                    "label": "Ime i Prezime",
                    "required": True,
                    "placeholder": "Unesite vaše ime i prezime"
                },
                {
                    "id": "email",
                    "type": "email",
                    "label": "Email Adresa",
                    "required": True,
                    "placeholder": "vas@email.com"
                },
                {
                    "id": "poruka",
                    "type": "textarea",
                    "label": "Poruka",
                    "required": True,
                    "placeholder": "Vaša poruka..."
                }
            ],
            rules=[],
            theme={
                "primaryColor": "#3B82F6",
                "backgroundColor": "#F3F4F6",
                "fontFamily": "Inter, sans-serif"
            }
        ),
        Form(
            id=2,
            name="Registraciona Forma",
            description="Forma za registraciju korisnika sa naprednim poljima",
            fields=[
                {
                    "id": "korisnicko_ime",
                    "type": "text",
                    "label": "Korisničko Ime",
                    "required": True,
                    "minLength": 3,
                    "maxLength": 20
                },
                {
                    "id": "email",
                    "type": "email",
                    "label": "Email",
                    "required": True
                },
                {
                    "id": "lozinka",
                    "type": "password",
                    "label": "Lozinka",
                    "required": True,
                    "minLength": 8
                },
                {
                    "id": "datum_rodjenja",
                    "type": "date",
                    "label": "Datum Rođenja",
                    "required": False
                },
                {
                    "id": "drzava",
                    "type": "select",
                    "label": "Država",
                    "required": True,
                    "options": [
                        {"value": "rs", "label": "Srbija"},
                        {"value": "hr", "label": "Hrvatska"},
                        {"value": "ba", "label": "Bosna i Hercegovina"},
                        {"value": "me", "label": "Crna Gora"}
                    ]
                },
                {
                    "id": "saglasnost",
                    "type": "checkbox",
                    "label": "Slažem se sa uslovima korišćenja",
                    "required": True
                }
            ],
            rules=[],
            theme={
                "primaryColor": "#10B981",
                "backgroundColor": "#FFFFFF",
                "fontFamily": "Roboto, sans-serif"
            }
        ),
        Form(
            id=3,
            name="Anketa o Zadovoljstvu",
            description="Anketa za prikupljanje feedback-a od korisnika",
            fields=[
                {
                    "id": "ocena",
                    "type": "number",
                    "label": "Ocena (1-5)",
                    "required": True,
                    "min": 1,
                    "max": 5
                },
                {
                    "id": "komentar",
                    "type": "textarea",
                    "label": "Komentar",
                    "required": False,
                    "placeholder": "Podelite vaše mišljenje sa nama..."
                },
                {
                    "id": "preporuka",
                    "type": "radio",
                    "label": "Da li biste nas preporučili drugima?",
                    "required": True,
                    "options": [
                        {"value": "da", "label": "Da"},
                        {"value": "ne", "label": "Ne"},
                        {"value": "mozda", "label": "Možda"}
                    ]
                }
            ],
            rules=[],
            theme={
                "primaryColor": "#F59E0B",
                "backgroundColor": "#FEF3C7",
                "fontFamily": "Poppins, sans-serif"
            }
        ),
        Form(
            id=4,
            name="Forma sa Pravilima",
            description="Demo forma sa conditional logic - različita polja za fizičko i pravno lice",
            fields=[
                {
                    "id": "tip_lica",
                    "type": "radio",
                    "label": "Tip Korisnika",
                    "required": True,
                    "options": [
                        {"value": "fizicko", "label": "Fizičko lice"},
                        {"value": "pravno", "label": "Pravno lice"}
                    ]
                },
                {
                    "id": "ime_prezime",
                    "type": "text",
                    "label": "Ime i Prezime",
                    "required": True,
                    "visible": True
                },
                {
                    "id": "jmbg",
                    "type": "text",
                    "label": "JMBG",
                    "required": False,
                    "visible": False
                },
                {
                    "id": "naziv_firme",
                    "type": "text",
                    "label": "Naziv Firme",
                    "required": False,
                    "visible": False
                },
                {
                    "id": "pib",
                    "type": "text",
                    "label": "PIB",
                    "required": False,
                    "visible": False
                }
            ],
            rules=[
                {
                    "type": "visibility",
                    "condition": {
                        "field": "tip_lica",
                        "operator": "equals",
                        "value": "fizicko"
                    },
                    "target": "jmbg",
                    "action": "show"
                },
                {
                    "type": "visibility",
                    "condition": {
                        "field": "tip_lica",
                        "operator": "equals",
                        "value": "pravno"
                    },
                    "target": "naziv_firme",
                    "action": "show"
                },
                {
                    "type": "visibility",
                    "condition": {
                        "field": "tip_lica",
                        "operator": "equals",
                        "value": "pravno"
                    },
                    "target": "pib",
                    "action": "show"
                }
            ],
            theme={
                "primaryColor": "#8B5CF6",
                "backgroundColor": "#F5F3FF",
                "fontFamily": "Inter, sans-serif"
            }
        ),
        Form(
            id=5,
            name="Event Registracija",
            description="Forma za prijavu na događaj",
            fields=[
                {
                    "id": "ime",
                    "type": "text",
                    "label": "Ime",
                    "required": True
                },
                {
                    "id": "prezime",
                    "type": "text",
                    "label": "Prezime",
                    "required": True
                },
                {
                    "id": "email",
                    "type": "email",
                    "label": "Email",
                    "required": True
                },
                {
                    "id": "telefon",
                    "type": "tel",
                    "label": "Telefon",
                    "required": False
                },
                {
                    "id": "broj_gostiju",
                    "type": "number",
                    "label": "Broj Gostiju",
                    "required": True,
                    "min": 1,
                    "max": 5,
                    "default": 1
                },
                {
                    "id": "dijeta",
                    "type": "checkbox",
                    "label": "Imam posebne dijetetske zahteve",
                    "required": False
                },
                {
                    "id": "dijeta_opis",
                    "type": "textarea",
                    "label": "Opišite dijetetske zahteve",
                    "required": False,
                    "visible": False
                }
            ],
            rules=[
                {
                    "type": "visibility",
                    "condition": {
                        "field": "dijeta",
                        "operator": "equals",
                        "value": True
                    },
                    "target": "dijeta_opis",
                    "action": "show"
                }
            ],
            theme={
                "primaryColor": "#EF4444",
                "backgroundColor": "#FEE2E2",
                "fontFamily": "Montserrat, sans-serif"
            }
        )
    ]
    
    db.add_all(forms)
    db.commit()
    logger.info(f"✅ Kreirano {len(forms)} formi")


def seed_submissions(db: Session):
    """Kreira test submissions"""
    logger.info("📨 Kreiranje test submissions...")
    
    now = datetime.utcnow()
    
    submissions = [
        # Submissions za Kontakt Formu (id=1)
        Submission(
            form_id=1,
            submitted_at=now - timedelta(hours=2),
            data={
                "ime": "Marko Marković",
                "email": "marko.markovic@example.com",
                "poruka": "Pozdrav! Zanima me više informacija o vašim uslugama."
            }
        ),
        Submission(
            form_id=1,
            submitted_at=now - timedelta(hours=5),
            data={
                "ime": "Ana Anić",
                "email": "ana.anic@example.com",
                "poruka": "Odličan proizvod! Sve pohvale timu."
            }
        ),
        Submission(
            form_id=1,
            submitted_at=now - timedelta(days=1),
            data={
                "ime": "Petar Petrović",
                "email": "petar.petrovic@example.com",
                "poruka": "Imam tehničko pitanje. Kako mogu da kontaktiram podršku?"
            }
        ),
        
        # Submissions za Registracionu Formu (id=2)
        Submission(
            form_id=2,
            submitted_at=now - timedelta(hours=1),
            data={
                "korisnicko_ime": "marko123",
                "email": "marko123@example.com",
                "lozinka": "********",
                "datum_rodjenja": "1995-03-15",
                "drzava": "rs",
                "saglasnost": True
            }
        ),
        Submission(
            form_id=2,
            submitted_at=now - timedelta(hours=3),
            data={
                "korisnicko_ime": "jelena_j",
                "email": "jelena@example.com",
                "lozinka": "********",
                "datum_rodjenja": "1990-07-22",
                "drzava": "hr",
                "saglasnost": True
            }
        ),
        
        # Submissions za Anketu (id=3)
        Submission(
            form_id=3,
            submitted_at=now - timedelta(minutes=30),
            data={
                "ocena": 5,
                "komentar": "Odličan servis, brza dostava!",
                "preporuka": "da"
            }
        ),
        Submission(
            form_id=3,
            submitted_at=now - timedelta(hours=2),
            data={
                "ocena": 4,
                "komentar": "Dobro, ali može i bolje.",
                "preporuka": "mozda"
            }
        ),
        Submission(
            form_id=3,
            submitted_at=now - timedelta(hours=4),
            data={
                "ocena": 3,
                "komentar": "",
                "preporuka": "ne"
            }
        ),
        Submission(
            form_id=3,
            submitted_at=now - timedelta(days=1),
            data={
                "ocena": 5,
                "komentar": "Najbolji proizvod koji sam probao!",
                "preporuka": "da"
            }
        ),
        
        # Submissions za Formu sa Pravilima (id=4)
        Submission(
            form_id=4,
            submitted_at=now - timedelta(hours=1),
            data={
                "tip_lica": "fizicko",
                "ime_prezime": "Milan Milić",
                "jmbg": "1234567890123"
            }
        ),
        Submission(
            form_id=4,
            submitted_at=now - timedelta(hours=6),
            data={
                "tip_lica": "pravno",
                "ime_prezime": "Tech Solutions DOO",
                "naziv_firme": "Tech Solutions",
                "pib": "123456789"
            }
        ),
        
        # Submissions za Event Registraciju (id=5)
        Submission(
            form_id=5,
            submitted_at=now - timedelta(minutes=15),
            data={
                "ime": "Stefan",
                "prezime": "Stefanović",
                "email": "stefan@example.com",
                "telefon": "+381641234567",
                "broj_gostiju": 2,
                "dijeta": False
            }
        ),
        Submission(
            form_id=5,
            submitted_at=now - timedelta(hours=1),
            data={
                "ime": "Ivana",
                "prezime": "Ivanović",
                "email": "ivana@example.com",
                "telefon": "+381691234567",
                "broj_gostiju": 1,
                "dijeta": True,
                "dijeta_opis": "Vegetarijanska ishrana, bez glutena"
            }
        ),
        Submission(
            form_id=5,
            submitted_at=now - timedelta(hours=3),
            data={
                "ime": "Nikola",
                "prezime": "Nikolić",
                "email": "nikola@example.com",
                "telefon": "",
                "broj_gostiju": 3,
                "dijeta": False
            }
        )
    ]
    
    db.add_all(submissions)
    db.commit()
    logger.info(f"✅ Kreirano {len(submissions)} submissions")


def run_seed(clear: bool = False):
    """
    Pokreće seed process
    
    Args:
        clear: Ako je True, briše sve postojeće podatke pre seed-a
    """
    logger.info("🌱 Pokretanje seed procesa...")
    
    db = SessionLocal()
    try:
        if clear:
            clear_data(db)
        
        seed_forms(db)
        seed_submissions(db)
        
        # Prikaži statistiku
        forms_count = db.query(Form).count()
        submissions_count = db.query(Submission).count()
        
        logger.info("=" * 60)
        logger.info("🎉 Seed završen uspešno!")
        logger.info(f"📊 Statistika:")
        logger.info(f"   - Forme: {forms_count}")
        logger.info(f"   - Submissions: {submissions_count}")
        logger.info("=" * 60)
        
    except Exception as e:
        logger.error(f"❌ Greška tokom seed-a: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    
    # Prihvati --clear flag
    clear = "--clear" in sys.argv
    
    run_seed(clear=clear)


