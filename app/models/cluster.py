from sqlalchemy import Column, Integer, String, DateTime, JSON, Table, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base

# Association Table
order_cluster_association = Table(
    "order_cluster_association",
    Base.metadata,
    Column("cluster_id", String, ForeignKey("order_clusters.id"), primary_key=True),
    Column("order_id", Integer, ForeignKey("orders.id"), primary_key=True),
)


class OrderCluster(Base):
    __tablename__ = "order_clusters"

    id = Column(String, primary_key=True, index=True, nullable=False)
    time_window = Column(DateTime, nullable=False)
    total_items = Column(Integer, nullable=False)
    earliest_delivery_time = Column(DateTime, nullable=False)
    cluster_route = Column(JSON, nullable=False)

    # Many-to-many relationship
    orders = relationship(
        "Order",
        secondary="order_cluster_association",
        back_populates="clusters",
    )
