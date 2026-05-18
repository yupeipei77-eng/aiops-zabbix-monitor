from sqlalchemy import BigInteger, Integer, JSON
from sqlalchemy.dialects.postgresql import JSONB


JSON_FIELD = JSON().with_variant(JSONB, "postgresql")
BIGINT_PK = BigInteger().with_variant(Integer, "sqlite")
