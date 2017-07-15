#!/usr/bin/python
# encode a shell script with base64 and produce a python script that will unpack itself
# and exceute

import os
import sys
import base64

if len(sys.argv) != 2:
        print "usage: %s inputfile" % sys.argv[0]

filename = sys.argv[1]

with open(filename, "rb") as shell_file:
      encoded_string = base64.b64encode(shell_file.read())

output_file = open(filename + ".py", "w")
output_file.write("#!/usr/bin/python\n");
output_file.write("import os,base64;os.system(base64.b64decode('")
output_file.write(encoded_string)
output_file.write("'))\n")
output_file.close()

os.system("chmod 755 %s.py" % filename)
