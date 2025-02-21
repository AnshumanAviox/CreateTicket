from sqlalchemy import Column, String, DateTime, Float
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class InvoiceTable(Base):
    __tablename__ = 'INVOICE_TABLE'
    __table_args__ = {'schema': 'dbo'}

    Billing_ID = Column(String, primary_key=True)
    Ticket_ID = Column(String)
    Customer_ID = Column(String)
    Called = Column(String)
    Pickup_Date = Column(DateTime)
    Vehicle_Type = Column(String)
    Rate_Type = Column(String)
    Notes = Column(String)
    PO = Column(String)
    Pieces = Column(Float)
    Skids = Column(Float)
    Weight = Column(Float)
    COD = Column(Float)
    From_Company = Column(String)
    From_Contact = Column(String)
    From_Address_1 = Column(String)
    From_Address_2 = Column(String)
    From_City = Column(String)
    From_State = Column(String)
    From_Zip = Column(String)
    From_Phone = Column(String)
    From_Alt_Phone = Column(String)
    To_Company = Column(String)
    To_Contact = Column(String)
    To_Address_1 = Column(String)
    To_Address_2 = Column(String)
    To_City = Column(String)
    To_State = Column(String)
    To_Zip = Column(String)
    To_Phone = Column(String)
    To_Alt_Phone = Column(String) 