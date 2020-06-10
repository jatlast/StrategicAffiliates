function check_Afl_JoinNowForm(theForm)
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
	if (!checkDropdown(theForm.primary_category.value))
	{
		alert("Please choose the topic of your website.")
		return (false)
	}
  
// ----- name
  if (!validName(theForm.name.value))
  {
    alert("Please enter a valid \"Name\" value.")
    theForm.name.focus()
    theForm.name.select()
    return (false)
  }

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

// ----- country
  if (!checkDropdown(theForm.country.value))
  {
    alert("Please enter a valid \"Country\" value.")
    theForm.country.focus()
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

// ----- social_security_or_tax_id
  if (theForm.social_security_or_tax_id.value.length < 8 || theForm.social_security_or_tax_id.value.length > 12)
  {
    alert("Please enter a valid \"Tax ID (SSN/EIN)\" value.")
    theForm.social_security_or_tax_id.focus()
    theForm.social_security_or_tax_id.select()
    return (false)
  }

// ----- payment_method
	if (!validateRadioButtons(theForm.payment_method))
	{
		alert("Please choose a payment method value.")
		theForm.payment_method.focus()
		return (false)
	}
	else
	{
// -- if payment_method = Direct Deposit...
		if(theForm.payment_method[0].checked)
		{
			// ----- direct_deposit_country
			  if (!validateRadioButtons(theForm.direct_deposit_country))
			  {
				alert("Please choose a direct deposit country.")
				theForm.direct_deposit_country.focus()
				return (false)
			  }

			// ----- bank_name
			  if (!validName(theForm.bank_name.value))
			  {
				alert("Please enter a valid \"Bank Name\" value.")
				theForm.bank_name.focus()
				theForm.bank_name.select()
				return (false)
			  }

			// ----- name_on_bank_account
			  if (!validName(theForm.name_on_bank_account.value))
			  {
				alert("Please enter a valid \"Name on Account\" value.")
				theForm.name_on_bank_account.focus()
				theForm.name_on_bank_account.select()
				return (false)
			  }
			
			// ----- bank_account_number
			  if ( (!isNum(theForm.bank_account_number.value)) || theForm.bank_account_number.value.length < 10)
			  {
				alert("Please enter a valid \"Account number\" value.")
				theForm.bank_account_number.focus()
				theForm.bank_account_number.select()
				return (false)
			  }
			
			// ----- bank_routing_number
			  if ( ( !isNum(theForm.bank_routing_number.value) ) || theForm.bank_routing_number.value.length < 9)
			  {
				alert("Please enter a valid \"Routing number\" value.")
				theForm.bank_routing_number.focus()
				theForm.bank_routing_number.select()
				return (false)
			  }		
		}
// -- else payment_method = Pay by Check...
		else
		{
		// ----- pay_to_the_order_of
			  if (!validName(theForm.pay_to_the_order_of.value))
			  {
				alert("Please enter a valid \"Checks payable to\" value.")
				theForm.pay_to_the_order_of.focus()
				theForm.pay_to_the_order_of.select()
				return (false)
			  }		
		}
	}

// ----- accepted_terms
	if (!theForm.accepted_terms.checked)
	{
		alert("You must accept the terms before creating an account.")
		return (false)
	}

 return (true)
}

