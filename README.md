# discomap.ModifyServicesVisibility
Changing visibility of Services
Description
This tool allows changing the visibility of the selected services from a server.

Environment requirements
The tool is developped to run under Arcgis 10.3.1 (Python2.7)
The user that executes the tool or/and the user from ArcGIS Server that uses the geoprocessing service, should be able to access to each network path where the service’s sources are placed in order to copy them. 

Installation
ArcGIS Tool
ArcGis tool is placed in the toolbox called “EEA Generic Tools”. Inside this toolbox is the “ArcGis Server Tools” toolset. There is located the “ShowHideServices” tool.
 

Functionality

The script uses seven parameters:
 [1] Server Name (string)
The host name of the server. Typically a single name or fully qualified server, such as myServer.esri.com
 [2] Server Port (string)
The port number for the ArcGIS Server. Typically this is 6080. If you have a web adapter installed with your GIS Server and have the REST Admin enabled you can connect using the web servers port number.
[3] Server User (long)
Administrative username.
[4] Server Password (string) 
Administrative password.
[5] Service Type (string)
The type of the service.
[6] ServicesShow (Multiple Value)
One or more services to show. The tool will autopopulate with a list of services when the first 5 parameters are entered. Service names must be provided in the <ServiceName>.<ServiceType> style.
[7] ServicesHide (Multiple Value)
One or more services to hide. The tool will autopopulate with a list of services when the first 5 parameters are entered. Service names must be provided in the <ServiceName>.<ServiceType> style.

The script uses the username and the password to connect to the server with a generatetoken action. After accessing to the server, all services are listed. When the user selects the services to migrate and fills all the parameters the process starts.	