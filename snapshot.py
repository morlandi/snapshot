"""
(c) 2018 Mario Orlandi, Brainstorm S.n.c.

OpenCV test
"""

__author__ = "Mario Orlandi"
__version__ = "0.0.1"
__copyright__ = "Copyright (c) 2019, Brainstorm S.n.c."
__license__ = "GPL"

import logging
import sys
import argparse
import cv2
import time
import shutil
import signal
import os


logger = logging.getLogger(__name__)


def snapshot(video_capture, show, filename, gray, annotate, logger):

    logger.debug('New snapshot')

    # Capture frame
    ret, frame = video_capture.read()

    if gray:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Display the resulting frame
    if show:
        cv2.imshow('frame', frame)
        cv2.waitKey(1)

    # Save snapshot to file;
    # we create a new temporary file, than move it to the required target,
    # in case some client is still accessing the previous snapshot
    if filename:
        path, name = os.path.split(filename)
        tmp_filename = os.path.join(path, '~' + name)
        cv2.imwrite(tmp_filename, frame)
        logger.debug('tmp snapshot "%s" updated' % tmp_filename)
        # On Windows you might need to remove 'filename' first
        shutil.move(tmp_filename, filename)
        logger.debug('snapshot "%s" updated' % filename)

    if annotate:
        raise Exception("annotate: to be implemented")


def set_logger(verbosity):
    """
    Set logger level based on verbosity option
    """
    handler = logging.StreamHandler(sys.stdout)
    formatter = logging.Formatter('%(asctime)s|%(levelname)s|%(module)s| %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    if verbosity == 0:
        logger.setLevel(logging.WARN)
    elif verbosity == 1:  # default
        logger.setLevel(logging.INFO)
    elif verbosity > 1:
        logger.setLevel(logging.DEBUG)

    # verbosity 3: also enable all logging statements that reach the root logger
    if verbosity > 2:
        logging.getLogger().setLevel(logging.DEBUG)


video_capture = None


def signal_handler(signal, frame):
    global video_capture
    if video_capture:
        video_capture.release()
    cv2.destroyAllWindows()
    sys.exit(0)


def main():

    parser = argparse.ArgumentParser(
        description='Grab snapshot from video camera, and optionally save if to file'
    )
    parser.add_argument('--verbosity', '-v', type=int, default=1,
        help="Verbosity level; 0=minimal output, 1=normal output, 2=verbose output, 3=very verbose output")
    parser.add_argument('--hide', action='store_true', default=False, help="Do not show snapshot in a popup window")
    parser.add_argument('--gray', action='store_true', default=False, help="Convert to gray")
    parser.add_argument('--annotate', action='store_true', default=False, help="Annotate snapshot with timestamp")
    parser.add_argument('--filename', '-f', default=None, help="Optional filename for saving snapshot to disk")
    parser.add_argument('--polling_time', '-t', default=1000, help="Polling time in [ms]; defaults to 1000", type=int)
    args = parser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    set_logger(args.verbosity)

    global video_capture
    video_capture = cv2.VideoCapture(0)
    while True:
        snapshot(video_capture, not args.hide, args.filename, args.gray, args.annotate, logger)
        time.sleep(args.polling_time / 1000.0)


if __name__ == "__main__":
    main()
