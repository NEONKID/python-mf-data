from datetime import datetime
from typing import List


def process_revision_directives(context, revision, directives: List):
    script = directives[0]
    script.rev_id = datetime.now().strftime("%y%m%d%H%M%S")
