from sqlalchemy import MetaData
from sqlalchemy.orm import registry

metadata = MetaData()
mapper_registry = registry(metadata=metadata)
Base = mapper_registry.generate_base()
