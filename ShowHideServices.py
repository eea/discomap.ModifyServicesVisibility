import urllib, urllib2, json, httplib
import arcpy
import os, sys
import shutil
import errno
import string
import datetime, time
import socket
import tempfile
import getpass

def gentoken(server, port, adminUser, adminPass, expiration=300):
    
    #Re-usable function to get a token required for Admin changes
    query_dict = {'username':adminUser,'password':adminPass,'client':'requestip'}
    
    query_string = urllib.urlencode(query_dict)
    url = "http://{}:{}/arcgis/admin/generateToken".format(server, port)
    
    token = json.loads(urllib.urlopen(url + "?f=json", query_string).read())
        
    if 'token' not in token:
        arcpy.AddError(token['messages'])
        quit()
    else:
        return token['token']

def formatDate():
    return str(time.strftime('%Y-%m-%d %H:%M:%S'))

def makeAGSconnection(server, port, adminUser, adminPass, workspace):
    
    ''' Function to create an ArcGIS Server connection file using the arcpy.Mapping function "CreateGISServerConnectionFile"    
    '''
    millis = int(round(time.time() * 1000))
    connectionType = 'ADMINISTER_GIS_SERVICES'
    connectionName = 'ServerConnection' + str(millis)
    serverURL = 'http://' + server + ':' + port + '/arcgis/admin'
    serverType = 'ARCGIS_SERVER'
    saveUserName = 'SAVE_USERNAME'
        
    outputAGS = os.path.join(workspace, connectionName + ".ags")
    try:
        arcpy.mapping.CreateGISServerConnectionFile(connectionType, workspace, connectionName, serverURL, serverType, True, '', adminUser, adminPass, saveUserName)
        return outputAGS
    except:
        arcpy.AddError("Could not create AGS connection file for: '" + server + ":" + port + "'")
        sys.exit()
        

# A function that will post HTTP POST request to the server
def postToServer(server, port, url, params):

    httpConn = httplib.HTTPConnection(server, port)
    headers = {"Content-type": "application/x-www-form-urlencoded", "Accept": "text/plain"}

    # URL encode the resoure URL
    url = urllib.quote(url.encode('utf-8'))
    
    # Build the connection to add the roles to the server
    httpConn.request("POST", url, params, headers)

    response = httpConn.getresponse()
    data = response.read()
    httpConn.close()
    
    return (response, data)


def numberOfServices(server, port, adminUser, adminPass, serviceType):
    
    #Count all the services of "MapServer" type in a server
    number = 0
    token = gentoken(server, port, adminUser, adminPass)    
    services = []    
    baseUrl = "http://{}:{}/arcgis/admin/services".format(server, port)
    catalog = json.load(urllib2.urlopen(baseUrl + "/" + "?f=json&token=" + token))
    services = catalog['services']
    
    for service in services:
        if service['type'] == serviceType:
            number = number + 1
            
    folders = catalog['folders']
    
    for folderName in folders:
        catalog = json.load(urllib2.urlopen(baseUrl + "/" + folderName + "?f=json&token=" + token))
        services = catalog['services']
        for service in services:
            if service['type'] == serviceType:
                number = number + 1

    return number


# A function that checks that the input JSON object is not an error object.
def assertJsonSuccess(data):
    
    obj = json.loads(data)
    if 'status' in obj and obj['status'] == "error":
        arcpy.AddMessage("     Error: JSON object returns an error. " + str(obj))
        return False
    else:
        return True

def showHideMapServices(serverName, serverPort, adminUser, adminPass, serviceListHide, serviceListShow, serviceType, token=None):
    serviceHideSuccesNumber = 0
    serviceHideFailureNumber = 0
    serviceShowSuccesNumber = 0
    serviceShowFailureNumber = 0
    
    content1 = "\n *************************************************************************** \n           Hidding services \n           " + formatDate() + "\n *************************************************************************** "
  
    # Getting services from tool validation creates a semicolon delimited list that needs to be broken up
    servicesHide = serviceListHide.split(';')
    servicesShow = serviceListShow.split(';')

    servicesHideCount = 0
    #modify the services(s)    
    for service in servicesHide:
        if (service != ''):
            servicesHideCount = servicesHideCount + 1 
            service = urllib.quote(service.encode('utf8'))
            serviceURL = "/arcgis/admin/services/" + service

            # Get and set the token
            token = gentoken(serverName, serverPort, adminUser, adminPass)

            # This request only needs the token and the response formatting parameter 
            params = urllib.urlencode({'token': token, 'f': 'json'})
            response, data = postToServer(serverName, str(serverPort), serviceURL, params)
            
            if (response.status != 200):
                arcpy.AddMessage("\n  ** Could not read service '" + str(service) + "' information.")
            else:
                # Check that data returned is not an error object
                if not assertJsonSuccess(data): arcpy.AddMessage("\n  ** Error when reading service '" + str(service) + "' information. " + str(data))
                else:
                    arcpy.AddMessage("\n  ** Service '" + str(service) + "' information read successfully.")

                    # Deserialize response into Python object
                    dataObj = json.loads(data)
                    user = getpass.getuser()
                    dataObj["deprecated"] = "true"

                    # Serialize back into JSON
                    updatedSvcJson = json.dumps(dataObj)

                    # Call the edit operation on the service. Pass in modified JSON.
                    editSvcURL = "/arcgis/admin/services/" + service + "/edit"
                    params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedSvcJson})
                    response, data = postToServer(serverName, str(serverPort), editSvcURL, params)
                    
                    if (response.status != 200):
                        serviceHideFailureNumber = serviceHideFailureNumber + 1
                        arcpy.AddMessage("  ** Error returned while editing service" + str(editData))
                    else:
                        serviceHideSuccesNumber = serviceHideSuccesNumber + 1
                        arcpy.AddMessage("  ** Service hidden successfully.")
          

    servicesShowCount = 0
    #modify the services(s)    
    for service in servicesShow:
        if (service != ''):
            servicesShowCount = servicesShowCount + 1
            service = urllib.quote(service.encode('utf8'))
            serviceURL = "/arcgis/admin/services/" + service

            # Get and set the token
            token = gentoken(serverName, serverPort, adminUser, adminPass)

            # This request only needs the token and the response formatting parameter 
            params = urllib.urlencode({'token': token, 'f': 'json'})
            response, data = postToServer(serverName, str(serverPort), serviceURL, params)
            
            if (response.status != 200):
                arcpy.AddMessage("\n  ** Could not read service '" + str(service) + "' information.")
            else:
                # Check that data returned is not an error object
                if not assertJsonSuccess(data): arcpy.AddMessage("\n  ** Error when reading service '" + str(service) + "' information. " + str(data))
                else:
                    arcpy.AddMessage("\n  ** Service '" + str(service) + "' information read successfully.")

                    # Deserialize response into Python object
                    dataObj = json.loads(data)
                    user = getpass.getuser()
                    dataObj["deprecated"] = "false"

                    # Serialize back into JSON
                    updatedSvcJson = json.dumps(dataObj)

                    # Call the edit operation on the service. Pass in modified JSON.
                    editSvcURL = "/arcgis/admin/services/" + service + "/edit"
                    params = urllib.urlencode({'token': token, 'f': 'json', 'service': updatedSvcJson})
                    response, data = postToServer(serverName, str(serverPort), editSvcURL, params)
                    
                    if (response.status != 200):
                        serviceShowFailureNumber = serviceShowFailureNumber + 1
                        arcpy.AddMessage("  ** Error returned while editing service" + str(editData))
                    else:
                        serviceShowSuccesNumber = serviceShowSuccesNumber + 1
                        arcpy.AddMessage("  ** Service shown successfully.")

                    
    number = numberOfServices(serverName, serverPort, adminUser, adminPass, serviceType)
    
    arcpy.AddMessage("\n***************************************************************************  ")
    arcpy.AddMessage(" - Number of services in '" + serverName + "': " + str(number))
    arcpy.AddMessage(" - Number of services selected in '" + serverName + "': " + str(servicesHideCount) + " to hide.")
    arcpy.AddMessage(" - Number of services selected in '" + serverName + "': " + str(servicesShowCount) + " to show.")
    arcpy.AddMessage(" - Number of services hidden successfully: " + str(serviceHideSuccesNumber))
    arcpy.AddMessage(" - Number of services shown successfully: " + str(serviceShowSuccesNumber))
    arcpy.AddMessage(" - Number of services not hidden: " + str(serviceHideFailureNumber))
    arcpy.AddMessage(" - Number of services not shown: " + str(serviceShowFailureNumber))
        
    arcpy.AddMessage("***************************************************************************  ")


   

if __name__ == "__main__":

    # Gather inputs    
    serverName = arcpy.GetParameterAsText(0)
    serverPort = arcpy.GetParameterAsText(1)
    adminUser = arcpy.GetParameterAsText(2)
    adminPass = arcpy.GetParameterAsText(3)
    serviceType = arcpy.GetParameterAsText(4) 
    serviceListShow = arcpy.GetParameterAsText(5)
    serviceListHide = arcpy.GetParameterAsText(6)
    
    if serviceType == "MapServer":
        showHideMapServices(serverName, serverPort, adminUser, adminPass, serviceListHide, serviceListShow, serviceType)
