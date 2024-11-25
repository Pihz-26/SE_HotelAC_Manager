from fastapi import FastAPI
from dbcontrol import Room, HotelCheck, acLog, acControl, RoomCheckIn, RoomAcData
from dbcontrol import engine, SessionDep, create_db_and_tables, data_check_in, data_check_out
from sqlmodel import Field, Session, SQLModel, Relationship, ForeignKey, create_engine, select


app = FastAPI()
create_db_and_tables()

@app.get("/test/check_in")
async def test_check_in(session: SessionDep):
    room_data = RoomCheckIn("12321", [("张三", "423141265764751")])
    print(room_data)
    data_check_in(room_data, session)
    datas = session.exec(select(HotelCheck)).all()
    return datas

@app.get("/test/check_out")
async def test_check_out(session: SessionDep):
    data_check_out("12321", session)
    datas = session.exec(select(HotelCheck)).all()
    return datas