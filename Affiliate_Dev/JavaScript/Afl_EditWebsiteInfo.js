function check_Afl_EditWebsiteInfoForm(theForm)
{
// ----- site_name
  if (!validName(theForm.site_name.value))
  {
    alert("Please enter a valid \"Site Name\" value.")
    theForm.site_name.focus()
    theForm.site_name.select()
    return (false)
  }

// ----- site_url
  if (theForm.site_url.value.length < 1 || theForm.site_url.value.length > 1024)
  {
    alert("Please enter a valid \"Site URL\" value.")
    theForm.site_url.focus()
    theForm.site_url.select()
    return (false)
  }

// ----- site_description
  if (theForm.site_description.value.length < 1 || theForm.site_description.value.length > 2048)
  {
    alert("Please enter a valid \"Site Description\" value.")
    theForm.site_description.focus()
    theForm.site_description.select()
    return (false)
  }

// ----- primary_category
	if (!validateRadioButtons(theForm.primary_category))
	{
		alert("Please chose at least one primary category.")
		return (false)
	}
  
// ----- secondary_category
  var count;
  var element;
  count = 0;
  for(i=0; i < theForm.length; i++)
	  {
		element = theForm.elements[i];
		if (element.type == 'checkbox') 
			{
				if(element.checked)
					{
						count += 1;
					}
			}
	}
  if (count > 3)
	{
		alert('You may only choose up to three general categories.');
		return (false)
	}

 return (true)
}

