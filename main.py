from datetime import date, datetime
from decimal import Decimal

from fastapi import FastAPI, HTTPException, Depends
from sqlmodel import Field, Session, SQLModel, create_engine, select
from dotenv import load_dotenv
from sqlalchemy.engine import URL
import os

# Cargar variables de entorno
load_dotenv()

# Conexion a MySQL
url_connection = URL.create(drivername="mysql+pymysql", username=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT")), database=os.getenv("DB_NAME"))
engine = create_engine(url_connection, pool_pre_ping=True)

app = FastAPI(title="API de un Hospital", description="API conectada a AWS/RDS", version="1.0")

def get_session():
    with Session(engine) as session:
        yield session

# Modelo de Medicamentos
class Medicamento(SQLModel, table=True):
    __tablename__ = "Medicamentos"
    Id_Medicamento: int | None = Field(default=None, primary_key=True)
    Nombre: str = Field(max_length=100)
    Principio_Activo: str = Field(max_length=150)
    Concentracion: str = Field(max_length=50)
    Forma_Farmaceutica: str = Field(max_length=50)
    Lote: str | None = Field(default=None, max_length=30)
    Fecha_Registro: datetime | None = Field(default=None)
    Fecha_caducidad: date
    Precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    Via_administracion: str = Field(max_length=30)

class MedicamentoRespuesta(SQLModel):
    Id_Medicamento: int | None = Field(default=None, primary_key=True)
    Nombre: str = Field(max_length=100)
    Principio_Activo: str = Field(max_length=150)
    Concentracion: str = Field(max_length=50)
    Forma_Farmaceutica: str = Field(max_length=50)
    Lote: str | None = Field(default=None, max_length=30)
    Fecha_Registro: datetime | None = Field(default=None)
    Fecha_caducidad: date
    Precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    Via_administracion: str = Field(max_length=30)

#GET
#Obtener todos los medicamentos
@app.get("/medicamentos", tags=["Medicamentos"], response_model=list[MedicamentoRespuesta])
def obtener_medicamentos(session: Session = Depends(get_session)):
    consulta = select(Medicamento)
    resultados = session.exec(consulta).all()
    return resultados

#Obtener medicamentos por Id
@app.get("/medicamentos/{id}", tags=["Medicamentos"])
def obtener_medicamento(id: int, session: Session = Depends(get_session)):
    medicamento = session.get(Medicamento, id)
    if medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")
    return medicamento

#POST
#Crear Medicamento
class Crear_Medicamento(SQLModel):
    Nombre: str = Field(max_length=100)
    Principio_Activo: str = Field(max_length=150)
    Concentracion: str = Field(max_length=50)
    Forma_Farmaceutica: str = Field(max_length=50)
    Lote: str | None = Field(default=None, max_length=30)
    Fecha_Registro: datetime | None = Field(default=None)
    Fecha_caducidad: date
    Precio_unitario: Decimal = Field(max_digits=10, decimal_places=2)
    Via_administracion: str = Field(max_length=30)

class Actualizar_Medicamento_id(SQLModel):
    Nombre: str | None = Field(default=None, max_length=100)
    Principio_Activo: str | None = Field(default=None, max_length=150)
    Concentracion: str | None = Field(default=None, max_length=50)
    Forma_Farmaceutica: str | None = Field(default=None, max_length=50)
    Lote: str | None = Field(default=None, max_length=30)
    Fecha_Registro: datetime | None = Field(default=None)
    Fecha_caducidad: date | None = Field(default=None)
    Precio_unitario: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    Via_administracion: str | None = Field(default=None, max_length=30)

# Registrar un medicamento
@app.post("/medicamentos", response_model=Medicamento, status_code=201, tags=["Medicamentos"])
def crear_medicamento(datos: Crear_Medicamento, session: Session = Depends(get_session)):
    nuevo_medicamento = Medicamento(**datos.model_dump())
    session.add(nuevo_medicamento)
    session.commit()
    session.refresh(nuevo_medicamento)
    return nuevo_medicamento

#PUT Medicamento
#Actualizar Medicamento por Id

# PUT / PATCH Medicamento
# Actualizar Medicamento por ID
@app.patch("/medicamentos/{id}", response_model=Medicamento, tags=["Medicamentos"])
def actualizar_medicamento(id: int, datos: Actualizar_Medicamento_id, session: Session = Depends(get_session)):
    medicamento = session.get(Medicamento, id)

    if medicamento is None:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")

    datos_actualizados = datos.model_dump(exclude_unset=True)

    for campo, valor in datos_actualizados.items():
        setattr(medicamento, campo, valor)

    session.commit()
    session.refresh(medicamento)
    return medicamento


#DELETE
#Eliminar Medicamento por Id
@app.delete("/medicamentos/{id}", tags=["Medicamentos"])
def eliminar_medicamento(id: int, session: Session = Depends(get_session)):
    medicamentoeliminar = session.get(Medicamento, id)
    if medicamentoeliminar is None:
        raise HTTPException(status_code=404, detail="Medicamento no encontrado")

    session.delete(medicamentoeliminar)
    session.commit()
    return {"message": "Medicamento eliminado correctamente"}


#Modelo de Doctores
class Doctor(SQLModel, table=True):
    __tablename__="Doctores"
    Id_Doctor: int | None = Field(default=None, primary_key=True)
    Nombre: str | None = Field(default=None, max_length=100)
    Apellidos: str | None = Field(default=None, max_length=100)
    Cedula_Profesional: str | None = Field(default=None, max_length=8, unique=True)
    Especialidad: str | None = Field(default=None, max_length=100)
    Fecha_Nacimiento: date | None = Field(default=None)
    Sueldo: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    Telefono: str | None = Field(default=None, max_length=10)
    Cargo_Puesto: str | None = Field(default=None, max_length=100)
    Estado: str | None = Field(default=None, max_length=100)

class DoctorRespuesta(SQLModel):
    Id_Doctor: int | None = Field(default=None, primary_key=True)
    Nombre: str | None = Field(default=None, max_length=100)
    Apellidos: str | None = Field(default=None, max_length=100)
    Cedula_Profesional: str | None = Field(default=None, max_length=8, unique=True)
    Especialidad: str | None = Field(default=None, max_length=100)
    Fecha_Nacimiento: date | None = Field(default=None)
    Sueldo: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    Telefono: str | None = Field(default=None, max_length=10)
    Cargo_Puesto: str | None = Field(default=None, max_length=100)
    Estado: str | None = Field(default=None, max_length=100)

#GET
#Obtener todos los doctores
@app.get("/doctores", tags=["Doctores"], response_model=list[DoctorRespuesta])
def obtener_doctores(session:Session = Depends(get_session)):
    consultadoc=select(Doctor)
    resultadosdoc = session.exec(consultadoc).all()
    return resultadosdoc

#Obtener docotores por Id
@app.get("/doctores/{id}", tags=["Doctores"])
def obtener_doctor(id:int, session: Session = Depends(get_session)):
    doctor=session.get(Doctor, id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    return doctor

#POST
#Crear doctor
class Crear_Doctor(SQLModel):
    Nombre: str | None = Field(default=None, max_length=100)
    Apellidos: str | None = Field(default=None, max_length=100)
    Cedula_Profesional: str | None = Field(default=None, max_length=8, unique=True)
    Especialidad: str | None = Field(default=None, max_length=100)
    Fecha_Nacimiento: date | None = Field(default=None)
    Sueldo: Decimal | None = Field(default=None, max_digits=10, decimal_places=2)
    Telefono: str | None = Field(default=None, max_length=10)
    Cargo_Puesto: str | None = Field(default=None, max_length=100)
    Estado: str | None = Field(default=None, max_length=100)

#Registrar Doctor
@app.post("/doctores", response_model=Doctor, status_code=201, tags=["Doctores"])
def crear_doctor(datos: Crear_Doctor, session: Session = Depends(get_session)):
    nuevo_doctor = Doctor(**datos.model_dump())
    session.add(nuevo_doctor)
    session.commit()
    session.refresh(nuevo_doctor)
    return nuevo_doctor

#PUT
#Actualizar Doctor por ID
@app.put("/doctores/{id}", response_model=Doctor, tags=["Doctores"])
def actualizar_doctor(id: int, datos: Crear_Doctor, session: Session = Depends(get_session)):
    doctor = session.get(Doctor, id)
    if doctor is None:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")
    datos_actualizados = datos.model_dump()
    for campo, valor in datos_actualizados.items():
        setattr(doctor, campo, valor)
    session.add(doctor)
    session.commit()
    session.refresh(doctor)
    return doctor

#DELETE
#Eliminar Doctor por Id
@app.delete("/doctores/{id}", tags=["Doctores"])
def eliminar_doctor(id: int, session: Session = Depends(get_session)):
    eliminardoctor = session.get(Doctor, id)
    if eliminardoctor is None:
        raise HTTPException(status_code=404, detail="Doctor no encontrado")

    session.delete(eliminardoctor)
    session.commit()
    return {"message": "Doctor eliminado correctamente"}

@app.get("/")
def root():
    return {"mensaje": "API de medicamentos funcionando correctamente"}