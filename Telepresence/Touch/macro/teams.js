const xapi = require('xapi');
	
const MYSPEED_DIAL_NUMBER = '1234567890@v.meeting.com';

xapi.event.on('UserInterface Extensions Page Action', (event) => {
	if(event.Type == 'Opened' && event.PageId == 'speed_dial_teams'){
		xapi.command("dial", {Number: MYSPEED_DIAL_NUMBER});
	}
});