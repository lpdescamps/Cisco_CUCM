const xapi = require('xapi');
const server = 'myserver.com';

xapi.config.set('HttpClient Mode', 'On');
var systemInfo = {
    softwareVersion : ''
    , systemName : ''
    , softwareReleaseDate : ''
    , ipaddress : ''
};


function sendWebHook() {

  systemInfo.systemName = systemInfo.systemName.replace(/\//g, "%20");
  systemInfo.systemName = systemInfo.systemName.replace("-","%20");
  systemInfo.systemName = systemInfo.systemName.replace("(","");
  systemInfo.systemName = systemInfo.systemName.replace(")","");
  systemInfo.systemName = systemInfo.systemName.replace("&","%20");
  systemInfo.systemName = systemInfo.systemName.replace(/ /g,"%20");

  if (systemInfo.systemName === "" || systemInfo.systemName === undefined) {
      init();

      setTimeout(function() {
         var model = {};
        model.TopColour =  "FF0000";
        model.BottomColour = "FF0000";
        model.ShouldFlash = false;
        model.ShouldReset = false;

        xapi.command('HttpClient Get', { 'Url' : 'http://' + server + ':8085/api/colourmessage/setcolours?topColour=' + model.TopColour + '&bottomColour=' + model.BottomColour + '&shouldFlash=' + model.ShouldFlash + '&shouldReset=' + model.ShouldReset, 'AllowInsecureHTTPS': 'False'});

        xapi.command('HttpClient Get', { 'Url' : 'http://' + server + ':8085/api/sms?ipAddress=' + systemInfo.ipaddress, 'AllowInsecureHTTPS': 'False'});

        return xapi.command('HttpClient Get', { 'Url': 'http://' + server + '/Home/Index?ipAddress=' + systemInfo.ipaddress + "&title=" + systemInfo.systemName + "&message=A%20user%20requires%20assistance%20in%20this%20meeting%20room.%20%20Please%20visit%20and%20provide%20support%20ASAP!", 'AllowInsecureHTTPS': 'False'});
      }, 3000);
    } else {

      setTimeout(function() {
        var model = {};
        model.TopColour =  "red";
        model.BottomColour = "FF0000";
        model.ShouldFlash = false;
        model.ShouldReset = false;

        xapi.command('HttpClient Get', { 'Url' : 'http://' + server + ':8085/api/colourmessage/setcolours?topColour=' + model.TopColour + '&bottomColour=' + model.BottomColour + '&shouldFlash=' + model.ShouldFlash + '&shouldReset=' + model.ShouldReset, 'AllowInsecureHTTPS': 'False'});

        xapi.command('HttpClient Get', { 'Url' : 'http://' + server + ':8085/api/sms?ipAddress=' + systemInfo.ipaddress, 'AllowInsecureHTTPS': 'False'});

        return xapi.command('HttpClient Get', { 'Url':'http://' + server + '/Home/Index?ipAddress=' + systemInfo.ipaddress + "&title=" + systemInfo.systemName + "&message=A%20user%20requires%20assistance%20in%20this%20meeting%20room.%20%20Please%20visit%20and%20provide%20support%20ASAP!", 'AllowInsecureHTTPS': 'False'});

      }, 3000);
    }
}

xapi.event.on('UserInterface Extensions Page Action', (event) => {
	if(event.Type == 'Opened' && event.PageId == 'Request_IT_Help'){
		sendWebHook();
	}
});

function closeNotification(event) {
  if (event.WidgetId === 'btnClose' && event.Type === 'clicked') {
    console.log('btnClose clicked');

    xapi.command('UserInterface Message Alert Display', {
                 Title: 'DD Test',
                 Text: 'DD Test',
                Duration: 10,
                });

   // xapi.command("UserInterface Extensions Page Close");
    //xapi.command("UserInterface Extensions Page Closed");
  }
}


xapi.event.on('UserInterface Extensions Widget Action', closeNotification);



function init(){
  xapi.status.get('SystemUnit Software Version').then((value) => {
    systemInfo.softwareVersion = value;
  });
  xapi.config.get('SystemUnit Name').then((value) => {
    if(value === ''){
        xapi.status.get('SystemUnit Hardware Module SerialNumber').then((value) => {
          systemInfo.systemName = value;
        });
    }
    else{
      systemInfo.systemName = value;
    }
  });
  xapi.status.get('SystemUnit Software ReleaseDate').then((value) => {
    systemInfo.softwareReleaseDate = value;
  });


  xapi.status.get("Network 1 IPv4 Address").then((value) => {
       systemInfo.ipaddress = value;
  });

  xapi.config.set('HttpClient Mode', 'On');


}


init();
