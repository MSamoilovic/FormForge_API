"""Seed submissions for existing forms

Revision ID: <generisani_hash_iz_komande>
Revises:
Create Date: 2025-09-29 15:48:00

"""
from alembic import op
import sqlalchemy as sa
import datetime

# revision identifiers, used by Alembic.
revision = '<generisani_hash_iz_komande>'  # Zameni sa pravim ID-jem
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Definišemo strukturu tabele sa kojom radimo
    submissions_table = sa.table('submissions',
                                 sa.column('id', sa.Integer),
                                 sa.column('form_id', sa.Integer),
                                 sa.column('submitted_at', sa.DateTime),
                                 sa.column('data', sa.JSON)
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
