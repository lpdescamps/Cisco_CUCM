const xapi = require('xapi');
	
const MYSPEED_DIAL_NUMBER = 'myroom@meeting.com';

xapi.event.on('UserInterface Extensions Page Action', (event) => {
	if(event.Type == 'Opened' && event.PageId == 'speed_dial'){
		xapi.command("dial", {Number: MYSPEED_DIAL_NUMBER});
	}
});