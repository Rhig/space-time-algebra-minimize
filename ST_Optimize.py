import csv
import xlsxwriter
#####
# file name constants - CHANGE HERE FOR NEW FILES
#####
FILE_BASE_NAME = 'second_best_sorted_bounded_by_10'
INPUT_FILE_NAME = './inputs/' + FILE_BASE_NAME + '.csv'
OUTPUT_FILE_NAME = './outputs/' + FILE_BASE_NAME + '.xlsx'

#####
# excel formats
#####
workbook = xlsxwriter.Workbook(OUTPUT_FILE_NAME)
step_format = workbook.add_format()
step_format.set_bold()
step_format.set_bg_color('yellow')
step_format.set_border(2)
header_format = workbook.add_format()
header_format.set_bold()
header_format.set_border(1)
header_format.set_bg_color('silver')
cell_format = workbook.add_format()
cell_format.set_border(1)
not_used_format = workbook.add_format()
not_used_format.set_border(1)
not_used_format.set_bg_color('red')
group_colors = ['cyan', 'gray', 'green', 'lime', 'orange', 'pink', 'silver', 'yellow', 'magenta']
group_formats = {}
for color in group_colors:
    group_formats[color] = workbook.add_format()
    group_formats[color].set_border(1)
    group_formats[color].set_bg_color(color)
used_implicant_format = workbook.add_format()
used_implicant_format.set_border(2)
used_implicant_format.set_bg_color('green')
covered_minterm_format = workbook.add_format()
covered_minterm_format.set_border(2)
covered_minterm_format.set_bg_color('red')
#####
# Classes
#####
"""
Input pin of a minterm/implicant.
Has excitatory delay (d_e) and inhibitory delay (d_i)
"""
class Input:
    def __init__(self, d_e, d_i):
        self.__d_e = d_e
        self.__d_i = d_i

    def get_excitatory_delay(self):
        return self.__d_e

    def get_inhibitory_delay(self):
        return self.__d_i

    def set_excitatory_delay(self, d_e):
        self.__d_e = d_e

    def set_inhibitory_delay(self, d_i):
        self.__d_i = d_i

    def __str__(self):
        if self.__d_e == self.__d_i:
            return str(self.__d_i)
        else:
            return str(self.__d_e) + ".." + str(self.__d_i)

"""
Class to describe implicants.
Can also be used to describe minterms.
Can have any number of input pins.
"""
class Implicant:
    def __init__(self, input_delay_pairs, minterm_names):
        self.__minterm_names = sorted(set(minterm_names))  # Assuming that every minterm name is unique
        self.__excitatory_sum = 0
        self.__inhibitory_sum = 0
        self.__used_in_next_step = False
        self.__inputs = []
        for pair in input_delay_pairs:
            self.__inputs.append(Input(pair[0], pair[1]))
            self.__excitatory_sum += pair[0]
            self.__inhibitory_sum += pair[1]

    def use_in_next_step(self):
        self.__used_in_next_step = True

    def is_used_in_next_step(self):
        return self.__used_in_next_step

    """
    Check if this implicant can be merged with another implicant received as input
    """
    def check_if_mergeable(self, other):
        # We only want one diff between implicants to merge them. All other inputs must be identical.
        found_one_diff = False
        for i in range(len(self.__inputs)):
            ex_diff = self.__inputs[i].get_excitatory_delay() - other.__inputs[i].get_excitatory_delay()
            inh_diff = self.__inputs[i].get_inhibitory_delay() - other.__inputs[i].get_inhibitory_delay()
            if ex_diff == 0 and inh_diff == 0:  # If the delays for this input are identical for both implicants,
                continue                        # that's good and we'll just skip
            elif abs(ex_diff) == 1 and abs(inh_diff) == 1 and ex_diff == inh_diff and not found_one_diff:
                found_one_diff = True  # If we found one diff, change boolean flag to true
            else:
                return False  # If we found more than one diff, that means that the implicants cannot be merged.
        return found_one_diff

    def get_group(self):
        if self.__excitatory_sum != self.__inhibitory_sum:
            return str(self.__excitatory_sum)+".."+str(self.__inhibitory_sum)
        else:
            return str(self.__excitatory_sum)

    def get_excitatory_sum(self):
        return self.__excitatory_sum

    def get_inhibitory_sum(self):
        return self.__inhibitory_sum

    def get_implicant_name(self):
        return "".join(self.__minterm_names)

    def get_minterm_list(self):
        return self.__minterm_names

    """
    The method merges this implicant with another implicant, and returns the merged implicant object.
    """
    def merge_implicants(self, other):
        if not self.check_if_mergeable(other):
            return False  # If the implicants cannot be merged, return False
        # Combine the lists of minterm names (The constructor will make sure to get rid of duplicates).
        names = self.__minterm_names + other.__minterm_names
        pairs = []
        # Mark that both implicants were used in the next step
        self.use_in_next_step()
        other.use_in_next_step()
        for i in range(len(self.__inputs)):
            pair = []
            # Take the minimum excitatory delay
            pair.append(min(self.__inputs[i].get_excitatory_delay(), other.__inputs[i].get_excitatory_delay()))
            # Take the maximum inhibitory delay
            pair.append(max(self.__inputs[i].get_inhibitory_delay(), other.__inputs[i].get_inhibitory_delay()))
            pairs.append(pair)
        return Implicant(pairs, names)

    """
    This method writes the implicant as a row in an excel worksheet.
    """
    def write_into_worksheet(self, worksheet, row, col, color_id):
        worksheet.write(row, col, self.get_group(), group_formats[group_colors[color_id % len(group_colors)]])
        worksheet.write(row, col+1, self.get_implicant_name(), cell_format)
        for i in range(len(self.__inputs)):
            worksheet.write(row, col+2+i, str(self.__inputs[i]), cell_format)
        if self.__used_in_next_step:
            worksheet.write(row, col+2+len(self.__inputs), "V", cell_format)
        else:
            worksheet.write(row,col+2+len(self.__inputs), "", not_used_format)

    """
    The string representation of an implicant creates a csv row.
    """
    def __str__(self):
        return_list = [self.get_implicant_name()]
        for i in range(len(self.__inputs)):
            return_list.append(str(self.__inputs[i]))
        if self.__used_in_next_step:
            return_list.append("V")
        else:
            return_list.append("")
        return ",".join(return_list)

"""
This method parses the input csv file and puts the data in the my_dict dictionary
"""
def get_data_from_csv(file_name, my_dict):
    all_minterm_names = []  # Save all of the minterms found in the csv in this list
    with open(file_name) as fh:
        reader = csv.reader(fh)
        for (i, row) in enumerate(reader):  # Assuming that row headers are name,d1,d2,d3,...
            if i == 0:  # First row has headers - keep them separately
                headers = row
                continue
            minterm_name = str(row[0])  # First cell in the row is the minterm name
            all_minterm_names.append(minterm_name)
            delay_pairs = []
            for j in range(1,len(row)):  # all other cells represent input delays
                delay = row[j].split("..")  # Implicant delays are written as "<d_e>..<d_i>"
                if len(delay) == 1:  # If this isn't an implicant delay, then d_e==d_i
                    delay.append(delay[0])  # Create a pair of delays with the same value
                for k in range(len(delay)):  # Covert delays to int.
                    delay[k] = int(delay[k])
                delay_pairs.append(delay)
            implicant = Implicant(delay_pairs, [minterm_name])
            exc = implicant.get_excitatory_sum()
            inh = implicant.get_inhibitory_sum()
            if exc not in my_dict:
                my_dict[exc] = {}
            if inh not in my_dict[exc]:
                my_dict[exc][inh] = {}
            my_dict[exc][inh][implicant.get_implicant_name()] = implicant
    return headers, all_minterm_names


########
# Main #
########
my_implicants_dict = {}  # Define an empty dictionary for implicants
# Parse the input csv file and put the data in the dictionary -
# data structure is my_implicants_dict[<excitatory_delay>][<inhibitory_delay>][<implcant_name>]
headers, all_minterm_names = get_data_from_csv(INPUT_FILE_NAME, my_implicants_dict)
go_to_next_step = True  # This variable is used to tell if we can go to the next step
step = 1
# This while loop does the minimization process and stores the implicants in my_implicants_dict
while (go_to_next_step):
    go_to_next_step = False  # We'll set this back to True if we manage to merge two implicants in this step
    for exc in my_implicants_dict:
        inh = exc + step - 1  # The diff between inh and exc in step i will be i-1
        if inh not in my_implicants_dict[exc]:  # If there is no implicant matching for this step
            continue
        if exc+1 not in my_implicants_dict:  # If there is no implicant from the 1-higher group then we can't merge
            continue
        if inh+1 not in my_implicants_dict[exc+1]:  # If there is no implicant from the 1-higher group then we can't merge
            continue
        for name in my_implicants_dict[exc][inh]:
            for other_name in my_implicants_dict[exc+1][inh+1]:  # You can only merge implicants with other implicants from the 1-higher group
                my_imp = my_implicants_dict[exc][inh][name]
                other_imp = my_implicants_dict[exc+1][inh+1][other_name]
                if my_imp.check_if_mergeable(other_imp):
                    new_imp = my_imp.merge_implicants(other_imp)
                    new_exc = new_imp.get_excitatory_sum()
                    new_inh = new_imp.get_inhibitory_sum()
                    new_name = new_imp.get_implicant_name()
                    if not new_exc in my_implicants_dict:
                        my_implicants_dict[new_exc] = {}
                    if not new_inh  in my_implicants_dict[new_exc]:
                        my_implicants_dict[new_exc][new_inh] = {}
                    my_implicants_dict[new_exc][new_inh][new_name] = new_imp
                    go_to_next_step = True
    step += 1  # move to next step

max_step = step - 1
sorted_keys = sorted(my_implicants_dict.keys())
primary_implicants_chart = {}  # This will store the primary implicants chart
for minterm in all_minterm_names:
    primary_implicants_chart[minterm] = []  # Every minterm will have a list of implicants that cover it
worksheet = workbook.add_worksheet('Minimization process')
col = 0
# Print the minimization process into the first worksheet.
for step in range(max_step):
    row = 0
    worksheet.write(row, col, 'Step '+str(step+1), step_format)
    row += 1
    worksheet.write(row, col, 'Group', header_format)
    for (shift,header) in enumerate(headers):
        worksheet.write(row,col+shift+1, header, header_format)
    worksheet.write(row, col+len(headers)+1, 'used in next step', header_format)
    group_count = 0
    for exc in sorted_keys:
        inh = exc + step
        if inh not in my_implicants_dict[exc]:  # If there is no implicant matching for this step
            continue
        for name in my_implicants_dict[exc][inh]:
            row += 1
            my_imp = my_implicants_dict[exc][inh][name]
            my_imp.write_into_worksheet(worksheet, row, col, group_count)
            if not my_imp.is_used_in_next_step():
                name = my_imp.get_implicant_name()
                for minterm in my_imp.get_minterm_list():
                    primary_implicants_chart[minterm].append(my_imp)
        group_count += 1
    col += len(headers)+3
# Figure out which primary implicants are essential and choose implicants to cover all of the minterms.
worksheet = workbook.add_worksheet('Primary Implicant Chart')
used_implicants = []
covered_minterms = []
# Sort the minterms from the ones with the smallest number of covering implicants to the largest
for minterm in sorted(primary_implicants_chart, key=lambda k: len(primary_implicants_chart[k]), reverse=False):
    if minterm in covered_minterms:
        continue  # If we already covered this minterm, continue
    my_imp = primary_implicants_chart[minterm][0]
    used_implicants.append(my_imp.get_implicant_name())
    for minterm in my_imp.get_minterm_list():
        covered_minterms.append(minterm)
row = 1
col = 0
printed_implicants = []
# Print the primary implicant chart
worksheet.write(0, 0, "Primary implicants chosen: " + ", ".join(used_implicants))
worksheet.write(row, col, "Implicant", header_format)
for minterm in sorted(primary_implicants_chart.keys()):
    col += 1
    worksheet.write(1, col, minterm, header_format)
    for implicant in primary_implicants_chart[minterm]:
        if implicant not in printed_implicants:
            row += 1
            if implicant.get_implicant_name() in used_implicants:
                worksheet.write(row, 0, implicant.get_implicant_name(), used_implicant_format)
            else:
                worksheet.write(row, 0, implicant.get_implicant_name(), header_format)
            printed_implicants.append(implicant)
row = 1
for implicant in printed_implicants:
    col = 0
    row += 1
    used = implicant.get_implicant_name() in used_implicants
    for minterm in sorted(primary_implicants_chart.keys()):
        col += 1
        if implicant in primary_implicants_chart[minterm]:
            worksheet.write(row, col, 'X', covered_minterm_format)
        elif used:
            worksheet.write(row, col, '', used_implicant_format)
        else:
            worksheet.write(row, col, '')
# Third worksheet - print only the chosen implicants
worksheet = workbook.add_worksheet('Chosen Primary Implicants')
row = 0
col = 0
worksheet.write(row, col, 'Group', header_format)
for (shift, header) in enumerate(headers):
    worksheet.write(row, col + shift + 1, header, header_format)
worksheet.write(row, col + len(headers) + 1, 'used in next step', header_format)
for implicant in printed_implicants:
    if implicant.get_implicant_name() in used_implicants:
        row += 1
        implicant.write_into_worksheet(worksheet, row, col, 0)
workbook.close()
print("Used Implicants:" + str(used_implicants))
