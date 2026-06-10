from flask import Flask, jsonify, request
from extensions import db, migrate
from models import Brendovi, Artikli, Kategorije, Korisnik, Velicine
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.config["SQLALCHEMY_DATABASE_URI"] = "mysql+pymysql://root:@localhost/trgovina_obuce"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
migrate.init_app(app, db)


@app.route('/')
def index():
    return "Početna - Trgovina Obuće"


# --- ARTIKLI ---
@app.route('/artikli', methods=['GET'])
def get_artikli():
    svi_artikli = Artikli.query.all()
    return jsonify([a.to_dict() for a in svi_artikli])


def get_or_create_velicina(broj):
    if broj is None:
        return None
    try:
        broj = float(broj)
    except (TypeError, ValueError):
        return None
    velicina = Velicine.query.filter_by(broj=broj).first()
    if not velicina:
        velicina = Velicine(broj=broj)
        db.session.add(velicina)
        db.session.flush()
    return velicina

@app.route('/artikli', methods=['POST'])
def dodaj_artikl():
    data = request.get_json()
    try:
        
        kat = Kategorije.query.first()
        kat_id = kat.id if kat else 1

        novi = Artikli(
            naziv=data.get('naziv'),
            cijena=float(data.get('cijena', 0)),
            brend_id=int(data.get('brend_id', 1)),
            kategorija_id=kat_id,
            slika_url=data.get('slika_url', ''),
            na_stanju=data.get('na_stanju', True)
        )

        brojevi = data.get('brojevi', [])
        if isinstance(brojevi, str):
            brojevi = [v.strip() for v in brojevi.split(',') if v.strip()]
        novi.dostupne_velicine = [v for v in (get_or_create_velicina(b) for b in brojevi) if v]

        db.session.add(novi)
        db.session.commit()
        return jsonify({"poruka": "Artikl dodan"}), 201
    except Exception as e:
        db.session.rollback()
        print(f"Baza javlja grešku: {e}")
        return jsonify({"poruka": "Greška na serveru", "error": str(e)}), 400


@app.route('/artikli/<int:id>', methods=['DELETE'])
def obrisi_artikl_ruta(id):
    try:
        a = Artikli.query.get_or_404(id)
        db.session.delete(a)
        db.session.commit()
        return jsonify({"poruka": "Artikl obrisan"}), 200
    except Exception as e:
        return jsonify({"poruka": "Greška pri brisanju"}), 400


@app.route('/artikli/<int:id>', methods=['PUT'])
def uredi_artikl_ruta(id):
    data = request.get_json()
    try:
        artikl = Artikli.query.get_or_404(id)
        artikl.naziv = data.get('naziv', artikl.naziv)
        artikl.cijena = float(data.get('cijena', artikl.cijena))
        artikl.slika_url = data.get('slika_url', artikl.slika_url)
        artikl.brend_id = int(data.get('brend_id', artikl.brend_id))
        artikl.na_stanju = data.get('na_stanju', artikl.na_stanju)

        brojevi = data.get('brojevi', [])
        if isinstance(brojevi, str):
            brojevi = [v.strip() for v in brojevi.split(',') if v.strip()]
        artikl.dostupne_velicine = [v for v in (get_or_create_velicina(b) for b in brojevi) if v]

        db.session.commit()
        return jsonify({"poruka": "Artikl ažuriran"}), 200
    except Exception as e:
        db.session.rollback()
        print(f"Greška pri uređivanju artikla: {e}")
        return jsonify({"poruka": "Greška pri uređivanju artikla", "error": str(e)}), 400


# --- BRENDOVI ---
@app.route('/brendovi', methods=['GET'])
def get_brendovi():
    svi_brendovi = Brendovi.query.all()
    return jsonify([b.to_dict() for b in svi_brendovi])


# --- DASHBOARD ---
@app.route('/dashboard', methods=['GET'])
def dashboard():
    return jsonify({
        "broj_artikala": Artikli.query.count(),
        "broj_brendova": Brendovi.query.count(),
        "broj_korisnika": Korisnik.query.count(),
        "broj_kategorija": Kategorije.query.count()
    })


if __name__ == '__main__':
    app.run(debug=True, port=5005)
