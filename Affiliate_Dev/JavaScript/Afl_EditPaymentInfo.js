function check_Afl_EditPaymentInfoForm(theForm)
{
	// ----- social_security_or_tax_id
	if (theForm.social_security_or_tax_id.value.length < 9)
	{
		alert("Please enter a valid \"Tax ID (SSN/EIN)\" value.")
		theForm.social_security_or_tax_id.focus()
		theForm.social_security_or_tax_id.select()
		return (false)
	}

	// ----- minimum_payment
	if (!checkDropdown(theForm.minimum_payment.value))
	{
		alert("Please enter a valid \"Minimum Payment Acount\" value.")
		theForm.minimum_payment.focus()
		return (false)
	}

// ----- payment_method
	if (!validateRadioButtons(theForm.payment_method))
	{
		alert("Please chose a payment method value.")
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
				alert("Please chose a direct deposit country.")
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
  return (true)
}

