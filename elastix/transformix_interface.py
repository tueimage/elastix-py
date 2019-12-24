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


class TransformParameterFileEditor(object):

    def __init__(self,
                 transform_parameter_file_path=None,
                 initial_transform_parameter_file_path=None,
                 output_file_name=None):
        """
        Class to modify the generate transform parameter file. Usual modifications include
        switching from "short" to "float" when saving the resulting image or changing the order
        of (bspline) interpolation from 3 to 0 (for binary labels)

        Args:
            transform_parameter_file_path: (str) Path to transform parameter file
            initial_transform_parameter_file_path: (str) Usually registration is done in a cascaded fashion (rigid,
                                                         followed by deformable). The transform parameters files therefore
                                                         contain a pointer to a previous transformation (if any)
            output_file_name: (str) Filename for the output transform parameter file

        """
        self.transform_parameter_file_path = transform_parameter_file_path
        self.initial_transform_parameter_file = initial_transform_parameter_file_path
        self.output_file_name = output_file_name
        self.params_dict = {}

    def _get_lines(self):
        f = open(self.transform_parameter_file_path, 'r')
        lines = f.readlines()
        lines = [line.strip() for line in lines]
        return lines

    def _parse_file(self):
        """
        Read and parse the file and store the named parameters and their values
        in the params_dict
        """
        lines = self._get_lines()
        for line in lines:
            if len(line) > 2:
                string_tuple = line.split(' ')
                if line[0] == '/' and line[1] == '/':  # Comment-line, skip it
                    continue
                elif line[0] == '(' and line[-1] == ')':  # Valid line
                    self.params_dict[string_tuple[0][1:]] = line[len(string_tuple[0]):-1]
            else:
                continue

    def _edit_parameters(self):
        """
        Function edit the values of transform parameters.
        Currently only supports parameter changes to support resampling of
        binary labels
        FIXME: Custom parameter edits
        FIXME: Protect certain transform parameters from editing (eg: transform parameters/ dimension/ grid etc.)

        """
        assert (len(self.params_dict) > 0)
        if self.initial_transform_parameter_file is not None:
            self.params_dict['InitialTransformParametersFileName'] = ' ' + self.initial_transform_parameter_file

        # Result image format
        self.params_dict['ResultImagePixelType'] = ' "' + 'float' + '"'
        # Interpolation order to 0 for binary labels
        self.params_dict['FinalBSpineInterpolatorOrder'] = ' 0'

    def _writer_parameters_to_file(self):
        """
        Write updated parameter dict to file in the correct format

        """
        parameter_file_string = ''
        for key, value in self.params_dict.items():
            parameter_file_string += '('
            parameter_file_string += key
            parameter_file_string += value
            parameter_file_string += ')'
            parameter_file_string += '\n'

        result_file = open(self.output_file_name, 'w')
        result_file.write(parameter_file_string)
        result_file.close()

    def modify_transform_parameter_file(self):
        self._parse_file()
        self._edit_parameters()
        self._writer_parameters_to_file()


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

        if os.path.exists(output_dir) is True:
            shutil.rmtree(output_dir)

        os.makedirs(output_dir)

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

        if os.path.exists(output_dir) is True:
            shutil.rmtree(output_dir)

        os.makedirs(output_dir)

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

