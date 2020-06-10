function check_Afl_LogInForm(theForm)
{
// ----- email
  if (!validEmail(theForm.email.value))
  {
    alert("Please enter a valid \"Email\" value.")
    theForm.email.focus()
    theForm.email.select()
    return (false)
  }

// ----- password
  if (!validName(theForm.password.value))
  {
    alert("Please enter a valid value for the \"Password\" field.\nThe following are invalid( ~`!@#$%^&*()-+={[}]|\"',<.>?/:;\)")
    theForm.password.focus()
    theForm.password.select()
    return (false)
  }  
  return (true)
}

