### Robbie's comment ###

#!/usr/bin/env python
import os
import sys

if __name__ == "__main__":
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "untitled1.settings")

    from django.core.management import execute_from_command_line
#chickenseatdogs
    execute_from_command_line(sys.argv)
### Robbie's comment ###
