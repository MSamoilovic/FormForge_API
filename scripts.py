import uvicorn
import sys


def run_dev():
    """Pokreće development server sa hot-reload"""
    uvicorn.run("app.main:app", reload=True)


def seed_db():

    from app.database.seed import run_seed

    clear = "--clear" in sys.argv
    
    if clear:
        response = input("Da li želite da nastavite? (da/ne): ")
        if response.lower() not in ['da', 'yes', 'y']:
            print("❌ Operacija otkazana")
            return
    
    run_seed(clear=clear)


def reset_db():
    """Briše sve podatke i ponovo popunjava bazu"""
    response = input("Da li ste sigurni? (da/ne): ")
    if response.lower() not in ['da', 'yes', 'y']:
        print("❌ Operacija otkazana")
        return
    
    from app.database.seed import run_seed
    run_seed(clear=True)   