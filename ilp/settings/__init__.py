from .base import *

try:
    from .local_settings import *
except ImportError:
    pass

try:
    from .ci_settings import *
except ImportError:
    pass
    
try:
    from .prod_settings import *
except ImportError:
    pass
