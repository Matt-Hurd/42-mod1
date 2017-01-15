import sys
import re

def parse_file(inputfile):
    try:
        with open(inputfile, 'r') as f:
            points = []
            for line in f.readlines():
                group = []
                for point in line.strip().split(' '):
                    m = re.match("^\(([0-9]+),([0-9]+),([0-9]+)\)$", point)
                    if m:
                        group.append((int(m.group(1)),int(m.group(2)),int(m.group(3))))
                    else:
                        print "Invalid input file"
                        return None
                points.append(group)
            return points
    except IOError as e:
        print "Invalid input file"
        exit()
