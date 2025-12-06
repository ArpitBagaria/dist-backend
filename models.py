"""Database ORM Models - defines all tables"""
from sqlalchemy import Column, Integer, String, Float, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base


class Retailer(Base):
    __tablename__ = "retailers"
    id = Column(Integer, primary_key=True, index=True)
    retailer_code = Column(String, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=False)
    address = Column(Text, nullable=True)
    contact_phone = Column(String, nullable=True)
    tally_ledger_name = Column(String, nullable=True)
    inventory_snapshots = relationship("PrmInventorySnapshot", back_populates="retailer")
    activations = relationship("Activation", back_populates="retailer")
    ledger_cache = relationship("TallyLedgerCache", back_populates="retailer")


class Product(Base):
    __tablename__ = "products"
    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(String, unique=True, nullable=False, index=True)
    name = Column(Text, nullable=True)
    category = Column(String, nullable=True)
    current_price = Column(Float, nullable=True)
    last_price_update = Column(DateTime, default=func.now(), onupdate=func.now())
    inventory_snapshots = relationship("PrmInventorySnapshot", back_populates="product")
    activations = relationship("Activation", back_populates="product")
    price_history = relationship("PriceHistory", back_populates="product")  # FIXED: Added missing relationship


class PrmInventorySnapshot(Base):
    __tablename__ = "prm_inventory_snapshot"
    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    goods_id = Column(String, ForeignKey("products.goods_id"), nullable=False)
    quantity = Column(Integer, nullable=False)
    last_seen = Column(DateTime, default=func.now())
    retailer = relationship("Retailer", back_populates="inventory_snapshots")
    product = relationship("Product", back_populates="inventory_snapshots")


class Activation(Base):
    __tablename__ = "activations"
    id = Column(Integer, primary_key=True, index=True)
    goods_id = Column(String, ForeignKey("products.goods_id"), nullable=False)
    imei_sn = Column(String, nullable=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=True)
    activation_status = Column(String, nullable=True)
    activation_time = Column(DateTime, nullable=True)
    product = relationship("Product", back_populates="activations")
    retailer = relationship("Retailer", back_populates="activations")


class TallyLedgerCache(Base):
    __tablename__ = "tally_ledger_cache"
    id = Column(Integer, primary_key=True, index=True)
    retailer_id = Column(Integer, ForeignKey("retailers.id"), nullable=False)
    ledger_name = Column(Text, nullable=False)
    closing_balance = Column(Float, nullable=True)
    as_of = Column(DateTime, default=func.now())
    retailer = relationship("Retailer", back_populates="ledger_cache")


class PriceHistory(Base):
    """Price History - tracks all price changes"""
    __tablename__ = "price_history"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    old_price = Column(Float, nullable=True)
    new_price = Column(Float, nullable=False)
    changed_at = Column(DateTime, default=func.now())
    source = Column(String, default='admin_api')
    
    # Relationships
    product = relationship("Product", back_populates="price_history")


class PrmSyncRunLog(Base):
    __tablename__ = "prm_sync_run_log"
    id = Column(Integer, primary_key=True, index=True)
    started_at = Column(DateTime, default=func.now())
    finished_at = Column(DateTime, nullable=True)
    status = Column(String, nullable=True)
    rows_imported = Column(Integer, nullable=True)
    error_message = Column(Text, nullable=True)
