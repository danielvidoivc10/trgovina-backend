from extensions import db

artikl_velicina = db.Table('artikl_velicina',
                           db.Column('artikl_id', db.Integer, db.ForeignKey('artikli.id'), primary_key=True),
                           db.Column('velicina_id', db.Integer, db.ForeignKey('velicine.id'), primary_key=True)
                           )


class Brendovi(db.Model):
    __tablename__ = "brendovi"
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), nullable=False)
    drzava = db.Column(db.String(50), nullable=True)

    artikli = db.relationship("Artikli", backref="brend", lazy=True)

    def to_dict(self):
        return {"id": self.id, "naziv": self.naziv, "drzava": self.drzava}


class Kategorije(db.Model):
    __tablename__ = "kategorije"
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(50), nullable=False)

    artikli = db.relationship("Artikli", backref="kategorija", lazy=True)

    def to_dict(self):
        return {"id": self.id, "naziv": self.naziv}


class Velicine(db.Model):
    __tablename__ = "velicine"
    id = db.Column(db.Integer, primary_key=True)
    broj = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {"id": self.id, "broj": self.broj}


class Artikli(db.Model):
    __tablename__ = "artikli"
    id = db.Column(db.Integer, primary_key=True)
    naziv = db.Column(db.String(100), nullable=False)
    cijena = db.Column(db.Float, nullable=False)
    slika_url = db.Column(db.String(500), nullable=True)
    brend_id = db.Column(db.Integer, db.ForeignKey("brendovi.id"), nullable=False)
    kategorija_id = db.Column(db.Integer, db.ForeignKey("kategorije.id"), nullable=True)

    na_stanju = db.Column(db.Boolean, default=True, nullable=False)
    dostupne_velicine = db.relationship("Velicine", secondary=artikl_velicina, backref="artikli")

    def to_dict(self):
        return {
            "id": self.id,
            "naziv": self.naziv,
            "cijena": self.cijena,
            "slika_url": self.slika_url,
            "brend_id": self.brend_id,
            "na_stanju": self.na_stanju,
            "brend": self.brend.naziv if self.brend else None,
            "kategorija": self.kategorija.naziv if self.kategorija else None,
            "brojevi": [v.broj for v in self.dostupne_velicine]
        }


class Korisnik(db.Model):
    __tablename__ = "korisnici"
    id = db.Column(db.Integer, primary_key=True)
    ime = db.Column(db.String(50), nullable=False)
    prezime = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "ime": self.ime,
            "prezime": self.prezime,
            "email": self.email
        }