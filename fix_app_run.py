import fileinput
import sys

# Replace debug=True with debug=False in the app.run line
for line in fileinput.input('app.py', inplace=True):
    if 'app.run(debug=True' in line:
        line = line.replace('debug=True', 'debug=False')
    sys.stdout.write(line)

print("Successfully disabled debug mode in app.py!")
