# Running P1 and P2 
P1 and P2 can be run with minimal command line arguments or with additional configuration options. We will first discuss execution with default configuration. P2 **MUST** be started before P1 because it is the socket host.

## Running P1 with default options
`python3 P1.py <overt_data>` where `<overt_data>` contains ASCII text

## Running P1 with custom configuration
Running the custom configuration requires ALL additional arguments, with the exception of the `<testing>` flag, which is optional. The `<testing>` flag will cause P1 to terminate when the sending buffer has been sent and no new bytes are waiting at standard input (used for testing purposes)
`python3 P1.py <overt_data> <base_delay> <time_step> <testing = 0/1>`

## Running P2 with default options
`python3 P2.py`

## Running P2 with custom configuration
Running the custom configuration requires ALL additional arguments. The `<debug>` flag will print and save statistics information to be used during testing.
`python3 P2.py <base_delay> <time_step> <error_margin> <debug = 0/1>` 

## Custom timing argument explanations
`<base_delay>` is the first type of delay for information transfer (assigned to 0)
`<time_step>` is the amount of time separating one informational delay from the next. base_delay + x * time_step for the number of distinct information-carrying delay types x generates the delays to signal information
`<error_margin>` describes how far from the received delay a value can be to be considered as part of the closest information-carrying delay type

## Sending Covert Data
Covert data may be sent in one of two ways. The first method creates a stream for cover data. After begining both processes, simply type or paste the raw binary data to send into the command line of P1, then press enter. This will send the data to the second principal and allow additional command line data inputs. The second method does not allow for additional input to be sent after the first message, but allows for file references. For this method as you start P1, pipe the file containing covert binary data into P1 as follows: 
`cat [covert_data_file_text_file] | python3 P1.py [overt data text file]` or `echo [raw binary data] | python3 P1.py [overt data text file]`. This will send data from the covert file until either 1) all overt data is sent and the connection to P2 is closed or 2) all covert data is sent (at which point the overt data will continue sending until its end is reached).

### This project is currently directed at local communication, but by running P1 and P2 on separate devices (after making the few easy edits to IP and PORT as referenced in P1 and P2 code comments), the project easily pivots for network usage. The TCP packet delay rates that allow the transmission of the covert data are customizable and may be fitted for individual networks and use cases to decrease errors (at the cost of throughput) or increase data throughput (at the cost of message accuracy).

### For additional project information, see the repository's about page. There, you can find information about the authors and the ideas behind the project.
