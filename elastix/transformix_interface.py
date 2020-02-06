#!/usr/bin/env python
#
# Transformix transforms of images and pointsets. Also used to obtain
# deformation fields, and jacobian matrices and determinants.


from __future__ import division, print_function

import os, shutil
import signal
import subprocess
import logging

logger = logging.getLogger(__name__)


DEFAULT_TRANSFORMIX_PATH = 'transformix'




class TransformixInterface:

    def __init__(self,
                 parameters,
                 transformix_path=DEFAULT_TRANSFORMIX_PATH
                 ):
        self.transformix_path = transformix_path
        self.parameter_file = parameters

    def _execute(self, command, verbose):
        if verbose:
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
                proc = subprocess.Popen(command, stderr=subprocess.PIPE)

            # Register the process to be killed post registration
            # atexit.register(kill_child(proc.pid))
            proc.wait()

        except Exception as ex:
            raise TransformixError('Quitted with error', ex)

        # Check if succesful
        if proc.returncode != 0:
            raise TransformixError(proc.returncode, ' '.join(command))
        if verbose:
            logger.info('Finished command ' + ' '.join(command))

    def deformation_field(self, output_dir=None, verbose=True):

        command = [self.transformix_path,
                   '-tp', self.parameter_file,
                   '-out', output_dir,
                   '-def', 'all'
                   ]

        self._execute(command, verbose)
        after = os.listdir(output_dir)

        # Find out to which file the result was written
        # On Linux, 2D images will result in dcm files, which are empty
        # On Windows, they should result in tiff files
        if 'deformationField.mhd' in after:
            filename = 'deformationField.mhd'
        elif 'deformationField.dcm' in after:
            filename = 'deformationField.dcm'
        elif 'deformationField.tiff' in after:
            filename = 'deformationField.tiff'
        else:
            TransformixError('Deformation field not found in results folder {}'.format(output_dir))
        path = os.path.join(output_dir, filename)
        assert os.path.exists(path)
        return path

    def jacobian_determinant(self, output_dir=None, verbose=True):

        command = [self.transformix_path,
                   '-tp', self.parameter_file,
                   '-out', output_dir,
                   '-jac', 'all'
                   ]

        assert (os.path.exists(output_dir))

        self._execute(command, verbose)
        after = os.listdir(output_dir)

        # Find out to which file the result was written
        # On Linux, 2D images will result in dcm files, which are empty
        # On Windows, they should result in tiff files
        if 'spatialJacobian.mhd' in after:
            filename = 'spatialJacobian.mhd'
        elif 'spatialJacobian.dcm' in after:
            filename = 'spatialJacobian.dcm'
        elif 'spatialJacobian.tiff' in after:
            filename = 'spatialJacobian.tiff'
        elif 'spatialJacobian.nii' in after:
            filename = 'spatialJacobian.nii'
        else:
            TransformixError('Spatial Jacobian determinant not found in results folder {}'.format(output_dir))
        path = os.path.join(output_dir, filename)
        assert os.path.exists(path)
        return path

    def jacobian_matrix(self, output_dir=None, verbose=True):

        command = [self.transformix_path,
                   '-tp', self.parameter_file,
                   '-out', output_dir,
                   '-jacmat', 'all']

        assert (os.path.exists(output_dir))

        self._execute(command, verbose)
        after = os.listdir(output_dir)

        # Find out to which file the result was written
        # On Linux, 2D images will result in dcm files, which are empty
        # On Windows, they should result in tiff files
        if 'fullSpatialJacobian.mhd' in after:
            filename = 'fullSpatialJacobian.mhd'
        elif 'fullSpatialJacobian.dcm' in after:
            filename = 'fullSpatialJacobian.dcm'
        elif 'fullSpatialJacobian.tiff' in after:
            filename = 'fullSpatialJacobian.tiff'
        elif 'fullSpatialJacobian.nii' in after:
            filename = 'fullSpatialJacobian.nii'
        else:
            TransformixError('Spatial Jacobian not found in results folder {}'.format(output_dir))
        path = os.path.join(output_dir, filename)

        return path

    def transform_image(self, image_path, output_dir=None, verbose=True):

        command = [self.transformix_path,
                   '-tp', self.parameter_file,
                   '-out', output_dir,
                   '-in', image_path]

        self._execute(command, verbose)
        after = os.listdir(output_dir)


        # Find out to which file the result was written
        if 'result.tiff' in after:
            filename = 'result.tiff'
        elif 'result.mhd' in after:
            filename = 'result.mhd'
        elif 'result.nii' in after:
            filename = 'result.nii'
        else:
            TransformixError('Transformed image not found in results folder {}'.format(output_dir))
        path = os.path.join(output_dir, filename)
        assert os.path.exists(path)
        return path

    def transform_points(self,
                         pointsfile_path,
                         output_dir=None,
                         verbose=True):
        command = [self.transformix_path,
                   '-tp', self.parameter_file,
                   '-out', output_dir,
                   '-def', pointsfile_path]

        self._execute(command, verbose)
        after = os.listdir(output_dir)

        # Find out to which file the result was written
        if 'outputpoints.txt' in after:
            filename = 'outputpoints.txt'
        elif 'outputpoints.vtk' in after:
            filename = 'outputpoints.vtk'
        else:
            TransformixError('Transformed points not found in results folder {}'.format(output_dir))
        path = os.path.join(output_dir, filename)
        assert os.path.exists(path)
        return path


class TransformixError(Exception):
    """Exception at error in Transformix command."""
    def __init__(self, returncode, command):
        message = ('Transformix crashed with code'
                   ' {0} for command \'{1}\'.').format(returncode, command)
        super(TransformixError, self).__init__(message)
        self.message = message

