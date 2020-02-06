"""
Class to modify the generated transform parameter file.

Usual modifications include switching from "short" to "float" when saving the resulting image or changing the order
of (bspline) interpolation from 3 to 0 (for binary labels)

Mainly used to auto-edit transform parameter files generated from registering a pair of images to resample binary
labels, which typically involve a change in the order of interpolation and/or pixel type.

@author: Ishaan Bhat
@email: ishaan@isi.uu.nl
"""


class TransformParameterFileEditor(object):

    def __init__(self,
                 transform_parameter_file_path=None,
                 initial_transform_parameter_file_path=None,
                 output_file_name=None):
        """

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
