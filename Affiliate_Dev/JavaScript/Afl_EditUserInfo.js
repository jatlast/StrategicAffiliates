function check_Afl_EditUserInfoForm(theForm)
{
// ----- name
  if (!validName(theForm.name.value))
  {
    alert("Please enter a valid \"Name\" value.")
    theForm.name.focus()
    theForm.name.select()
    return (false)
  }

// ----- title
  if (theForm.title.value.length > 0)
  {
	  if (!validName(theForm.title.value))
	  {
		alert("Please enter a valid \"Title\" or just leave it blank.")
		theForm.title.focus()
		theForm.title.select()
		return (false)
	  }
  }

// ----- email
  if (!validEmail(theForm.email.value))
  {
    alert("Please enter a valid \"Email\" value.")
    theForm.email.focus()
    theForm.email.select()
    return (false)
  }

// ----- phone
  if (theForm.phone.value.length > 0)
  {
	var why = "";
	why += checkPhone(theForm.phone.value);
	if (why != "") 
	{	
		why = why + "\nThe Phone field is not required so you can just leave it blank.";
		alert(why);
		theForm.phone.focus()
		theForm.phone.select()
		return (false)
	} 
  }

// ----- password
  if (!validName(theForm.password.value))
  {
    alert("Please enter a valid value for the \"Password\" field.\nThe following are invalid( ~`!@#$%^&*()-+={[}]|\"',<.>?/:;\)")
    theForm.password.focus()
    theForm.password.select()
    return (false)
  }

  if (theForm.password.value.length > 15)
  {
    alert("Please enter at most 15 characters in the \"Password\" field.")
    theForm.password.focus()
    theForm.password.select()
    return (false)
  }

// ----- verify_password
  if (theForm.password.value != theForm.verify_password.value)
  {
    alert("Password fields do not match")
    theForm.password.focus()
    theForm.password.select()
    return (false)
  }
  
// ----- password_question
  if (!checkDropdown(theForm.password_question.value))
  {
    alert("Please enter a valid \"I.D. Question\" value.")
    theForm.password_question.focus()
    return (false)
  }

// ----- password_answer
  if (theForm.password_answer.value.length < 1)
  {
    alert("Please enter a valid answer in the \"I.D. Answer\" field.")
    theForm.password_answer.focus()
    theForm.password_answer.select()
    return (false)
  }
  
// ----- account_type
	if (theForm.account_type.value == -1)
	{
		alert("Please enter a valid \"User Type\" value.")
		theForm.account_type.focus()
		return (false)
	}    

  return (true)
}

