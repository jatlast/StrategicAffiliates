function checkForm(theForm)
{
// ----- unique_id
  if ( !validName(theForm.user_name.value) )
  {
    alert("Please enter a numeric value for the \"User Name\" field.")
    theForm.unique_id.focus()
    return (false)
  }

// ----- password
  if (!validName(theForm.password.value))
  {
    alert("Please enter a valid value for the \"Password\" field.\nThe following are invalid( ~`!@#$%^&*()-+={[}]|\"',<.>?/:;\)")
    theForm.password.focus()
    return (false)
  }
  return (true)
}