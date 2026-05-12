from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.database.session import Base

class Employee(Base):
    """
    SQLAlchemy Employee model representing the employees table.
    """
    __tablename__ = "employees"
    
    employeeNumber = Column(Integer, primary_key=True, index=True)
    lastName = Column(String(50), nullable=False, index=True)
    firstName = Column(String(50), nullable=False)
    extension = Column(String(10), nullable=False)
    email = Column(String(100), nullable=False, unique=True, index=True)
    officeCode = Column(String(10), ForeignKey('offices.officeCode'), nullable=False, index=True)
    reportsTo = Column(Integer, ForeignKey('employees.employeeNumber'), nullable=True, index=True)
    jobTitle = Column(String(50), nullable=False)
    
    # Relationships
    office = relationship("Office", back_populates="employees")
    reports_to_employee = relationship("Employee", remote_side=[employeeNumber])
    customers = relationship("Customer", back_populates="sales_rep")
    
    def __repr__(self):
        return f"<Employee(employeeNumber={self.employeeNumber}, name='{self.firstName} {self.lastName}')>"
