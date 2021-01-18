import socket
import time
import sys

IP = 'localhost' #Change this to your desired IP. 
PORT = 54300 #Change to your desired port. This must be the same port as in Principal 1's code (P1).

sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_addr = (IP, PORT)
sock.bind(server_addr)

# for timing out client from inactivity
prev_time = time.perf_counter()

# -------------------- START COVERT CODE -------------------- #

# base delay in ms
base_delay = 50.0
# step-up time between different delays
time_difference = 50.0
# max error margin
error_margin = 10.0

# -------------------- END COVERT CODE -------------------- #

# -------------------- START TESTING VARIABLES -------------------- #

debug = False
if(len(sys.argv) > 1):
    amount = float(sys.argv[1])
    if(amount > 0):
        base_delay = amount

    amount = float(sys.argv[2])
    if(amount > 0):
        time_difference = amount

    amount = float(sys.argv[3])
    if(amount > 0):
        error_margin = amount

    amount = float(sys.argv[4])
    if(amount):
        debug = True

zero = base_delay
one = base_delay + 1 * time_difference
pause = base_delay + 2 * time_difference

# -------------------- END TESTING VARIABLES -------------------- #

# -------------------- START COVERT CODE -------------------- #

# expected length of message
msg_len = 0

# expected length of checksum
check_size = 4

# Keep track of which bit we're on
bit_counter = 0

# size of length bits
len_size = 4

# size bits
size_bits = ""

# bits thus far
curr_bits = ""

checksum_val = ""

wait_for_pause = False

# information gathering vars
set_first = False
first_bit_time = 0
last_bit_time = 0
total_bits = 0
total_bits_good = 0

last_delta = 0  

def handleModulation(last_delta):
    global zero, one, pause, error_margin, curr_bits, error_char, checksum_val, msg_size, bit_counter, len_size, size_bits, msg_len, wait_for_pause, set_first, first_bit_time, last_bit_time, total_bits, total_bits_good
    
    new_bit = False
    new_bit_string = ""

    if (last_delta >= pause - error_margin and last_delta <= pause + error_margin or wait_for_pause):
        # set last bit received time in case transmissions end
        last_bit_time = time.perf_counter()

        # pause, process then reset everything
        if(not wait_for_pause and checkChecksum(curr_bits, checksum_val, msg_len) and len(curr_bits) == msg_len):
            total_bits_good += len(curr_bits) + len(size_bits) + len(checksum_val)
            print(curr_bits, end='', flush=True)
        else:
            # corruption/error message
            print(" *?* ", end='', flush=True)
            pass

        curr_bits = ""
        size_bits = ""
        msg_len = 0
        bit_counter = 0
        checksum_val = ""
        wait_for_pause = False
    elif (last_delta >= zero - error_margin and last_delta <= zero + error_margin):
        new_bit = True
        new_bit_string = "0"
    elif (last_delta >= one - error_margin and last_delta <= one + error_margin):
        new_bit = True
        new_bit_string = "1"
            
    if(new_bit):
        total_bits += 1

        if(not set_first):
            set_first = True
            first_bit_time = time.perf_counter()
        if bit_counter < len_size:
            bit_counter += 1
            size_bits += new_bit_string

            if(bit_counter == len_size):
                msg_len = int(size_bits, 2) + 1

        elif(bit_counter < len_size + msg_len):
            bit_counter += 1

            curr_bits += new_bit_string

        elif(bit_counter < len_size + msg_len + check_size):
            bit_counter += 1

            checksum_val += new_bit_string
            
        else:
            wait_for_pause = True

# UPC
def checkChecksum(curr_bits, checksum_val, msg_len):
    if(len(curr_bits) == 0 or len(checksum_val) != 4):
        return False 
    check_sum = int(checksum_val, 2)
    curr_sum = 0
    check_val = 0
    odd_counter = 0
    even_counter = 1
    if len(curr_bits) % 2 == 0:
        odd_counter = 1
        even_counter = 0
    
    # calculate odd sum
    for i in range(odd_counter, len(curr_bits), 2):
        curr_sum += int(curr_bits[i])
    
    # multiply sum of odd bits by 3
    curr_sum *= 3
    
    # calculate even sum
    for i in range(even_counter, len(curr_bits), 2):
        curr_sum += int(curr_bits[i])

    # find remainder
    remainder = curr_sum % 10

    # if not 0 do 10-remainder
    if (remainder != 0):
        check_val = 10 - remainder

    length_bits = format(msg_len - 1, "b").zfill(4) 
    for bit in length_bits:
        check_val += int(bit)

    if check_val == check_sum:
        return True

    return False

# -------------------- END COVERT CODE -------------------- #

# start listening for P1
sock.listen(1)  

file_handle = open("overtdata.txt", "w")

while True:
    con, client_addr = sock.accept()

    try:
        print('- Received Connection -')

        while True:
            data = con.recv(16)

            if data:
                file_handle.write(data.decode())

                # -------------------- START COVERT CODE -------------------- #
                last_delta = (time.perf_counter() - prev_time) * 1000
                handleModulation(last_delta)
                #print("Handling modulation", last_delta)
                # -------------------- END COVERT CODE -------------------- #

                prev_time = time.perf_counter()

            elif((time.perf_counter() - prev_time) * 1000 > 1000):
                break
    except:
        print(sys.exc_info()[0])
    finally:
        print("\n- Client disconnected/timed out -")

        # -------------------- START TESTING CODE -------------------- #
        if(debug):
            print("---Final statistics---")
            total_time = last_bit_time - first_bit_time
            stats_file = open("stats.csv", "a")
            write_string = str(base_delay) + "," + str(time_difference) + "," + str(error_margin) + "," + str(total_time) + "," + str(total_bits_good) + "," + str(total_bits)
            print(write_string)
            stats_file.write(write_string)
            stats_file.write("\n")
            stats_file.close()
        # -------------------- END TESTING CODE -------------------- #
        
        file_handle.close()
        con.close()
        exit()

