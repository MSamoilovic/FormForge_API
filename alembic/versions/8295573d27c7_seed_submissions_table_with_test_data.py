"""Seed submissions for existing forms

Revision ID: <generisani_hash_iz_komande>
Revises:
Create Date: 2025-09-29 15:48:00

"""
from alembic import op
import sqlalchemy as sa
import datetime
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '8295573d27c7'
down_revision = '0001_initial'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # First, create the forms that we need for the submissions
    # Note: theme column is added in the next migration, so we don't include it here
    forms_table = sa.table('forms',
                          sa.column('id', sa.Integer),
                          sa.column('name', sa.String),
                          sa.column('description', sa.String),
                          sa.column('fields', postgresql.JSON),
                          sa.column('rules', postgresql.JSON))
    
    # Insert forms if they don't exist
    op.bulk_insert(forms_table,
                   [
                       {
                           'id': 2,
                           'name': 'Jednostavna Kontakt Forma',
                           'description': 'Kontakt forma sa osnovnim poljima',
                           'fields': [
                               {'id': 'ime_prezime', 'type': 'text', 'label': 'Ime i Prezime', 'required': True},
                               {'id': 'email_adresa', 'type': 'email', 'label': 'Email Adresa', 'required': True},
                               {'id': 'poruka', 'type': 'textarea', 'label': 'Poruka', 'required': True}
                           ],
                           'rules': []
                       },
                       {
                           'id': 4,
                           'name': 'Forma sa Pravilima',
                           'description': 'Demo forma sa conditional logic',
                           'fields': [
                               {'id': 'tip_korisnika', 'type': 'radio', 'label': 'Tip Korisnika', 'required': True,
                                'options': [{'value': 'fizicko', 'label': 'Fizičko lice'}, {'value': 'pravno', 'label': 'Pravno lice'}]},
                               {'id': 'pib_firme', 'type': 'text', 'label': 'PIB Firme', 'required': False},
                               {'id': 'maticni_broj', 'type': 'text', 'label': 'Matični Broj', 'required': False}
                           ],
                           'rules': []
                       },
                       {
                           'id': 5,
                           'name': 'Anketa o Zadovoljstvu',
                           'description': 'Anketa za prikupljanje feedback-a',
                           'fields': [
                               {'id': 'ocena_usluge', 'type': 'number', 'label': 'Ocena Usluge', 'required': True, 'min': 1, 'max': 5},
                               {'id': 'dodatni_komentar', 'type': 'textarea', 'label': 'Dodatni Komentar', 'required': False},
                               {'id': 'dozvola_kontakt', 'type': 'checkbox', 'label': 'Dozvola za Kontakt', 'required': False},
                               {'id': 'ime', 'type': 'text', 'label': 'Ime', 'required': True}
                           ],
                           'rules': []
                       }
                   ])

    # Definišemo strukturu tabele sa kojom radimo
    submissions_table = sa.table('submissions',
                                 sa.column('id', sa.Integer),
                                 sa.column('form_id', sa.Integer),
                                 sa.column('submitted_at', sa.DateTime),
                                 sa.column('data', postgresql.JSON)
                                 )

    # Koristimo bulk_insert da dodamo više redova odjednom
    op.bulk_insert(submissions_table,
                   [
                       # --- Odgovori za Formu ID=2 ("Jednostavna Kontakt Forma") ---
                       {
                           'form_id': 2,
                           'submitted_at': datetime.datetime.utcnow(),
                           'data': {
                               'ime_prezime': 'Marko Marković',
                               'email_adresa': 'marko@example.com',
                               'poruka': 'Sve pohvale za vaš proizvod, odličan je!'
                           }
                       },
                       {
                           'form_id': 2,
                           'submitted_at': datetime.datetime.utcnow() - datetime.timedelta(hours=1),
                           'data': {
                               'ime_prezime': 'Jelena Jelić',
                               'email_adresa': 'jelena@example.com',
                               'poruka': 'Imam pitanje u vezi sa dostavom, da li šaljete van Srbije?'
                           }
                       },

                       # --- Odgovori za Formu ID=4 ("Forma sa Pravilima") ---
                       {
                           'form_id': 4,
                           'submitted_at': datetime.datetime.utcnow() - datetime.timedelta(days=1),
                           'data': {  # Slučaj "Pravno lice"
                               'tip_korisnika': 'pravno',
                               'pib_firme': '123456789',
                               'maticni_broj': '98765432'
                           }
                       },
                       {
                           'form_id': 4,
                           'submitted_at': datetime.datetime.utcnow() - datetime.timedelta(days=2),
                           'data': {  # Slučaj "Fizičko lice"
                               'tip_korisnika': 'fizicko',
                               'pib_firme': None,  # Polja su prazna, kao što bi pravila diktirala
                               'maticni_broj': None
                           }
                       },

                       # --- Odgovori za Formu ID=5 ("Anketa o Zadovoljstvu") ---
                       {
                           'form_id': 5,
                           'submitted_at': datetime.datetime.utcnow() - datetime.timedelta(minutes=30),
                           'data': {
                               'ocena_usluge': 5,
                               'dodatni_komentar': 'Korisnička podrška je bila izvanredna. Brz i efikasan odgovor.',
                               'dozvola_kontakt': True,
                               'ime': 'Ana Anić'
                           }
                       },
                       {
                           'form_id': 5,
                           'submitted_at': datetime.datetime.utcnow() - datetime.timedelta(hours=3),
                           'data': {
                               'ocena_usluge': 3,
                               'dodatni_komentar': '',
                               'dozvola_kontakt': False,
                               'ime': 'Petar Perić'
                           }
                       }
                   ]
                   )


def downgrade() -> None:
    # Logika za brisanje ovih podataka ako želimo da "poništimo" migraciju
    op.execute("DELETE FROM submissions WHERE form_id IN (2, 4, 5)")
    op.execute("DELETE FROM forms WHERE id IN (2, 4, 5)")
