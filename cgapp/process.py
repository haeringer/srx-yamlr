import subprocess


def runansible():
    # call(['ansible', '--version'])

    # Set up the command and direct the output to a pipe
    p1 = subprocess.Popen(['ping', '-c 2', 'localhost'],
                          stdout=subprocess.PIPE)

    # Run the command
    output = p1.communicate()[0]

    print(output)
