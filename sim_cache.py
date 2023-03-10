import math
import time
import sys

# read inputs and assign the data to respective variables

# taking input as a string and splitting them with space thereby storing them in a list
iput = input()
inputslist = iput.split()

# assigning variables with data in list
size_of_each_block = int(inputslist[0])
size_of_l1_cache = int(inputslist[1])
associativity_of_l1_cache = int(inputslist[2])
size_of_l2_cache = int(inputslist[3])
associativity_of_l2_cache = int(inputslist[4])
policy_for_replacement = int(inputslist[5])
inclusion_prop = int(inputslist[6])
name_of_trace_file = inputslist[7]

# calculate set index size, tag size, number of sets in cache for both l1 and l2

number_of_sets_l1_cache = size_of_l1_cache // (size_of_each_block * associativity_of_l1_cache)
length_of_set_index_l1 = int(math.log(number_of_sets_l1_cache, 2))

if size_of_l2_cache == 0:
    number_of_sets_l2_cache = 0
    length_of_set_index_l2 = 0
else:
    number_of_sets_l2_cache = size_of_l2_cache // (size_of_each_block * associativity_of_l2_cache)
    length_of_set_index_l2 = int(math.log(number_of_sets_l2_cache, 2))

length_of_block_size = math.log(size_of_each_block, 2)

length_of_tag_l1 = int(32 - length_of_block_size - length_of_set_index_l1)
length_of_tag_l2 = int(32 - length_of_block_size - length_of_set_index_l2)


# read file and store each in 2d list
data_in_file = []
with open(name_of_trace_file, 'r') as textfile:
    for each_line in textfile:
        data_in_file.append(each_line.split())

# check each item and convert to binary values
count_for_while = len(data_in_file) - 1
while count_for_while > -1:
    temp_var = data_in_file[count_for_while][1]
    temp_len = len(temp_var)
    zero_str = ""
    if temp_len < 8:
        for i in range(8 - temp_len):
            zero_str + "0"
        temp_var = zero_str + temp_var
    data_in_file[count_for_while][1] = bin(int(temp_var, 16))[2:].zfill(32)
    count_for_while -= 1

# split each item and just keep the tag value and set values in index 0 and 1 and also 32 binary value
for i in range(len(data_in_file)):
    temp_bin_val = data_in_file[i][1]
    temp_tag_val = temp_bin_val[0:length_of_tag_l1]
    temp_set_val = temp_bin_val[length_of_tag_l1:(length_of_tag_l1 + length_of_set_index_l1)]
    data_in_file[i][1] = temp_tag_val
    if len(temp_set_val) <= 0:
        data_in_file[i].append(0)
    else:
        data_in_file[i].append(int(temp_set_val, 2))
    data_in_file[i].append(temp_bin_val)
    data_in_file[i].append(temp_bin_val[0:(length_of_tag_l1 + length_of_set_index_l1)])

# create an empty list for cache with empty sets appended as per the number of sets in l1 cache
l1_cache = []
for i in range(number_of_sets_l1_cache):
    l1_cache.append([])

# create an empty l2 cache
l2_cache = []
for i in range(number_of_sets_l2_cache):
    l2_cache.append([])


l1_read_count = 0
l1_write_count = 0
l1_read_miss = 0
l1_write_miss = 0
l1_writebacks = 0
l2_read_count = [0]
l2_write_count = [0]
l2_read_miss = [0]
l2_write_miss = [0]
l2_write_backs = [0]


def find_element(tagname, listname):
    return any(tagname in sub for sub in listname)


def find_index(tagname, listname):
    for ind in range(len(listname)):
        if tagname in listname[ind]:
            return ind


def check_lru(set):
    x = set[0][2]
    inde = 0
    for i in range(len(set)):
        if set[i][2] < x:
            x = set[i][2]
            inde = i
    return inde


# find tag, set index from 32 bit value
def find_l2_items(item):
    temp_tag_val = item[0:length_of_tag_l2]
    temp_set_val = item[length_of_tag_l2:(length_of_tag_l2 + length_of_set_index_l2)]
    temp_set_val = int(temp_set_val, 2)
    return temp_tag_val, temp_set_val


l1_invalid_count = [0]


# inclusion property implementing function
def l1_remove_element(val):
    temp_tag_val = val[0:length_of_tag_l1]
    temp_set_val = val[length_of_tag_l1:(length_of_tag_l1 + length_of_set_index_l1)]
    temp_set_val = int(temp_set_val, 2)
    for i in range(len(l1_cache[temp_set_val])):
        if l1_cache[temp_set_val][i][3] == val:
            x = l1_cache[temp_set_val].pop(i)
            if x[1] == 1:
                l1_invalid_count[0] += 1
            break
    pass


# l2 cache function for lru
def l2_lru(element, operation):
    tag_value, set_number = find_l2_items(element)
    if operation == 'r':
        l2_read_count[0] += 1
        if find_element(tag_value, l2_cache[set_number]):
            index_of_tag = find_index(tag_value, l2_cache[set_number])
            l2_cache[set_number][index_of_tag][2] = time.time() * 100000000000
            time.sleep(0.00000000001)
        else:
            l2_read_miss[0] += 1
            if len(l2_cache[set_number]) < associativity_of_l2_cache:
                l2_cache[set_number].append([tag_value, 0, time.time() * 100000000000, element])
                time.sleep(0.00000000001)
            else:
                lru_index = check_lru(l2_cache[set_number])
                if l2_cache[set_number][lru_index][1] == 1:
                    l2_write_backs[0] += 1
                l1_removal = l2_cache[set_number][lru_index][3]
                l2_cache[set_number][lru_index] = [tag_value, 0, time.time() * 100000000000, element]
                time.sleep(0.00000000001)
                if inclusion_prop == 1:
                    l1_remove_element(l1_removal)
    else:
        l2_write_count[0] += 1
        if find_element(tag_value, l2_cache[set_number]):
            index_of_tag = find_index(tag_value, l2_cache[set_number])
            l2_cache[set_number][index_of_tag][2] = time.time() * 100000000000
            time.sleep(0.00000000001)
            l2_cache[set_number][index_of_tag][1] = 1
        else:
            l2_write_miss[0] += 1
            if len(l2_cache[set_number]) < associativity_of_l2_cache:
                l2_cache[set_number].append([tag_value, 1, time.time() * 100000000000, element])
                time.sleep(0.00000000001)
            else:
                lru_index = check_lru(l2_cache[set_number])
                if l2_cache[set_number][lru_index][1] == 1:
                    l2_write_backs[0] += 1
                l1_removal = l2_cache[set_number][lru_index][3]
                l2_cache[set_number][lru_index] = [tag_value, 1, time.time() * 100000000000, element]
                time.sleep(0.00000000001)
                if inclusion_prop == 1:
                    l1_remove_element(l1_removal)


# l2 cache function for fifo
def l2_fifo(element, operation):
    tag_value, set_number = find_l2_items(element)
    if operation == 'r':
        l2_read_count[0] += 1
        if find_element(tag_value, l2_cache[set_number]):
            pass
        else:
            l2_read_miss[0] += 1
            if len(l2_cache[set_number]) < associativity_of_l2_cache:
                l2_cache[set_number].append([tag_value, 0, time.time() * 100000000000, element])
                time.sleep(0.00000000001)
            else:
                lru_index = check_lru(l2_cache[set_number])
                if l2_cache[set_number][lru_index][1] == 1:
                    l2_write_backs[0] += 1
                l1_removal = l2_cache[set_number][lru_index][3]
                l2_cache[set_number][lru_index] = [tag_value, 0, time.time() * 100000000000, element]
                time.sleep(0.00000000001)
                if inclusion_prop == 1:
                    l1_remove_element(l1_removal)
    else:
        l2_write_count[0] += 1
        if find_element(tag_value, l2_cache[set_number]):
            index_of_tag = find_index(tag_value, l2_cache[set_number])
            l2_cache[set_number][index_of_tag][2] = time.time() * 100000000000
            time.sleep(0.00000000001)
            l2_cache[set_number][index_of_tag][1] = 1
        else:
            l2_write_miss[0] += 1
            if len(l2_cache[set_number]) < associativity_of_l2_cache:
                l2_cache[set_number].append([tag_value, 1, time.time() * 100000000000, element])
                time.sleep(0.00000000001)
            else:
                lru_index = check_lru(l2_cache[set_number])
                if l2_cache[set_number][lru_index][1] == 1:
                    l2_write_backs[0] += 1
                l1_removal = l2_cache[set_number][lru_index][3]
                l2_cache[set_number][lru_index] = [tag_value, 1, time.time() * 100000000000, element]
                time.sleep(0.00000000001)
                if inclusion_prop == 1:
                    l1_remove_element(l1_removal)


# l1 cache implementation for LRU
if policy_for_replacement == 0:
    for element in data_in_file:
        set_number = element[2]
        tag_value = element[1]
        bit_value = element[3]
        if element[0] == 'r':
            l1_read_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                index_of_tag = find_index(tag_value, l1_cache[set_number])
                l1_cache[set_number][index_of_tag][2] = time.time() * 100000000000
                time.sleep(0.00000000001)
            else:
                l1_read_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, 0, time.time() * 100000000000, bit_value])
                    time.sleep(0.00000000001)
                else:
                    lru_index = check_lru(l1_cache[set_number])
                    if l1_cache[set_number][lru_index][1] == 1:
                        l1_writebacks += 1
                        if size_of_l2_cache != 0:
                            l2_lru(l1_cache[set_number][lru_index][3], 'w')
                    l1_cache[set_number][lru_index] = [tag_value, 0, time.time() * 100000000000, bit_value]
                    time.sleep(0.00000000001)
                if size_of_l2_cache != 0:
                    l2_lru(bit_value, 'r')
        else:
            l1_write_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                index_of_tag = find_index(tag_value, l1_cache[set_number])
                l1_cache[set_number][index_of_tag][2] = time.time() * 100000000000
                time.sleep(0.00000000001)
                l1_cache[set_number][index_of_tag][1] = 1
            else:
                l1_write_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, 1, time.time() * 100000000000, bit_value])
                    time.sleep(0.00000000001)
                else:
                    lru_index = check_lru(l1_cache[set_number])
                    if l1_cache[set_number][lru_index][1] == 1:
                        l1_writebacks += 1
                        if size_of_l2_cache != 0:
                            l2_lru(l1_cache[set_number][lru_index][3], 'w')
                    l1_cache[set_number][lru_index] = [tag_value, 1, time.time() * 100000000000, bit_value]
                    time.sleep(0.00000000001)
                if size_of_l2_cache != 0:
                    l2_lru(bit_value, 'r')

# l1 cache fifo implementation
if policy_for_replacement == 1:
    for element in data_in_file:
        set_number = element[2]
        tag_value = element[1]
        bit_value = element[3]
        if element[0] == 'r':
            l1_read_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                continue
            else:
                l1_read_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, 0, time.time() * 100000000000, bit_value])
                    time.sleep(0.00000000001)
                else:
                    lru_index = check_lru(l1_cache[set_number])
                    if l1_cache[set_number][lru_index][1] == 1:
                        l1_writebacks += 1
                        if size_of_l2_cache != 0:
                            l2_fifo(l1_cache[set_number][lru_index][3], 'w')
                    l1_cache[set_number][lru_index] = [tag_value, 0, time.time() * 100000000000, bit_value]
                    time.sleep(0.00000000001)
                if size_of_l2_cache != 0:
                    l2_lru(bit_value, 'r')
        else:
            l1_write_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                index_of_tag = find_index(tag_value, l1_cache[set_number])
                l1_cache[set_number][index_of_tag][1] = 1
            else:
                l1_write_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, 1, time.time() * 100000000000, bit_value])
                    time.sleep(0.00000000001)
                else:
                    lru_index = check_lru(l1_cache[set_number])
                    if l1_cache[set_number][lru_index][1] == 1:
                        l1_writebacks += 1
                        if size_of_l2_cache != 0:
                            l2_fifo(l1_cache[set_number][lru_index][3], 'w')
                    l1_cache[set_number][lru_index] = [tag_value, 1, time.time() * 100000000000, bit_value]
                    time.sleep(0.00000000001)
                if size_of_l2_cache != 0:
                    l2_fifo(bit_value, 'r')

optimal_dic = {}
# loading the file into a dictionary with future occurrences
for i in range(len(data_in_file)):
    if data_in_file[i][4] in optimal_dic.keys():
        optimal_dic[data_in_file[i][4]].append(i)
    else:
        optimal_dic[data_in_file[i][4]] = []

# optimal implementation for L1
if policy_for_replacement == 2:
    for item in data_in_file:
        set_number = item[2]
        tag_value = item[1]
        bit_value = item[3]
        key_value = item[4]
        if len(optimal_dic[key_value]) == 0:
            dic_len = 1000000000  # 9 zeros
        else:
            dic_len = optimal_dic[key_value][0]
        if item[0] == 'r':
            l1_read_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                index_of_tag = find_index(tag_value, l1_cache[set_number])
                l1_cache[set_number][index_of_tag][1] = dic_len
            else:
                l1_read_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, dic_len, 0])
                else:
                    maximum = -1
                    maximum_index = 0;
                    for i in range(len(l1_cache[set_number])):
                        if l1_cache[set_number][i][1] > maximum:
                            maximum = l1_cache[set_number][i][1]
                            maximum_index = i
                    if l1_cache[set_number][maximum_index][2] == 1:
                        l1_writebacks += 1
                    l1_cache[set_number][maximum_index] = [tag_value, dic_len, 0]
        else:
            l1_write_count += 1
            if find_element(tag_value, l1_cache[set_number]):
                index_of_tag = find_index(tag_value, l1_cache[set_number])
                l1_cache[set_number][index_of_tag][1] = dic_len
                l1_cache[set_number][index_of_tag][2] = 1
            else:
                l1_write_miss += 1
                if len(l1_cache[set_number]) < associativity_of_l1_cache:
                    l1_cache[set_number].append([tag_value, dic_len, 1])
                else:
                    maximum = -1
                    maximum_index = 0;
                    for i in range(len(l1_cache[set_number])):
                        if l1_cache[set_number][i][1] > maximum:
                            maximum = l1_cache[set_number][i][1]
                            maximum_index = i
                    if l1_cache[set_number][maximum_index][2] == 1:
                        l1_writebacks += 1
                    l1_cache[set_number][maximum_index] = [tag_value, dic_len, 1]
        if len(optimal_dic[key_value]) > 0:
            optimal_dic[key_value].pop(0)

print("===== Simulator configuration =====")
print("BLOCKSIZE:             ", size_of_each_block)
print("L1_SIZE:               ", size_of_l1_cache)
print("L1_ASSOC:              ", associativity_of_l1_cache)
print("L2_SIZE:               ", size_of_l2_cache)
print("L2_ASSOC:              ", associativity_of_l2_cache)
if policy_for_replacement == 0:
    print("REPLACEMENT POLICY:    ", "LRU")
if policy_for_replacement == 1:
    print("REPLACEMENT POLICY:    ", "FIFO")
if policy_for_replacement == 2:
    print("REPLACEMENT POLICY:    ", "optimal")
if inclusion_prop == 0:
    print("INCLUSION PROPERTY:    ", "non-inclusive")
if inclusion_prop == 1:
    print("INCLUSION PROPERTY:    ", "inclusive")
print("trace_file:            ", name_of_trace_file)

print("===== L1 contents =====")
for i in range(len(l1_cache)):
    if i > 9:
        s = "Set     " + str(i) + ":      "
    else:
        s = "Set     " + str(i) + ":       "
    for j in l1_cache[i]:
        s += hex(int(j[0], 2))[2:]
        if j[1] == 1:
            s += " D"
            s += "    "
        else:
            s += "      "
    print(s)

if l2_read_count[0] != 0:
    print("===== L2 contents =====")
    for i in range(len(l2_cache)):
        if i > 9:
            s = "Set     " + str(i) + ":      "
        else:
            s = "Set     " + str(i) + ":       "
        for j in l2_cache[i]:
            s += hex(int(j[0], 2))[2:]
            if j[1] == 1:
                s += " D"
                s += "    "
            else:
                s += "      "
        print(s)

print("===== Simulation results (raw) =====")
print("a. number of L1 reads:        ", l1_read_count)
print("b. number of L1 read misses:  ", l1_read_miss)
print("c. number of L1 writes:       ", l1_write_count)
print("d. number of L1 write misses: ", l1_write_miss)
print("e. L1 miss rate:              ", (l1_read_miss + l1_write_miss)/(l1_read_count + l1_write_count))
print("f. number of L1 writebacks:   ", l1_writebacks)
print("g. number of L2 reads:        ", l2_read_count[0])
print("h. number of L2 read misses:  ", l2_read_miss[0])
print("i. number of L2 writes:       ", l2_write_count[0])
print("j. number of L2 write misses: ", l2_write_miss[0])
if l2_read_count[0] != 0:
    print("k. L2 miss rate:              ", l2_read_miss[0]/l2_read_count[0])
else:
    print("k. L2 miss rate:              ", 0)
print("l. number of L2 writebacks:   ", l2_write_backs[0])
memory_traffic = 0
if l2_read_count != 0:
    memory_traffic = l1_read_miss + l1_write_miss + l1_writebacks
else:
    memory_traffic = l2_read_miss[0] + l2_write_miss[0] + l2_write_backs[0] + l1_invalid_count[0]
print("m. total memory traffic:      ", memory_traffic)
