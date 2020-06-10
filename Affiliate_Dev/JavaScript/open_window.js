// **************************************************************
// JavaScript function to open a pop-up window

function OpenWithCrumbTrail( url, height, width ) {
	now = new Date();
	
	extraURL = '';
	pos = url.indexOf('?');
	if( pos >= 0 ) {
		extraURL = '&';
	} else {
		extraURL = '?';
	}
	extraURL += 'crumbTrail=' + now.valueOf();
	
    winName = "temp" + now.valueOf();
	
    (window.open(url + extraURL, winName, 'width=' + width + ',height=' + height + ',resizable=yes,scrollbars=yes')).focus();
}

function OpenWindow( url, height, width ) {
    
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable,scrollbars')).focus();
    
  }

function OpenWindowNoScroll(url, height, width) {
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable=no,scrollbars=no')).focus();
}

function OpenWindowToolBar(url, height, width) {
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable=yes,scrollbars=yes,toolbar=yes,status=yes')).focus();
}

function OpenWindowStatus( url, height, width ) {
    
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable,scrollbars,status,')).focus();
    
  }



function OpenWindowTool(url, height, width) {
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable,scrollbars,toolbar')).focus();
}


function makeRemote() {
remote = window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable=yes,scrollbars=yes,toolbar=yes,status=yes');

    if (remote.opener == null) remote.opener = window; 
remote.opener.name = "opener";
}

function changeOpenerUrl(url) {
	window.opener.location.href=url;
	window.opener.focus();
}

function confirmDelete(url){

  if (! confirm('Are you sure you want to delete this contact?')){
      
  }
  else{
      window.location = url;
      return false;
  }
}


 
