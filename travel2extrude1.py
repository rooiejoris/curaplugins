# Travel2Extrude
#
# special thanks to [he made the script!]:
# www.github.com/neut
# Neut <m.neut@ultimaker.com>

################################################################################
# Imports
################################################################################
import re
import numpy as np
import os.path
import sys
from math import trunc

################################################################################
# Class definitions
################################################################################
class Parser:
    # Define regular expressions
    regex_x = re.compile('X([-+]?\d*\.*\d+)', re.IGNORECASE)
    regex_y = re.compile('Y([-+]?\d*\.*\d+)', re.IGNORECASE)
    regex_z = re.compile('Z([-+]?\d*\.*\d+)', re.IGNORECASE)
    regex_e = re.compile('E([-+]?\d*\.*\d+)', re.IGNORECASE)
    regex_f = re.compile('F([-+]?\d*\.*\d+)', re.IGNORECASE)

    def __init__(self, file_path, e_per_mm=False):
        # Check if we can open the file
        if os.path.isfile(file_path):
            self.file_path = file_path
        else:
            sys.exit('Could not open file')

        self.writer = Writer(file_path + '.new')

        # Describe initial state
        self.state = {'prev_x': 0,
                      'prev_y': 0,
                      'prev_z': 0,
                      'prev_e': 0,
                      'prev_f': 0,
                      'retract': False,
                      'total_line_length': 0,
                      'total_extruded_length': 0}

        self.settings = {'e_per_mm': self.estimate_e_per_mm()}

        # Parse the file
        self.parse()

    def parse(self):
        # Open file and parse contents
        with open(self.file_path) as file:
            # Go line by line
            for line in file:
                # Split line on whitespaces (spaces)
                line_split = line.split()

                # Check for blank lines
                if not line_split:
                    print('[.] Ignoring blank line')
                    # Go to next line
                    continue

                # Check if travel move or extrusion move is detected
                if (line_split[0] == 'G0') or (line_split[0] == 'G1'):
                    # Travel or extrusion move detected. Pass line to parse_move()
                    self.parse_move(line)

                # Reset E axis if required
                # NOTE: Assuming G92 is always followed by E0
                elif (line_split[0] == 'G92'):
                    # Reset prev_e
                    self.state['prev_e'] = 0
                    self.writer.write_line(line)
                    continue

                # Keep track of retract state
                elif (line_split[0] == 'G10'):
                    # Enable retract
                    self.state['retract'] = True
                    self.writer.append_line(line)

                elif (line_split[0] == 'G11'):
                    self.state['retract'] = False
                    self.writer.append_line(line)

                else:
                    # Some other line. Can be copied directly
                    self.writer.append_line(line)

    def parse_move(self, line):
        # Initiate new line
        new_line = 'G1 '

        g92flag = False

        # Perform regular expressions to find xyzef commands
        f = self.regex_f.search(line)
        x = self.regex_x.search(line)
        y = self.regex_y.search(line)
        z = self.regex_z.search(line)
        e = self.regex_e.search(line)

        # Always pass F commands
        if f:
            f_new = np.float(f.group(1))
            new_line += 'F{0} '.format(trunc(f_new))
            self.state['prev_f'] = f_new

        if x:
            x_new = np.float(x.group(1))
            new_line += 'X{0} '.format(x_new)
            xdist = x_new - self.state['prev_x'] 
            self.state['prev_x'] = x_new
        else:
            xdist = 0

        if y:
            y_new = np.float(y.group(1))
            new_line += 'Y{0} '.format(y_new)
            ydist = y_new - self.state['prev_y'] 
            self.state['prev_y'] = y_new
        else:
            ydist = 0
        
        if z:
            z_new = np.float(z.group(1))
            new_line += 'Z{0} '.format(z_new)
            zdist = z_new - self.state['prev_z'] 
            self.state['prev_z'] = z_new
        else:
            zdist = 0
        
        # Compute total cartesian distance (line length)
        segment_length = np.sqrt(xdist**2 + ydist**2 + zdist**2)
        self.state['total_line_length'] += segment_length

        if e:
            # Existing extrude move, don't change, just pass as format x-y-z-e
            e_new = np.float(e.group(1))
            # Track delta_e (for computing total extruded length)
            delta_e = e_new - self.state['prev_e']
            # Update previous e
            self.state['prev_e'] = e_new

        else:
            # Don't perform E-axis extrusion override when retract is enabled
            if self.state['retract'] is True:
                e_new = self.state['prev_e']
                delta_e = 0
            else:
                # Not E, i.e. any move without extrusion. Enforce extrusion here
                delta_e = segment_length*self.settings['e_per_mm'] 
                e_new = self.state['prev_e'] + delta_e

                g92flag = True

        # Update total extruded lenghts:
        self.state['total_extruded_length'] += delta_e

        # Provide new E text
        new_line += 'E{0:0.5f}'.format(e_new)

        # Write line to file
        self.writer.write_line(new_line)

        # Write G92 to line to recognize where stuff happened
        if g92flag is True:
            self.writer.write_line('G92 E{0:0.5f}'.format(self.state['prev_e']))
            g92flag = False

    def estimate_e_per_mm(self):
        # Estimates the e_per_mm variable
        # This opens the file for reading, and parses a part of it (first n lines)

        # number of lines to read
        n = 100
        # initial e_per_mm
        e_per_mm = 0
        # initial values for xye
        prev_x = 0
        prev_y = 0
        prev_e = 0

        # initial values for total line and e-axis length
        sum_e_per_mm = 0
        num_e_per_mm = 0
        avg_e_per_mm = 0

        with open(self.file_path) as f:
            line_number = 0
            for line in f:
                line_number += 1

                # Break if line threshold is hit
                if line_number > n:
                    # print('Average e_per_mm: ', avg_e_per_mm)
                    return avg_e_per_mm

                # Split line on on whitespaces (spaces)
                line_split = line.split()

                # Ignore blank lines
                if not line_split:
                    continue
                
                # Record moves
                if (line_split[0] == 'G0') or (line_split[0] == 'G1'):
                    x = self.regex_x.search(line)
                    y = self.regex_y.search(line)
                    e = self.regex_e.search(line)

                    if x and y:
                        x_new = np.float(x.group(1))
                        y_new = np.float(y.group(1))

                        if e:
                            e_new = np.float(e.group(1))

                            line_length = np.sqrt((x_new - prev_x)**2 + (y_new - prev_y)**2)
                            # Since e is cumulative in the Ggcode file, no need to update this here
                            delta_e = e_new - prev_e

                            # update e_per_mm
                            e_per_mm = delta_e / line_length

                            sum_e_per_mm += e_per_mm
                            num_e_per_mm += 1
                            avg_e_per_mm = sum_e_per_mm/num_e_per_mm
                            # print(e_per_mm, avg_e_per_mm)

                            prev_e = e_new

                        prev_x = x_new
                        prev_y = y_new

                else:
                    # Ignore anything else 
                    continue

            # If file ends before number of lines threshold is hit 
            return e_per_mm

    def set_e_per_mm(self):
        # Placeholder method to manually compute e_per_mm based on flowrate, speed and other parameters
        return 0

    def getSummary(self):
        print('== Summary ==')
        print('Used e_per_mm: ', self.settings['e_per_mm'])
        print('Total line length: ', self.state['total_line_length'])
        print('Total extruded length: ', self.state['total_extruded_length'])

class Writer:
    def __init__(self, file_path):
        # Open file for writing
        self.file = open(file_path, mode='w+')

    def write_line(self, line):
        self.file.write(line + '\n')

    def append_line(self, line):
        self.file.write(line)

    def close(self):
        self.file.close()

################################################################################
# Main 
################################################################################
def main(args):
    parser = Parser(args[1])
    parser.parse()
    parser.getSummary()

################################################################################
# Runtime 
################################################################################
if __name__ == '__main__':
    main(sys.argv)
