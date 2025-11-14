"""
Core module - Chứa các cấu hình và tiện ích cơ bản
"""

from app.core.config import get_config, config_by_name
from app.core.database import (
    db,
    get_db,
    get_db_context,
    init_database,
    close_database,
    Base
)


__all__ = [
    # Config
    'get_config',
    'config_by_name',

    # Database
    'db',
    'get_db',
    'get_db_context',
    'init_database',
    'close_database',
    'Base',

]
