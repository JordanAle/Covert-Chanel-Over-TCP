import sys
import time
import socket
import select 

IP = 'localhost' #Change this to your desired IP. 
PORT = 54300 #Change this to your desired port. This must be the same on Principal 2's end (P2)

# time between messages (overt)
sleep_time = 200

# base delay in ms
base_delay = 50.0

# step-up time between different delays
time_difference = 50.0

#establish connection with server
socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
socket.connect((IP,PORT))

# -------------------- START TESTING VARIABLES -------------------- #
debug_terminate_on_finish = 0

# get option args for testing 
if(len(sys.argv) > 3):
    amount = float(sys.argv[2])
    if(amount > 0):
        base_delay = amount

    amount = float(sys.argv[3])
    if(amount > 0):
        time_difference = amount


# termination after next packet sent
if len(sys.argv) > 4:
    amount = int(sys.argv[4])
    if(amount > 0):
        debug_terminate_on_finish = amount

terminate_next = False

# -------------------- END TESTING VARIABLES -------------------- #

# -------------------- START COVERT CODE -------------------- #

def compute_checksum(covert_buffer):
    curr_sum = 0
    check_sum = 0
    odd_counter = 0
    even_counter = 1
    if len(covert_buffer) % 2 == 0:
        odd_counter = 1
        even_counter = 0

    # calculate odd sum
    for i in range(odd_counter, len(covert_buffer), 2):
        curr_sum += int(covert_buffer[i])
    
    # multiply sum of odd bits by 3
    curr_sum *= 3
    
    # calculate even sum
    for i in range(even_counter, len(covert_buffer), 2):
        curr_sum += int(covert_buffer[i])

    # find remainder
    remainder = curr_sum % 10

    # if not 0 do 10-remainder
    if (remainder != 0):
        check_sum = 10 - remainder
    
    length_bits = format(len(covert_buffer) - 1, "b").zfill(4)

    for bit in length_bits:
        check_sum += int(bit)
    
    return f'{check_sum:04b}'

# calculate timing based on configuration
zero = base_delay
one = base_delay + 1 * time_difference
pause = base_delay + 2 * time_difference
standby = base_delay + 3 * time_difference

# overwrite sleep_time standard
sleep_time = standby

covert_msg_size = 11
covert_little_bits = []

# contains buffer for covert bits to send
send_pause = False
current_message_buffer = []

# -------------------- END COVERT CODE -------------------- #

# get overt messages from file
with open(sys.argv[1], 'r') as f:
    overt = f.read()
overt_index = 0

while (overt_index < len(overt)):

    # standard overt messaging
    start = overt_index
    end = min(overt_index+16, len(overt))
    msg = overt[start: end]
    overt_index += 16
    socket.sendall(str.encode(msg))

    if (terminate_next):
        exit()

    # -------------------- START COVERT CODE -------------------- #
    covert_bits = ""
    exists_input = sys.stdin in select.select([sys.stdin], [], [], 0)[0]
    if(exists_input):
        covert_bits = sys.stdin.readline().rstrip()
        length = len(covert_bits)

    if(len(covert_bits) > 0):
        covert_little_bits = covert_little_bits + [covert_bits[i:i+covert_msg_size] for i in range(0, len(covert_bits), covert_msg_size)]
    
    if(not send_pause and debug_terminate_on_finish and len(covert_little_bits) == 0 and len(current_message_buffer) == 0):
        exit()

    if(not send_pause and len(current_message_buffer) == 0 and len(covert_little_bits) > 0):
        msg_body_bits = covert_little_bits.pop(0)
        msg_len_bits = format(len(msg_body_bits) - 1, "b").zfill(4)
        msg_chk_bits = compute_checksum(msg_body_bits)
        
        complete_packet = msg_len_bits + msg_body_bits + msg_chk_bits
        current_message_buffer = [complete_packet[i] for i in range(0, len(complete_packet))]
    
    if(len(current_message_buffer) > 0):
        current_bit = current_message_buffer.pop(0)

        if(int(current_bit)):
            sleep_time = one
        else:
            sleep_time = zero

        if(len(current_message_buffer) == 0):
            send_pause = True
    else:
        if(send_pause):
            sleep_time = pause
            send_pause = False
        else:
            sleep_time = standby
    # -------------------- END COVERT CODE -------------------- #

    time.sleep(sleep_time/1000.0)

print("!!!!!!!!!--------------------- END OF OVERT DATA ---------------------!!!!!!!!!")
socket.close()
