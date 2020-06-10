function check_Afl_EditContactInfoForm(theForm)
{
// ----- name
  if (!validName(theForm.name.value))
  {
    alert("Please enter a valid \"Name\" value.")
    theForm.name.focus()
    theForm.name.select()
    return (false)
  }

// ----- address_1
  if (theForm.address_1.value.length < 1 || theForm.address_1.value.length > 64)
  {
    alert("Please enter a valid \"Address 1\" value.")
    theForm.address_1.focus()
    theForm.address_1.select()
    return (false)
  }

// ----- city
  if (theForm.city.value.length < 1 || theForm.city.value.length > 32)
  {
    alert("Please enter a valid \"City\" value.")
    theForm.city.focus()
    theForm.city.select()
    return (false)
  }

// ----- state
  if (!checkDropdown(theForm.state.value))
  {
    alert("Please enter a valid \"State\" value.")
    theForm.state.focus()
    return (false)
  }

// ----- country
  if (!checkDropdown(theForm.country.value))
  {
    alert("Please enter a valid \"Country\" value.")
    theForm.country.focus()
    return (false)
  }

// ----- zip
	var why = "";
	why += checkZipCode(theForm.zip.value);
	if (why != "") 
	{
		alert(why);
		theForm.zip.focus()
		theForm.zip.select()
		return (false)
	} 

// ----- phone
	why += checkPhone(theForm.phone.value);
	if (why != "") 
	{
		alert(why);
		theForm.phone.focus()
		theForm.phone.select()
		return (false)
	} 

// ----- fax
	why += checkPhone(theForm.fax.value);
	if (why != "") 
	{
		alert(why);
		theForm.fax.focus()
		theForm.fax.select()
		return (false)
	} 
  
  return (true)
}

