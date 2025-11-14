from sqlalchemy import create_engine, event # pool
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, scoped_session
from sqlalchemy.exc import SQLAlchemyError, OperationalError
from contextlib import contextmanager
import logging
from typing import Generator
from app.core.config import get_config

logger = logging.getLogger(__name__)
config = get_config()

# Base class cho các models
Base = declarative_base()


class Database:
    """Quản lý kết nối database"""

    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._initialized = False

    def init_db(self):
        """Khởi tạo database engine và session"""
        if self._initialized:
            logger.warning("Database already initialized")
            return

        try:
            # Tạo engine với connection pooling
            self.engine = create_engine(
                config.SQLALCHEMY_DATABASE_URI,
                **config.SQLALCHEMY_ENGINE_OPTIONS,
                echo=config.DEBUG,  # Log SQL queries in debug mode
                future=True,
                pool_pre_ping=True,  # Verify connections before using
            )

            # Thiết lập session factory
            session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=self.engine
            )

            # Sử dụng scoped_session để thread-safe
            self.SessionLocal = scoped_session(session_factory)

            # Đăng ký event listeners
            self._setup_event_listeners()

            self._initialized = True
            logger.info("Database initialized successfully")

        except SQLAlchemyError as e:
            logger.error(f"Failed to initialize database: {str(e)}")
            raise

    def _setup_event_listeners(self):
        """Thiết lập các event listeners cho database"""

        @event.listens_for(self.engine, "connect")
        def receive_connect(_dbapi_conn, _connection_record):
            """Event khi tạo connection mới"""
            logger.debug("New database connection established")

        @event.listens_for(self.engine, "checkout")
        def receive_checkout(_dbapi_conn, _connection_record, _connection_proxy):
            """Event khi lấy connection từ pool"""
            logger.debug("Connection checked out from pool")

        @event.listens_for(self.engine, "checkin")
        def receive_checkin(_dbapi_conn, _connection_record):
            """Event khi trả connection về pool"""
            logger.debug("Connection returned to pool")

    def create_all(self):
        """Tạo tất cả các bảng trong database"""
        try:
            Base.metadata.create_all(bind=self.engine)
            logger.info("All database tables created successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to create tables: {str(e)}")
            raise

    def drop_all(self):
        """Xóa tất cả các bảng trong database"""
        try:
            Base.metadata.drop_all(bind=self.engine)
            logger.info("All database tables dropped successfully")
        except SQLAlchemyError as e:
            logger.error(f"Failed to drop tables: {str(e)}")
            raise

    def get_session(self):
        """Lấy database session"""
        if not self._initialized:
            raise RuntimeError("Database not initialized. Call init_db() first")
        return self.SessionLocal()

    def close_session(self):
        """Đóng session hiện tại"""
        if self.SessionLocal:
            self.SessionLocal.remove()

    def dispose(self):
        """Đóng tất cả connections và dispose engine"""
        if self.engine:
            self.SessionLocal.remove()
            self.engine.dispose()
            self._initialized = False
            logger.info("Database connections disposed")

    def check_connection(self) -> bool:
        """Kiểm tra kết nối database"""
        try:
            with self.engine.connect() as conn:
                conn.execute("SELECT 1")
            return True
        except OperationalError:
            logger.error("Database connection check failed")
            return False


# Singleton instance
db = Database()


def get_db() -> Generator:
    """
    Dependency để lấy database session
    Sử dụng trong FastAPI dependency injection
    """
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database session error: {str(e)}")
        raise
    finally:
        session.close()


@contextmanager
def get_db_context():
    """
    Context manager để sử dụng database session

    Usage:
        with get_db_context() as session:
            # Your database operations
            user = session.query(User).first()
    """
    session = db.get_session()
    try:
        yield session
        session.commit()
    except Exception as e:
        session.rollback()
        logger.error(f"Database context error: {str(e)}")
        raise
    finally:
        session.close()


def init_database():
    """Khởi tạo database - gọi khi start application"""
    db.init_db()

    # Tạo tables nếu chưa tồn tại
    if config.ENVIRONMENT == 'development':
        db.create_all()

    # Kiểm tra kết nối
    if not db.check_connection():
        raise RuntimeError("Failed to connect to database")

    logger.info("Database setup completed")


def close_database():
    """Đóng database - gọi khi shutdown application"""
    db.dispose()
    logger.info("Database connections closed")