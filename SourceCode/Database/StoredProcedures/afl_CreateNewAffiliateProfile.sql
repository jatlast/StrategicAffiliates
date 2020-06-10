CREATE PROCEDURE [afl_CreateNewAffiliateProfile]
-- afl_website_info...
  @site_name			VARCHAR	(128)	
, @site_url			VARCHAR	(1024)	
, @site_description		VARCHAR	(2048)	
, @primary_category		SMALLINT
-- afl_main_user_info...
, @name			VARCHAR	(96)
, @email			VARCHAR	(64)	
, @password			VARCHAR	(16)
, @password_question		VARCHAR	(28)	
, @password_answer		VARCHAR	(32)	
, @email_verification_code	VARCHAR	(17)	
-- afl_contact_info...
, @address_1			VARCHAR	(64)	
, @address_2			VARCHAR	(32)	
, @city				VARCHAR	(32)	
, @state			SMALLINT
, @zip				VARCHAR	(10)	
, @country			SMALLINT
, @phone			VARCHAR	(20)	
, @fax				VARCHAR	(20)	
-- afl_payment_info...
, @social_security_or_tax_id	VARCHAR	(9)		
, @payment_method		TINYINT
, @direct_deposit_country	SMALLINT
, @bank_name			VARCHAR	(32)	
, @account_type			VARCHAR	(8)	
, @name_on_bank_account	VARCHAR	(96)	
, @bank_account_number	VARCHAR	(10)	
, @bank_routing_number	VARCHAR	(9)	
, @pay_to_the_order_of		VARCHAR	(96)	
-- afl_main_user_info...
, @receive_promo_mail	BIT
, @accepted_terms		BIT
, @affiliate_of			INT

 AS

DECLARE @Today DATETIME
SELECT @Today = GETDATE()

DECLARE @@StoredProcName VARCHAR(256)
	, @CurrentAffiliateAccountId INT
SELECT @@StoredProcName = 'afl_CreateNewAffiliateProfile'


IF (@email_verification_code = '')
	BEGIN
		SELECT @email_verification_code = CONVERT( VARCHAR(10), CONVERT( INT, RAND() * 100000000 ) )  -- email_verification_code (Create a random numerical character sequence no larger than 10 chars long)
	END

	-- Begin a transaction so that all changes can be rolled back if any one of them fail...
	BEGIN TRANSACTION

	PRINT 'insert new affiliate into afl_main_user_info'
	INSERT INTO afl_main_user_info (email
					, password
					, name			
					, title
					, phone			
					, creation_date
					, last_login
					, password_question		
					, password_answer		
					, email_verification_code
					, is_email_verified
					, receive_promo_mail
					, accepted_terms
				   ) 
			VALUES (@email			      
				, @password			      
				, @name			      
				, 'Admin'			      
				, @phone			-- title
				, @Today			-- creation_date
				, @Today			-- last_login
				, @password_question		
				, @password_answer		      
				, @email_verification_code 	
				, '0'				-- is_email_verified
				, @receive_promo_mail		
				, @accepted_terms
				)

	-- Check for errors...
	IF( @@ERROR <> 0 )
		BEGIN
			PRINT  'ROLLBACK ' + @@StoredProcName + ': INSERT afl_main_user_info had problems.  (' + CONVERT( VARCHAR(8), @@ERROR ) + ')'
			-- Since an error was encountered rollback all prior work
			ROLLBACK TRANSACTION
			-- Skip to the end of the procedure
			GOTO end_of_batch
		END

	SELECT @CurrentAffiliateAccountId = @@identity
	
	PRINT 'insert new data into afl_contact_info'
	INSERT INTO afl_contact_info (afl_account_id
					, name
					, address_1			
					, address_2			
					, city				
					, state			
					, zip				
					, country			
					, phone			
					, fax				
				   ) 
			VALUES (@CurrentAffiliateAccountId
				, @name			      
				, @address_1			
				, @address_2			
				, @city				
				, @state
				, @zip				
				, @country
				, @phone		
				, @fax				
				)

	-- Check for errors...
	IF( @@ERROR <> 0 )
		BEGIN
			PRINT  'ROLLBACK ' + @@StoredProcName + ': INSERT afl_contact_info had problems.  (' + CONVERT( VARCHAR(8), @@ERROR ) + ')'
			-- Since an error was encountered rollback all prior work
			ROLLBACK TRANSACTION
			-- Skip to the end of the procedure
			GOTO end_of_batch
		END


	PRINT 'insert new data into afl_payment_info'
	INSERT INTO afl_payment_info (afl_account_id
					, minimum_payment		
					, payment_method			
					, pay_to_the_order_of		
					, social_security_or_tax_id		
					, bank_name				
					, name_on_bank_account				
					, account_type				
					, bank_account_number				
					, bank_routing_number				
				   ) 
			VALUES (@CurrentAffiliateAccountId
				, 20		
				, @payment_method			
				, @pay_to_the_order_of		
				, @social_security_or_tax_id		
				, @bank_name				
				, @name_on_bank_account				
				, @account_type				
				, @bank_account_number				
				, @bank_routing_number				
				)

	-- Check for errors...
	IF( @@ERROR <> 0 )
		BEGIN
			PRINT  'ROLLBACK ' + @@StoredProcName + ': INSERT afl_payment_info had problems.  (' + CONVERT( VARCHAR(8), @@ERROR ) + ')'
			-- Since an error was encountered rollback all prior work
			ROLLBACK TRANSACTION
			-- Skip to the end of the procedure
			GOTO end_of_batch
		END

	PRINT 'insert new data into afl_website_info'
	INSERT INTO afl_website_info (afl_account_id
					, site_name		
					, site_url			
					, site_description		
					, primary_category		
					, secondary_category_1				
					, secondary_category_2				
					, secondary_category_3				
				   ) 
			VALUES (@CurrentAffiliateAccountId
				, @site_name		
				, @site_url			
				, @site_description		
				, @primary_category		
				, NULL
				, NULL
				, NULL
				)

	-- Check for errors...
	IF( @@ERROR <> 0 )
		BEGIN
			PRINT  'ROLLBACK ' + @@StoredProcName + ': INSERT afl_website_info had problems.  (' + CONVERT( VARCHAR(8), @@ERROR ) + ')'
			-- Since an error was encountered rollback all prior work
			ROLLBACK TRANSACTION
			-- Skip to the end of the procedure
			GOTO end_of_batch
		END

	PRINT 'insert new data into afl_related_affiliates'
	INSERT INTO afl_related_affiliates (affiliate_unique_id
					, afl_account_id
					, payment_plan		
					, creation_date		
					, receive_email			
				   ) 
			VALUES ( @affiliate_of
				, @CurrentAffiliateAccountId		
				, 0			-- (payment_plan)  0 = Not Yet Chosen 
				, @Today
				, @receive_promo_mail
				)

	-- Check for errors...
	IF( @@ERROR <> 0 )
		BEGIN
			PRINT  'ROLLBACK ' + @@StoredProcName + ': INSERT afl_related_affiliates had problems.  (' + CONVERT( VARCHAR(8), @@ERROR ) + ')'
			-- Since an error was encountered rollback all prior work
			ROLLBACK TRANSACTION
			-- Skip to the end of the procedure
			GOTO end_of_batch
		END
	
	-- Pass back the unique id's
	SELECT @CurrentAffiliateAccountId AS 'affiliate_unique_id'

	-- Since every transaction returned a value of ( 0 ) commit all transactions...
	COMMIT TRANSACTION
	RETURN 1

	-- The GOTO lable that enables the batch to skip to the end without commtting
	end_of_batch:
	RETURN 666
GO

