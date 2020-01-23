const xapi = require('xapi');
const server = 'gbcrowebwd0008.qbe.eo';

xapi.config.set('HttpClient Mode', 'On');

var systemInfo = {
  softwareVersion : ''
  , systemName : ''
  , softwareReleaseDate : ''
  , ipaddress : ''
};

function sendWebHook(title, message, shouldSendSms) {

  if (systemInfo.systemName === "" || systemInfo.systemName === undefined) {
      init();
  }

  setTimeout(function() {

    systemInfo.systemName = systemInfo.systemName.replace(/\//g, "%20");
    systemInfo.systemName = systemInfo.systemName.replace("-","%20");
    systemInfo.systemName = systemInfo.systemName.replace("(","");
    systemInfo.systemName = systemInfo.systemName.replace(")","");
    systemInfo.systemName = systemInfo.systemName.replace("&","%20");
    systemInfo.systemName = systemInfo.systemName.replace(/ /g,"%20");

    if (shouldSendSms === true) {
      xapi.command('HttpClient Get', { 'Url' : 'http://' + server + ':8085/api/sms?ipAddress=' + systemInfo.ipaddress, 'AllowInsecureHTTPS': 'False'});
    }

    xapi.command('HttpClient Get', { 'Url':'http://' + server + '/Home/Index?ipAddress=' + systemInfo.ipaddress + "&title=" + title + systemInfo.systemName + "&message=" + message, 'AllowInsecureHTTPS': 'False'});

  }, 3000);

}

function displayEngineerWillRespondShortlyAlert() {
    xapi.command('UserInterface Message Alert Display', {
      Title: 'Incident Reported',
      Text: 'Thank you for reporting this issue, one of the team will visit the room shortly and investigate further.',
      Duration: 10
    });
}

function displayEngineerNotifiedAlert() {
  xapi.command('UserInterface Message Alert Display', {
    Title: 'Incident Reported',
    Text: 'Thank you for reporting this issue. An onsite engineer has been notified.',
    Duration: 10
  });
}

function sendImmediateAssistance(event) {
  if (event.WidgetId === 'btnImmediateHelp' && event.Type === 'clicked') {
    var message = "A%20user%20requires%20assistance%20in%20this%20meeting%20room.%20%20Please%20visit%20and%20provide%20support%20ASAP!";
    sendWebHook("Urgent%20Request%20for%20Meeting%20Room%20", message, true);
    displayEngineerWillRespondShortlyAlert();
  }
}

function unableToJoinTeamsMeeting(event) {
  if (event.WidgetId === 'btnUrgentTeams' && event.Type === 'clicked') {
    var message = "A%20user%20is%20having%20issues%20connecting%20to%20a%20meeting.%20%20Please%20visit%20and%20provide%20support%20ASAP.";
    sendWebHook("Urgent%20Request%20for%20Meeting%20Room%20", message, true);
    displayEngineerWillRespondShortlyAlert();
  }
}

function nonUrgentAudio(event) {
  if (event.WidgetId === 'btnNonUrgentAudio' && event.Type === 'clicked') {
    var message = "A%20user%20has%20reported%20an%20issue%20with%20the%20television%20audio.%20%20Please%20provide%20support%20when%20you%20are%20available.%20%20This%20is%20a%20non%20urgent%20request."
    sendWebHook("An%20issue%20has%20been%20reported%20in%20", message, false);
    displayEngineerNotifiedAlert();
  }
}

function nonUrgentTelephone(event) {
  if (event.WidgetId === 'btnNotUrgentTelephone' && event.Type === 'clicked') {
    var message = "A%20user%20has%20reported%20an%20issue%20with%20the%20meeting%20room%20telephone.%20%20Please%20provide%20support%20when%20you%20are%20available.%20%20This%20is%20a%20non%20urgent%20request."
    sendWebHook("An%20issue%20has%20been%20reported%20in%20", message, false);
    displayEngineerNotifiedAlert();
  }
}

function nonUrgentEquipment(event) {
  if (event.WidgetId === 'btnNonUrgentEquipment' && event.Type === 'clicked') {
    var message = "A%20user%20has%20reported%20the%20meeting%20room%20is%20missing%20equipment.%20%20Please%20provide%20support%20when%20you%20are%20available.%20%20This%20is%20a%20non%20urgent%20request."
    sendWebHook("An%20issue%20has%20been%20reported%20in%20", message, false);
    displayEngineerNotifiedAlert();
  }
}

function nonUrgentHdmi(event) {
  if (event.WidgetId === 'btnNotUrgentHDMI' && event.Type === 'clicked') {
    var message = "A%20user%20has%20reported%20the%20meeting%20room%20is%20having%20issues%20with%20HDMI.%20%20Please%20provide%20support%20when%20you%20are%20available.%20%20This%20is%20a%20non%20urgent%20request."
    sendWebHook("An%20issue%20has%20been%20reported%20in%20", message, false);
    displayEngineerNotifiedAlert();
  }
}

function reportFacilities(event) {
    if (event.WidgetId === 'btnReportFacilities' && event.Type === 'clicked') {
    var message = "A%20user%20has%20reported%20that%20the%20facilities%20of%20this%20meeting%20room%20require%20attention.%20%20Please%20investigate%20accordingly."
    sendWebHook("Facilities%20Issue%20in%20", message, false);
    displayEngineerNotifiedAlert();
  }
}

function nonUrgentOther(event) {

  if (event.WidgetId === 'btnNotUrgentOther' && event.Type === 'clicked') {

    xapi.event.on('UserInterface Message TextInput Response', (event) => {
      if (event.FeedbackId === 'report-issue') {
         var message = event.Text;
         message = message.replace(/\//g, "%20");
         message = message.replace("-","%20");
         message = message.replace("(","");
         message = message.replace(")","");
         message = message.replace("&","%20");
         message = message.replace(/ /g,"%20");

        sendWebHook("An%20issue%20has%20been%20reported%20in%20", message, false);
        displayEngineerNotifiedAlert();
      }
    });

    xapi.command('UserInterface Message TextInput Display', {
      FeedbackId: 'report-issue',
      Title: 'Please describe the issue',
      Text: 'The onsite team will investigate and resolve the issue',
    });

  }
}

xapi.event.on('UserInterface Extensions Widget Action', sendImmediateAssistance);
xapi.event.on('UserInterface Extensions Widget Action', unableToJoinTeamsMeeting);
xapi.event.on('UserInterface Extensions Widget Action', nonUrgentAudio);
xapi.event.on('UserInterface Extensions Widget Action', nonUrgentTelephone);
xapi.event.on('UserInterface Extensions Widget Action', nonUrgentEquipment);
xapi.event.on('UserInterface Extensions Widget Action', nonUrgentHdmi);
xapi.event.on('UserInterface Extensions Widget Action', nonUrgentOther);
xapi.event.on('UserInterface Extensions Widget Action', reportFacilities);

function init(){

  xapi.config.set('HttpClient Mode', 'On');
  xapi.status.get('SystemUnit Software Version').then((value) => { systemInfo.softwareVersion = value; });
  xapi.status.get('SystemUnit Software ReleaseDate').then((value) => {  systemInfo.softwareReleaseDate = value; });
  xapi.status.get("Network 1 IPv4 Address").then((value) => { systemInfo.ipaddress = value; });

  xapi.config.get('SystemUnit Name').then((value) => {
    if(value === '') {
        xapi.status.get('SystemUnit Hardware Module SerialNumber').then((value) => {
          systemInfo.systemName = value;
        });
    } else {
      systemInfo.systemName = value;
    }
  });
}

init();
