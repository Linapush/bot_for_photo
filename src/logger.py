import logging
from contextvars import ContextVar

import yaml
# yaml — «дружественный» формат сериализации данных, концептуально близкий к языкам разметки, но ориентированный на удобство ввода-вывода типичных структур данных многих языков программирования

with open('conf/logging.conf.yml', 'r') as f:
    LOGGING_CONFIG = yaml.full_load(f)

# запись в консоль с correlation_id
class ConsoleFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        try:
            correlation_id = correlation_id_ctx.get()
            return '[%s] %s' % (correlation_id, super().format(record))
        except LookupError:
            return super().format(record)


correlation_id_ctx: ContextVar[str] = ContextVar('correlation_id_ctx')
# logging.config.dictConfig(LOGGING_CONFIG)
logger = logging.getLogger('bot')