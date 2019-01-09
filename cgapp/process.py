import subprocess as sp


def runansible():

    # cmd = ['ansible', '--version']
    cmd = ['ping', '-c 5', 'localhost']

    p1 = sp.Popen(cmd, stdout=sp.PIPE)

    for line in p1.stdout:
        output = line.decode("utf-8")
        print(output.rstrip('\n'))
