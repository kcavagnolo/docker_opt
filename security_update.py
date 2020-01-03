import os
import sys
import time
import logging
import subprocess
import datetime as dt

def main():
    try:
        # avoid using shell=True
        # https://security.openstack.org/guidelines/dg_use-subprocess-securely.html
        args = ['safety', 'check', '--bare', '-r', 'requirements.txt']
        subprocess.check_output(args, shell=False, stderr=subprocess.STDOUT)
    except Exception as e:
        # safety check doesn't exit clean
        pkgs = str(e.output.decode("utf-8")).split()
    for pkg in pkgs:
        args = ['pip', 'install', '--upgrade', pkg]
        subprocess.call(args, shell=False, stderr=subprocess.STDOUT)

if __name__ == '__main__':
    # setup file logger
    script_name = os.path.splitext(os.path.basename(__file__))[0]
    logging.basicConfig(level=logging.DEBUG,
                        format='%(asctime)s %(name)-22s %(levelname)-8s %(message)s',
                        datefmt='%d-%m-%Y %H:%M:%S',
                        filename=script_name + '.log')

    # setup stdout logger
    console = logging.StreamHandler()
    console.setLevel(logging.INFO)
    formatter = logging.Formatter('%(name)-12s: %(levelname)-8s %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

    # run the main program
    logging.info("Starting new run...")
    start_time = time.time()
    main()
    logging.info("Run complete.")
    elapsed = time.time() - start_time
    elapsed = str(dt.timedelta(seconds=elapsed))
    logging.info("--- Run time: {} ---".format(elapsed))
    sys.exit(0)