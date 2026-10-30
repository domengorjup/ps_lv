import pyvisa

import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SDG1X:
    def __init__(self, resource=None):
        """
        SDG1X class to control Siglent SDG1X series function generator.
        This class provides methods to set waveform parameters and control the output.
        It uses the PyVISA library to communicate with the instrument via VISA.

        Parameters:
            resource (str): VISA resource string for the instrument. 
            If None, it will use the first available SDG1X resource.
            Defaults to None.
        """

        self.rm = pyvisa.ResourceManager()

        if resource is None:
            self.resource = self.valid_resources[0]
        else:
            self.resource = resource

        idn = self.connect()
        logging.info(f'Connected to {idn}')

    @property
    def valid_resources(self):
        """
        Lists all available SDG1X resources.

        Returns:
            list: List of available SDG1X resources.
        """
        self._valid_resources = [res for res in self.rm.list_resources() if 'SDG1X' in res]
        return self._valid_resources
    
    def connect(self):
        """
        Connects to the specified instrument resource.

        Parameters:
            resource (str): VISA resource string for the instrument.
            If None, it will use the first available SDG1X resource.
            Defaults to None.
        """
        self.instrument = self.rm.open_resource(self.resource)
        return self.instrument.query('*IDN?')

    def disconnect(self):
        """
        Closes the connection to the instrument.
        """
        self.instrument.close()

    def validate_waveform_parameters(self, parameters):
        """
        Validates the waveform parameters.

        Parameters:
            parameters (dict): Dictionary containing waveform parameters.

        Returns:
            bool: True if all parameters are valid, raises AssertionError otherwise.
        """
        assert parameters['channel'] in [1, 2, None]
        assert parameters['frequency'] is None or parameters['frequency'] > 0
        assert parameters['amplitude'] is None or parameters['amplitude'] > 0
        assert parameters['offset'] is None or parameters['offset'] >= 0
        if parameters['offset'] is not None and parameters['amplitude'] is not None:
            assert parameters['offset'] + parameters['amplitude'] / 2 <= 5
            assert parameters['offset'] - parameters['amplitude'] / 2 >= 0
        assert parameters['phase'] is None or 0 <= parameters['phase'] <= 360
        assert parameters['waveform'] in ['SINE', 'SQUARE', 'PULSE', 'RAMP', 'PRBS', 'NOISE', 'ARB', 'DC', None]
        return True
        

    def set_basic_wave(self, channel, frequency=None, amplitude=None, offset=2.5, phase=None, waveform=None, output=True):
        """
        Sets the basic waveform parameters for the specified channel.

        Parameters:
            channel (int): Channel number (1 or 2).
            frequency (float): Frequency in Hz. Default is None.
            amplitude (float): Amplitude in Vpp. Default is None.
            offset (float): Offset in V. Default is 2.5V.
            phase (float): Phase in degrees. Default is None.
            waveform (str): Waveform type. Default is None.
            output (bool): If True, the output is turned on. 
                If False, the output is turned off. Default is True.                                                

        Returns:
            str: Response from the instrument after setting the parameters.
        """ 

        parameters_dict = {
            'channel': channel,
            'frequency': frequency, # [Hz]
            'amplitude': amplitude, # [Vpp]
            'offset': offset,
            'phase': phase, # [degrees]
            'waveform': waveform,
        }

        # validate input channel parameters
        self.validate_waveform_parameters(parameters_dict)
        
        # construct command string
        COMMAND = f'C{channel:d}' + ':BSWV {parameter:s},{value:s}'

        if frequency is not None:
            freq_command = COMMAND.format(parameter='FRQ', value=str(frequency)) 
            logging.debug(f'Executing: {freq_command}')
            self.instrument.write(freq_command) 

        if amplitude is not None:
            amp_command = COMMAND.format(parameter='AMP', value=str(amplitude))
            logging.debug(f'Executing: {amp_command}')
            self.instrument.write(amp_command)

        if offset is not None:
            offset_command = COMMAND.format(parameter='OFST', value=str(offset))
            logging.debug(f'Executing: {offset_command}')
            self.instrument.write(offset_command)

        if phase is not None:
            phase_command = COMMAND.format(parameter='PHSE', value=str(phase))
            logging.debug(f'Executing: {phase_command}')
            self.instrument.write(phase_command)

        if waveform is not None:
            waveform_command = COMMAND.format(parameter='WVTP', value=waveform)
            logging.debug(f'Executing: {waveform_command}')
            self.instrument.write(waveform_command)

        if output:
            self.instrument.write(f'C{channel:d}:OUTP ON')
        else:
            self.instrument.write(f'C{channel:d}:OUTP OFF')

        channel_settings = self.instrument.query(f'C{channel:d}:BSWV?')
        logging.info(f'instrument channel settings:\n{channel_settings}')
