''' Module to handle connections to TheSkyX

The classes are defined to match the classes in Script TheSkyX. This isn't
really necessary as they all just send the javascript to TheSkyX via
SkyXConnection._send().
'''
import logging
import time
from socket import socket, AF_INET, SOCK_STREAM, SHUT_RDWR, error


logger = logging.getLogger(__name__)

class Singleton(object):
    ''' Singleton class so we dont have to keep specifing host and port'''
    def __init__(self, klass):
        ''' Initiator '''
        self.klass = klass
        self.instance = None

    def __call__(self, *args, **kwds):
        ''' When called as a function return our singleton instance. '''
        if self.instance is None:
            self.instance = self.klass(*args, **kwds)
        return self.instance


class SkyxObjectNotFoundError(Exception):
    ''' Exception for objects not found in SkyX.
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxObjectNotFoundError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)


class SkyxConnectionError(Exception):
    ''' Exception for Failures to Connect to SkyX
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxConnectionError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)

class SkyxTypeError(Exception):
    ''' Exception for Failures to Connect to SkyX
    '''
    def __init__(self, value):
        ''' init'''
        super(SkyxTypeError, self).__init__(value)
        self.value = value

    def __str__(self):
        ''' returns the error string '''
        return repr(self.value)
    
@Singleton
class SkyXConnection(object):
    ''' Class to handle connections to TheSkyX
    '''
    def __init__(self, host="localhost", port=3040):
        ''' define host and port for TheSkyX.
        '''
        self.host = host
        self.port = port
        
    def reconfigure(self,host="localhost", port=3040):
        ''' If we need to chane ip we can do so this way'''
        self.host = host
        self.port = port
                
    def _send(self, command):
        ''' sends a js script to TheSkyX and returns the output.
        '''
        try:
            logger.debug(command)
            sockobj = socket(AF_INET, SOCK_STREAM)
            sockobj.connect((self.host, self.port))
            sockobj.send(('/* Java Script */\n' +
                               '/* Socket Start Packet */\n' + command +
                               '\n/* Socket End Packet */\n').encode())
            oput = sockobj.recv(2048)
            logger.debug(oput)
            sockobj.shutdown(SHUT_RDWR)
            sockobj.close()
            return oput.decode().split("|")[0]
        except error as msg:
            raise SkyxConnectionError("Connection to " + self.host + ":" + \
                                      str(self.port) + " failed. :" + str(msg))

    def find(self, target):
        ''' Find a target
            target can be a defined object or a decimal ra,dec
        '''
        output = self._send('sky6StarChart.Find("' + target + '")')
        if output == "undefined":
            return True
        else:
            raise SkyxObjectNotFoundError(target)

class TheSkyXAction(object):
    ''' Class to implement the TheSkyXAction script class
    '''
    def __init__(self, host="localhost", port=3040):
        ''' Define connection
        '''
        self.conn = SkyXConnection(host, port)
        
    def TheSkyXAction(self, action):
        ''' The TheSkyXAction object allows a script to invoke a subset of
            commands listed under Preferences, Toolbars, Customize.
        '''
        command = "TheSkyXAction.execute(\"" + action + "\")"
        oput = self.conn._send(command)
        if oput == "undefined":
            return True
        else:
            raise SkyxObjectNotFoundError(oput)

class SkyXTargetInformation(object):
    ''' Class to implement the sky6ObjectInformation script class
    '''
    def __init__(self, host="localhost", port=3040):
        ''' Define connection
        '''
        self.conn = SkyXConnection(host, port)
        
    def property(self, prop):
        ''' Returns a value for the desired Sk6ObjectInformationProperty
            argument.
        '''
        command = """
                var Out = "";
                sky6ObjectInformation.Property(""" + str(prop) + """);
                Out = String(sky6ObjectInformation.ObjInfoPropOut);"""
        oput = self.conn._send(command)
        return oput

    def current_target_ra_dec(self, j="now"):
        ''' Attempt to get info on the current target
        '''
        if j == "now":
            command = """
                    var Out = "";
                    var Target54 = 0;
                    var Target55 = 0;
                    sky6ObjectInformation.Property(54);
                    Target54 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(55);
                    Target55 = sky6ObjectInformation.ObjInfoPropOut;
                    Out = String(Target54) + " " + String(Target55);
                      """        
        elif j == "2000":
            command = """
                    var Out = "";
                    var Target56 = 0;
                    var Target57 = 0;
                    sky6ObjectInformation.Property(56);
                    Target56 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(57);
                    Target57 = sky6ObjectInformation.ObjInfoPropOut;
                    Out = String(Target56) + " " + String(Target57);
                      """
        else:
            raise SkyxTypeError("Unknown epoch: " + j)
        res = self.conn._send(command).splitlines()
        logger.debug(res)
        output = [float(x) for x in res[0].split()   ] 
        return output

    def __call__(self, target):
        ''' Method to return basic SkyX position information on a target.
        '''
        # TODO: make target optional
        # TODO: return all data
        command = """
                var Target = \"""" + target + """\";
                var Target56 = 0;
                var Target57 = 0;
                var Target58 = 0;
                var Target59 = 0;
                var Target77 = 0;
                var Target78 = 0;
                var Out = "";
                var err;
                try {
                    sky6StarChart.Find(Target);
                    sky6ObjectInformation.Property(54);
                    Target56 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(55);
                    Target57 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(58);
                    Target58 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(59);
                    Target59 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(77);
                    Target77 = sky6ObjectInformation.ObjInfoPropOut;
                    sky6ObjectInformation.Property(78);
                    Target78 = sky6ObjectInformation.ObjInfoPropOut;
                    Out = "sk6ObjInfoProp_RA_NOW:"+String(Target56)+
                    "\\nsk6ObjInfoProp_DEC_NOW:"+String(Target57)+
                    "\\nsk6ObjInfoProp_AZM:"+String(Target58)+
                    "\\nsk6ObjInfoProp_ALT:"+String(Target59)+
                    "\\nsk6ObjInfoProp_RA_RATE_ASPERSEC:"+String(Target77)+
                    "\\nsk6ObjInfoProp_DEC_RATE_ASPERSEC:"+String(Target78)+"\\n";
                } catch (e) {
                    Out = Target + " not found.";
                }
                """
        results = {}
        oput = self.conn._send(command)
        for line in oput.splitlines():
            if "not found" in line:
                raise SkyxObjectNotFoundError("Object not found.")
            if ":" in line:
                info = line.split(":")[0].split("_", 1)[1].lower()
                val = float(line.split(":")[1])
                results[info] = val
        return results


class SkyXCamera(object):
    ''' Class to implement the ccdsoftCamera script class
    '''
    def __init__(self, host="localhost", port=3040):
        ''' Define connection
        '''
        self.conn = SkyXConnection(host, port)
        self.frames = {1:"Light", 2:"Bias", 3:"Dark", 4:"Flat Field"}
        self.connect()
        
    def connect(self, is_async: bool = False):
        ''' Connect to the camera defined in the TheSkyX profile
      
            Returns True on success or throws a SkyxTypeError
        '''
        command = """
                    var Imager = ccdsoftCamera;
                    var Out = "";
                    Imager.Connect();
                    Imager.Asynchronous = """ + str(int(is_async)) + """;
                    Out = Imager.Status;
                    """
        output = self.conn._send(command).splitlines()
        if "Ready" not in output[0]:
            raise SkyxTypeError(output[0])
        return True

    def disconnect(self):
        ''' Disconnect the camera
            Returns True on success or throws a SkyxTypeError
        '''
        command = """
                    var Imager = ccdsoftCamera;
                    var Out = "";
                    Imager.Disconnect();
                    Out = Imager.Status;
                  """
        output = self.conn._send(command).splitlines()
        if "Not Connected" not in output[0]:
            raise SkyxTypeError(output[0])
        return True
    
    @property
    def integration_time(self):
        ''' Set the exposure time to the given argument or return the 
            current exposure time.
        '''
        command = "ccdsoftCamera.ExposureTime"
        return(self.conn._send(command).splitlines()[0])
    
    @integration_time.setter
    def integration_time(self, seconds: float):
        command = "ccdsoftCamera.ExposureTime = " + str(seconds) + ";"
        output = self.conn._send(command).splitlines()
        if abs(float(output[0]) - seconds) > 1e-6:
            raise SkyxTypeError(output[0])
        return(output[0])
    
    @property
    def binning(self):
        """Get the current binning."""
        command = "ccdsoftCamera.BinX"
        binning_value = self.conn._send(command).splitlines()[0]
        return binning_value

    @binning.setter
    def binning(self, value: int):
        """Set the binning or return the current binning.
        
        We assume NxN binning, so just set/get BinX.
        """
        command = f"ccdsoftCamera.BinX = {value};"
        output = self.conn._send(command).splitlines()
        if output[0] != str(value):
            raise SkyxTypeError(f"Failed to set binning to {value}, response was {output[0]}")
        return output[0]

    @property 
    def frame_type(self):
        ''' Set the Frame type or return the current type

            Be careful setting 'Dark' as the frame as this will open
            a dialog on screen.
        '''
        command = "ccdsoftCamera.Frame"
        itype = self.conn._send(command).splitlines()[0]
        return(self.frames[int(itype)])
    
    @frame_type.setter
    def frame_type(self, frame_type: str):
        if not frame_type in self.frames:
            raise SkyxTypeError("Unknown Frame type. Must be one of: " +
                                str(self.frames))

        frameid = self.frames.index(frame_type)
        command = "ccdsoftCamera.Frame = " + str(frameid) + ";"
        output = self.conn._send(command).splitlines()
        if output[0] != str(frameid):
            raise SkyxTypeError(output[0])

    def take_image(self):
        ''' Takes an image.
        '''
        command = """
                  var Out = "";
                  ccdsoftCamera.TakeImage();"""
        self.conn._send(command)
    
    @property
    def last_image_file_name(self):
        command = """
            var Out = "";
            Out += ccdsoftCamera.LastImageFileName;
        """
        return self.conn._send(command)
    
    @property
    def temperature(self):
        command = """
            var Out = "";
            Out += ccdsoftCamera.Temperature;
        """
        return self.conn._send(command)

    @property
    def auto_save(self):
        command = """
        var Out = "";
        Out += ccdsoftCamera.AutoSaveOn;
        """
        return bool(int(self.conn._send(command)))

    @auto_save.setter
    def auto_save(self, state: bool):
        command = f"""
        ccdsoftCamera.AutoSaveOn = {int(state)};
        """
        self.conn._send(command)

class SkyXTelescope(object):
    def __init__(self, host="localhost", port=3040):
        """Initializes the telescope

        :param host: The host of TheSkyX's TCP server, defaults to "localhost"
        :type host: str, optional
        :param port: The port of TheSkyX's TCP server, defaults to 3040
        :type port: int, optional
        """
        self.conn = SkyXConnection(host, port)
        self.connect()
        
    def connect(self) -> bool:
        """Connects to the telescope
        """
        command = """
                  var Out = "";
                  sky6RASCOMTele.Connect();
                  Out = sky6RASCOMTele.IsConnected"""
        output = self.conn._send(command).splitlines()
        if int(output[0]) != 1:
            raise SkyxTypeError("Telescope not connected. "+\
                                "sky6RASCOMTele.IsConnected=" + output[0])
        return True
        
    def disconnect(self):
        """Disconnects the telescope
        """
        command = """
                  var Out = "";
                  sky6RASCOMTele.Disconnect();
                  Out = sky6RASCOMTele.IsConnected"""
        output = self.conn._send(command).splitlines()
        if int(output[0]) != 0:
            raise SkyxTypeError("Telescope still connected. " +\
                                "sky6RASCOMTele.IsConnected=" + output[0])
        return True
    

    def slew_to_ra_dec(self, ra_deg: float, dec_deg: float) -> None:
        """Sluews the telescope to the given RA and Dec

        :param ra_deg: The RA in degrees
        :type ra_deg: float
        :param dec_deg: The Dec in degrees
        :type dec_deg: float
        :rtype: None
        """
        command= f"""
        var Out = "";

        sky6RASCOMTele.SlewToRaDec({ra_deg},{dec_deg}, "");
        """
        self.conn._send(command)

    @property
    def tracking_rates(self) -> list[float]:
        """Gets the tracking rates for the telescope

        :return: The RA and Dec tracking rates in arcseconds per second
        :rtype: list[float]
        """
        command= """
        var Out = "";

        Out += sky6RASCOMTele.dRaTrackingRate + "\\n";
        Out += sky6RASCOMTele.dDecTrackingRate; 
        """
        output = [float(x) for x in self.conn._send(command).splitlines()]
        return output
    
    def set_tracking_rates(self, ra_rate_asps: float, dec_rate_asps: float) -> None:
        """Sets the tracking rates for the telescope

        :param ra_rate_asps: The RA tracking rate in arcseconds per second
        :type ra_rate_asps: float
        :param dec_rate_asps: The Dec tracking rate in arcseconds per second
        :type dec_rate_asps: float
        :rtype: None
        """
        command= f"""
            sky6RASCOMTele.SetTracking(1,0,{ra_rate_asps},{dec_rate_asps});
        """
        self.conn._send(command).splitlines()

    def sidereal_tracking(self):
        """Sets the telescope to sidereal tracking (zero RA/Dec rates)
        """
        self.set_tracking_rates(0, 0)

    @property
    def pointing_ra_dec(self):
        """The current pointing RA and Dec in degrees
        """
        command = """
                  var Out = "";
                  sky6RASCOMTele.GetRaDec();
                  Out = String(sky6RASCOMTele.dRa) + " " + String(sky6RASCOMTele.dDec);
                  """
        output = [float(x) for x in self.conn._send(command).splitlines()[0].split()]
        return output

    def slew_to_ra_dec_and_track(self, ra_deg: float, dec_deg: float, ra_rate_asps: float, dec_rate_asps: float) -> None:
        """Slews to the given RA and Dec and sets the tracking rates to the given values

        :param ra_deg: The RA in degrees
        :type ra_deg: float
        :param dec_deg: The Dec in degrees
        :type dec_deg: float
        :param ra_rate_asps: The RA tracking rate in arcseconds per second
        :type ra_rate_asps: float
        :param dec_rate_asps: The Dec tracking rate in arcseconds per second
        :type dec_rate_asps: float
        """
        self.slew_to_ra_dec(ra_deg, dec_deg)
        self.set_tracking_rates(ra_rate_asps, dec_rate_asps)
    
    def slew_and_track_satellite(self, intl_designator: str) -> None:
        """Slews to the given satellite and tracks it, if it is visible

        :param intl_designator: The international designator of the satellite
        :type intl_designator: str
        """
        obj = SkyXTargetInformation()
        target = obj(intl_designator)
        self.slew_to_ra_dec_and_track(target['ra_now'], target['dec_now'], 
                                             target['ra_rate_aspersec'],
                                             target['dec_rate_aspersec'])