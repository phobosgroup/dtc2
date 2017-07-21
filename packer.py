#!/usr/bin/env python

# encode a shell script with base64 and produce a python script that
# will unpack itself and exceute
#
# WARNING: this will not work correctly with "complicated" shell
#          scripts due to the fact that os.system() utilizes
#          /bin/sh. Make sure your scripts function using "sh" rather
#          than "bash." Always test your stuff!

import os
import sys
import base64

# Make sure at least the inputfile was supplied.
if len(sys.argv) == 1:
        print "usage: %s <inputfile> [<outfile>]" % sys.argv[0]
        exit(os.EX_USAGE)

infile = sys.argv[1]

# Set outfile appropriately.
if len(sys.argv) > 2:
        outfile = sys.argv[2]
else:
        outfile = infile + ".py"

# Make sure outfile is writable.
try:
        output_file = open(outfile, "w")
except IOError, err:
        print "Unable to open file %s for writing: %s" % (outfile, err)
        exit(os.EX_USAGE)

# Read infile, encode it.
with open(infile, "rb") as shell_file:
      encoded_string = base64.b64encode(shell_file.read())


# Write encoded data to outfile.
output_template = \
"""#!/usr/bin/env python
import os
import base64
os.system(base64.b64decode('{encoded_string}'))
"""

context = { "encoded_string" : encoded_string }

output_file.write(output_template.format(**context))

# Clean up and exit
output_file.close()
os.chmod(outfile, 0755)
exit(os.EX_OK)
