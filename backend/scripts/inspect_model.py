import sys
import os
import pprint
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from src.modules.proposals.models import BusinessProposal
from beanie import Document

print("Attributes:", pprint.pformat([m for m in dir(BusinessProposal) if 'collection' in m or 'get_' in m or 'motor' in m]))
