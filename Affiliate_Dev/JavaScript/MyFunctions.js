function newDefinitionWindow(Word, WordDefined) 
{
    var myWindow = window.open('Definition', 'Define', 'toolbar=yes,location=yes,scrollbars=yes,resizable=yes,width=400,height=400')
    myWindow.document.writeln("<HTML>")
    myWindow.document.writeln("  <HEAD>")
    myWindow.document.writeln("    <TITLE>")
    myWindow.document.writeln("      Definition for: \"" + Word + "\"")
    myWindow.document.writeln("    </TITLE>")
    myWindow.document.writeln("  </HEAD>")
    myWindow.document.writeln("  <BODY>")
    myWindow.document.writeln("    <TABLE cellspacing=\"1\" cellpadding=\"8\" border=\"1\">")
    myWindow.document.writeln("      <TBODY>")
    myWindow.document.writeln("        <TR>")
    myWindow.document.writeln("          <TD>")
    myWindow.document.writeln("            <DL>")
    myWindow.document.writeln("              <DT>")
    myWindow.document.writeln("                 <EM><STRONG><FONT color=\"red\">" + Word + "</FONT></STRONG></EM>")
    myWindow.document.writeln("              </DT>")
    myWindow.document.writeln("              <DD>")
	myWindow.document.writeln("                " + WordDefined + "")
    myWindow.document.writeln("              </DD>")
    myWindow.document.writeln("            </DL>")
    myWindow.document.writeln("          </TD>")
    myWindow.document.writeln("        </TR>")
    myWindow.document.writeln("      </TBODY>")
    myWindow.document.writeln("    </TABLE>")
    myWindow.document.writeln("    <BR>")
    myWindow.document.writeln("    <P>")
    myWindow.document.writeln("       <A onclick=\"window.close(); return false;\" href=\"#\">Close this window.</A>")
    myWindow.document.writeln("    </P>")
    myWindow.document.writeln("  </BODY>")
    myWindow.document.writeln("</HTML>")

    myWindow.focus()
}

function newDefineWord(myWord) 
{
		var myWindow = window.open('Definition', 'Define', 'toolbar=no,location=no,scrollbars=yes,resizable=yes,width=500,height=400')
		myWindow.location="http://10.10.11.4:1800/cgi-bin/Define.cgi?word=" + myWord + "&link=yes"
		myWindow.focus()
}

function confirmDelete(url){

  if (! confirm('Are you sure you want to delete?'))
	{
      
	}
  else
	{
      window.location = url;
      return false;
	}
}

function OpenWindow( url, height, width ) {
    
    uniqueKey = Math.round(Math.random() * 100000);
    winName = "temp" + uniqueKey;
    (window.open(url, winName, 'width=' + width + ',height=' + height + ',resizable,scrollbars')).focus();
    
  }

function newWindowGeneric(url) 
{
	var h=Math.min(600,screen.height-50);
	var myWindow = window.open(url,'popup','width=500,height='+h+',toolbar=0,scrollbars=1,location=0,statusbar=1,menubar=0,resizable=1');
	myWindow.focus()
}

function popup(url) 
	{
  var h=Math.min(600,screen.height-50);
  window.open(url,'popup','width=500,height='+h+',toolbar=0,scrollbars=1,location=0,statusbar=1,menubar=0,resizable=1');
  return false;
}

function modifyText(id, text) 
	{
		if(document.getElementById && text != '') 
		{
			obj = document.getElementById(id);
			obj.childNodes[0].data = text;
		}
	}

function filterVisibleURL(text) 
	{
		return text.replace(/^\s*/, '').replace(/\s*$/, '').replace(/^https?:\/\//, '').replace(/\/.*/, '').replace(/:[0-9]+$/, '');
	}

function focusField(name) 
	{
		for(i=0; i < document.forms.length; ++i) 
			{
				var obj = document.forms[i].elements[name];
				if (obj && obj.focus) 
					{
						obj.focus();
					}
			}
	}

function selectField(name) 
	{
		for(i=0; i < document.forms.length; ++i) 
			{
				var obj = document.forms[i].elements[name];
				if (obj && obj.focus)
					{
						obj.focus();
					} 
				if (obj && obj.select)
					{
						obj.select();
					}
			}
	}

function mOvr(src, clrOver)
	{ 
		if (!src.contains(event.fromElement))
			{ 
				src.style.cursor = 'hand'; 
				src.bgColor = clrOver; 
			} 
	} 

function mOut(src, clrIn)
	{ 
		if (!src.contains(event.toElement))
			{
				src.style.cursor = 'default';
				src.bgColor = clrIn;
			} 
	} 

function mClk(src)
	{ 
		if(event.srcElement.tagName=='TD')
		{
			src.children.tags('A')[0].click();
		}
	}

function isNum(passedVal)
{
//	alert("within isNum")
	if(passedVal == "")
	{
		return false
	}
	for(i=0; i<passedVal.length; i++)
	{
		if(passedVal.charAt(i) < "0")
		{
			return false
		}
		if(passedVal.charAt(i) > "9")
		{
			return false
		}
	}
	return true
}

function validEmail(email)
{
invalidChars = " /:,;"

    // email cannot be empty...
    if(email == "")
    {
        return false
    }

    // does it contain any invalid characters...
    for (i=0; i<invalidChars.length; i++)
    {
        badChar = invalidChars.charAt(i)
        if (email.indexOf(badChar, 0) > -1)
        {
            return false
        }
    }

    // there must be one "@" symbol...
    atPos = email.indexOf("@",1)
    if (atPos == -1)
    {
        return false
    }

    // and only one "@" symbol...
    if (email.indexOf("@", atPos+1) != -1)
    {
        return false
    }

    // and at least one "." after the "@"...
    periodPos = email.indexOf(".", atPos)
    if (periodPos == -1)
    {
        return false
    }

    // must be at least 2 characters after the "."...
    if (periodPos+3 > email.length)
    {
        return false
    }
return true
}

function validateRadioButtons(ButtonsToValidate)
	{
//		alert("within validateRadioButtons")
		var contentOption = -1
//		alert(ButtonsToValidate.length)
		for(i=0; i<ButtonsToValidate.length; i++)
			{
//				alert(ButtonsToValidate[i])
//				alert(ButtonsToValidate[i].checked)
				if(ButtonsToValidate[i].checked)
					{
						contentOption = 1
					}
			}
		if(contentOption == -1)
			{
				return false
			}
		return true
	}

function validNoQuoteChars(myName)
	{
//		alert("within validNoQuoteChars")
		var invalidChars = "\"'\\"

		// field cannot be empty...
		if(myName == "" || myName.length < 2)
			{
				return false
			}

		// does it contain any invalid characters...
		for (i=0; i<invalidChars.length; i++)
			{
				badChar = invalidChars.charAt(i)
				if (myName.indexOf(badChar, 0) > -1)
					{
						return false
					}
			}
		return true
	}

function validName(myName)
{
var invalidChars = "~`!@#$%^&*()-+={[}]|\"',<>?/:;\\"

    // field cannot be empty...
    if(myName == "")
    {
        return false
    }

    // does it contain any invalid characters...
    for (i=0; i<invalidChars.length; i++)
    {
        badChar = invalidChars.charAt(i)
        if (myName.indexOf(badChar, 0) > -1)
        {
            return false
        }
    }
return true
}

// valid selector from dropdown list
function checkDropdown(choice) 
{
   if (choice == 0 || choice == -1)
	{
		return (false);
	}    
return (true);
}

// zip - between 4-5 numeric chars
function checkZipCode (strng) {
   var error = "";
   var legalChars = /[abcdefghijklmnopqrstuvwxyz0123456789-ABCDEFGHIJKLMNOPQRSTUVWXYZ]{4,10}/; // allow only letters and numbers

   if (strng == "") {
      error = "You didn't enter a Zip Code.\n";
   }
   else if ((strng.length < 4) || (strng.length > 10)) {
      error = "The Zip Code is the wrong length.\n";
   }
   else if (!legalChars.test(strng)) {
     error = "The Zip Code contains illegal characters.\n";
   } 
return error;    
} 

// phone number - strip out delimiters and check for 10 digits
function checkPhone (strng) 
{
	var error = "";
	if (strng == "") 
	{
		error = "You didn't enter a phone number.\n";
	}
	var stripped = strng.replace(/[\(\)\.\-\ ]/g, ''); //strip out acceptable non-numeric characters
	if (isNaN(parseInt(stripped))) 
	{
		error = "The phone number contains illegal characters.";
	}
	 if ((stripped.length < 10)) 
	{
		error = "The phone number is the wrong length. Make sure you included an area code.\n";
	} 
	return error;
}

function printAffiliateTable(Word, WordDefined) 
{
	document.writeln("    <TABLE width=\"500\" height=\"500\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">")
	document.writeln("      <TR>")
	document.writeln("        <TD width=\"501\" height=\"371\" background=\"images/index_BG.jpg\">")
	document.writeln("          <TABLE width=\"500\" height=\"500\" border=\"0\" cellpadding=\"0\" cellspacing=\"0\">")
	document.writeln("            <TR>")
	document.writeln("              <TD height=\"72\" colspan=\"2\">")
	document.writeln("                <IMG src=\"images/NetLM_meet_your_match.gif\">")
	document.writeln("              </TD>")
	document.writeln("            </TR>")
	document.writeln("            <TR>")
	document.writeln("              <TD width=\"250\" height=\"309\" valign=\"top\">")
	document.writeln("                <FORM onsubmit=\"return checkForm(this)\" method=\"POST\" action=\"http://www.persianconnections.com/cgi-bin/GenHome.exe\">")
	document.writeln("                </FORM>")
	document.writeln("                <TABLE width=\"240\" border=\"0\" cellspacing=\"0\" cellpadding=\"2\">")
	document.writeln("                  <TR>")
	document.writeln("                    <TD colspan=\"2\">")
	document.writeln("                      <A href=\"http://www.persianconnections.com/SimpleSearch.html\"><IMG src=\"images/NetLM_free_guest_search.gif\" border=\"0\"></A>")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                  <TR>")
	document.writeln("                    <TD colspan=\"2\">")
	document.writeln("                      <A href=\"http://www.persianconnections.com/CreateLogin.html\"><IMG src=\"images/NetLM_create_profile.gif\" border=\"0\"></A>")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                  <TR>")
	document.writeln("                    <TD colspan=\"2\">")
	document.writeln("                      <IMG src=\"images/NetLM_member_login.gif\">")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                  <TR>")
	document.writeln("                    <TD nowrap width=\"93\" align=\"right\"><font size=\"2\" face=\"Arial, Helvetica, sans-serif\">")
	document.writeln("                      user name:")
	document.writeln("                    </font></TD>")
	document.writeln("                    <TD width=\"144\">")
	document.writeln("                      <INPUT type=\"text\" name=\"textfield\">")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                  <TR>")
	document.writeln("                    <TD width=\"93\" align=\"right\"><font size=\"2\" face=\"Arial, Helvetica, sans-serif\">")
	document.writeln("                      password:")
	document.writeln("                    </font></TD>")
	document.writeln("                    <TD>")
	document.writeln("                      <INPUT type=\"text\" name=\"textfield2\">")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                  <TR>")
	document.writeln("                    <TD>")
	document.writeln("                      &nbsp;")
	document.writeln("                    </TD>")
	document.writeln("                    <TD>")
	document.writeln("                      <A href=\"http://\"><IMG src=\"images/NetLM_login.gif\" border=\"0\"></A>")
	document.writeln("                    </TD>")
	document.writeln("                  </TR>")
	document.writeln("                </TABLE>")
	document.writeln("                <P>")
	document.writeln("                  &nbsp;")
	document.writeln("                </P>")
	document.writeln("              </TD>")
	document.writeln("              <TD width=\"250\">")
	document.writeln("                &nbsp;")
	document.writeln("              </TD>")
	document.writeln("            </TR>")
	document.writeln("            <TR>")
	document.writeln("              <TD width=\"250\" height=\"27\">")
	document.writeln("                <A href=\"mailto:info\@persianconnections.com\"><IMG src=\"images/NetLM_contact_us.gif\" border=\"0\"></A><A href=\"http://\"><IMG src=\"images/NetLM_policies.gif\" border=\"0\"></A>")
	document.writeln("              </TD>")
	document.writeln("              <TD width=\"250\">")
	document.writeln("                &nbsp;")
	document.writeln("              </TD>")
	document.writeln("            </TR>")
	document.writeln("            <TR>")
	document.writeln("              <TD width=\"250\" height=\"33\">")
	document.writeln("                <A href=\"http://www.persianconnections.com\"><IMG src=\"images/NetLM_poweredby.gif\" border=\"0\"></A>")
	document.writeln("              </TD>")
	document.writeln("              <TD width=\"250\">")
	document.writeln("                &nbsp;")
	document.writeln("              </TD>")
	document.writeln("            </TR>")
	document.writeln("          </TABLE>")
	document.writeln("        </TD>")
	document.writeln("      </TR>")
	document.writeln("    </TABLE>")
}
