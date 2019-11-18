#!/usr/bin/env python
#
# Elastix registration of images, images with masks, images with pointsets,
# a images with masks and pointsets.
#
# The Elastix class has one method called `register` that can do all
# of the above.


from __future__ import division, print_function

import os
import signal
import subprocess
import logging

logger = logging.getLogger(__name__)
logger.setLevel(0)


DEFAULT_ELASTIX_PATH = 'elastix'


class ElastixInterface:

    def __init__(self,
                 elastix_path=DEFAULT_ELASTIX_PATH
                 ):
        self.elastix_path = elastix_path

    def _command(self, output_dir, parameter_files,
                 fixed_image, moving_image,
                 fixed_points, moving_points,
                 fixed_mask, moving_mask,
                 initial_transform
                 ):

        command = [self.elastix_path]

        if fixed_image and moving_image:
            command += ['-f', fixed_image,
                       '-m', moving_image]

        if fixed_points and moving_points:
            command += ['-fp', fixed_points,
                        '-mp', moving_points]
        if fixed_mask:
            command += ['-fMask', fixed_mask]
        if moving_mask:
            command += ['-mMask', moving_mask]

        if initial_transform:
            command += ['-t0', initial_transform]

        for parameter_file in parameter_files:
            command += ['-p', parameter_file]

        command += ['-out', output_dir]

        return command

    def _execute(self, command, verbose):
        logger.info('Started command ' + ' '.join(command))
        err = ''

        # Function to cleanly kill all processes post registration
        def kill_child(child_pid):  # Sorry if that sounds cruel
            if child_pid is None:
                pass
            else:
                def kill_function():
                    try:
                        os.kill(child_pid, signal.SIGTERM)
                    except OSError:
                        logger.info('Child process {}'
                                    ' already killed.'.format(child_pid))
                    return kill_function

        # Actually run the command
        try:
            if not verbose:
                DEVNULL = open(os.devnull, 'wb')
                proc = subprocess.Popen(command,
                                        stderr=subprocess.PIPE,
                                        stdout=DEVNULL)
                out, err = proc.communicate()
            else:
                logger.info(command)
                print(' '.join(command))
                proc = subprocess.Popen(command,
                                        stderr=subprocess.PIPE)

            # Register the process to be killed post registration
            # atexit.register(kill_child(proc.pid))
            proc.wait()

        except Exception as ex:
            raise ElastixError('Quit with error', ex)

        # Check if succesful
        if proc.returncode != 0:
            raise ElastixError(proc.returncode, ' '.join(command))
        logger.info('Finished command ' + ' '.join(command))

    def register(self,
                 parameters,
                 fixed_image=None,
                 moving_image=None,
                 fixed_mask=None,
                 moving_mask=None,
                 fixed_points=None,
                 moving_points=None,
                 initial_transform=None,
                 output_dir=None,
                 verbose=True
                 ):

        assert os.path.exists(output_dir)
        assert type(parameters) is list
        for prm in parameters:
            assert type(prm) is str

        self.output_dir = output_dir

        cmd = self._command(output_dir,
                            parameters,
                            fixed_image, moving_image,
                            fixed_points, moving_points,
                            fixed_mask, moving_mask,
                            initial_transform)
        self._execute(cmd, verbose)


class ElastixError(Exception):
    """Exception at error in Elastix command."""
    def __init__(self, returncode, command):
        message = ('Elastix crashed with code'
                   ' {0} for command \'{1}\'.').format(returncode, command)
        super(ElastixError, self).__init__(message)
        self.message = message

