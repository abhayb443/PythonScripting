from application.apps.document_service.model.DocumentServiceModel import *
from application.config.Autoload import *
from application.apps.document_service.service.ThirdPartyService import *
from multiprocessing import Pool,Process

Document_Model_Object = DocumentServiceModel()
Thirdparty_Service_Class = ThirdPartyService()


##################################################################
## Class : documentServiceCLass					##
## Use: Defination Of Logics 					##
## Author: J@yesh Bh@gat					##
##################################################################
class documentServiceClass():




######################################################################
## function : getDocuments					    ##
## User: Get list of documents with speicified types	            ##
## Parameters : request_params (Object of params)		    ##
##              extra_params (Object of params for where condition) ############
##		Uniuq_id : Request Unique identification number x-request-id ###
################################################################################
	def getDocuments(self,request_params,types,extra_parameters,Unique_Id):

		try:

			Request_Object = {}
			if types == 'users':

				Request_Object['user_reference_number'] = request_params # Get Documents for user reference number

			elif types == 'applications':

				Request_Object['application_reference_number'] = request_params # Get Documents for source reference number and source APPLICATION

			elif types == 'transactions':

				Request_Object['transaction_reference_number'] = request_params # Get Documents for source reference number and source TRANSACTION

			else:

				Request_Object['document_reference_number'] = request_params # Get Single Documents Via document reference number



			# If extra parameters are present in object it will be treated as where condition for select query
			if extra_parameters:

				for Param_Keys,Param_Values in extra_parameters.items():

					Request_Object[Param_Keys] = Param_Values


			# Get documents model call
			Response_Object = Document_Model_Object.getDocumentList(Request_Object) # Model Call
			Create_Response_Object = {}

			# If result has more that 0 count then change document url to presigned url and append in same key
			if Response_Object:

				Counter = 0

				for Data in Response_Object:

					# Create Amazon Presigned Url @ Amazon_Library is Library defined in Library folder
					Response_Object[Counter]['document_url'] = Amazon_Library.Create_Presigned_Url(Response_Object[Counter]['document_url'])
					Counter += 1

				Create_Response_Object['success'] = True
				Create_Response_Object['documents'] = Response_Object

				Core_Object.Write_Logs(str(Unique_Id), '|getDocuments| Response Data | '+str(Core_Object.returnJsonForLogs(Create_Response_Object)),
					      'Document_Processer_getDocumentsByUserRefNumber', 'document_process')



			else:

				Create_Response_Object['success'] = False
				Create_Response_Object['error_code'] = 502

				Core_Object.Write_Logs(str(Unique_Id), '|getDocuments| Response Data | '+str(Core_Object.returnJsonForLogs(Create_Response_Object)),
					      'Document_Processer_getDocumentsByUserRefNumber', 'document_process')



		except Exception as e:

			# Exception Handling
			Core_Object.Write_Logs(str(Unique_Id), '|getDocuments| Request Data | '+str(e),
					      'Document_Processer_getDocumentsByUserRefNumber', 'document_process')

			print('Exception Get Documents:-'+str(e))
			Create_Response_Object = {}
			Create_Response_Object['success'] = False
			Create_Response_Object['error_code'] = 502

		#print(Response_Object)
		return Create_Response_Object


##################################################################################
## function : setDocumentsService					    	##
## User: Make entry for documents using OCR,Blur CHeck,Parsing functionality	##
## Parameters : files (file bytes)		    				##
##              request_params (required params to make entry for docs)		##
##		Uniuq_id : Request Unique identification number x-request-id 	##
##################################################################################

	def setDocumentsService(self,files,request_params,Unique_Id,File_Name):

		print(2)
		Response = {}

		try:
			Options_Upload = {}
			Request_Object = {}

			if 'file' in request_params.keys():
				Check_File = files.encode("ascii")
				Check_Extension = base64.decodebytes(Check_File)
				Kind = filetype.guess(Check_Extension)
				Extension = Kind.mime.split('/')[1]
				Options_Upload['Format'] = Extension  # get Extension from filename


			else:
				# Get Filename , Extension from files
				File_Name,Extension = os.path.splitext(files.filename)
				Options_Upload['Format'] = Extension.replace('.','') # get Extension from filename


			Create_Mutable_Dict = {}

			for Keys,Values in request_params.items():

				Create_Mutable_Dict[Keys] = Values

			if Core_Object.acceptExetensions(Options_Upload['Format'].lower()) == False:

				Options_Upload['Format'] = ''


			# Nach_Category_Id is 8 for NACH defined in ConfigurationVariables.py below code executes only for NACH form
			if 'document_category_id' in Create_Mutable_Dict and Create_Mutable_Dict['document_category_id'] == Nach_Category_Id:

				Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-nach-start',
					      'Document_Processer_Set_Document', 'document_process')

				Process_Options = {}
				Process_Options['check'] = 2
				Process_Options['format'] = "tiff" # required output format tiff/ jpg
				Bytes = Core_Object.convertToBytes(files,1) # Convert bytes to CV2 format
				files.seek(0) # Close current file for another operation
				Uploaded_Filename = Amazon_Library.Upload_Document_S3(files.read(),{"Format":"jpg","Bucket_Key":"Original_Nach"},'Original_Nach'+request_params['source_reference_number'])


				Document_To_Upload = Nach_Process_Library.Process_Nach_Documents(Bytes,Process_Options) # Returned Bytes from Nach_Process_Library.Process_Nach_Documents

				Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-nach-process_completed',
					      'Document_Processer_Set_Document', 'document_process')

				if Document_To_Upload['success'] == False:

					return Document_To_Upload

				Extract_Text_From_Nach = Amazon_Library.Detect_Text_From_Image(Document_To_Upload['image_data']) # Extract text from nach form

				# If nach form wrongly formated reject it
				if Nach_Process_Library.Is_Image_Worng(Extract_Text_From_Nach) == False:

					Response['error_code'] = 512
					Response['success'] = False
					return Response

				Create_Mutable_Dict['document_category_id'] = '73'
				Create_Mutable_Dict['document_type_id'] = '169'
				Document_To_Upload = Document_To_Upload['image_data']

				Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-nach-process_final_out',
					      'Document_Processer_Set_Document', 'document_process')

			else:

				# If Not nach form
				if 'file' in request_params.keys():
					files = files.encode("ascii")
					Document_To_Upload =base64.decodebytes(files)

				else:
					Document_To_Upload = files.read()

			if Create_Mutable_Dict['document_type_id'] in Statement_Parsing_Document_Type:

				files.seek(0) # Close current file for another operation
				Bank_Statement_Response = Bank_Statment_Parsing.bankStatmentPasring(files,request_params)
				if 'success' in Bank_Statement_Response and Bank_Statement_Response['success'] == False:

						#Response['success'] = False
						#Response['error_code'] = 623
						Create_Mutable_Dict['extracted_data'] = json.dumps(Bank_Statement_Response)
						#return Response
				else:

						Create_Mutable_Dict['extracted_data'] = json.dumps(Bank_Statement_Response)

			Bounding_Box_Coordinates = ''

			Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-bounding_coordinates',
					      'Document_Processer_Set_Document', 'document_process')

			# If coordinates provided as bounding_coordinates for crop functionality
			if 'bounding_coordinates' in request_params:

					Bounding_Box_Coordinates = request_params['bounding_coordinates']


			# Only work for OCR functionality  Ocr_Enabled_Categories contains list of OCR enabled categories
			if 'document_type_id' in request_params and request_params['document_type_id'] in Ocr_Enabled_Categories:


				Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-inside OCR enable functionality',
					      'Document_Processer_Set_Document', 'document_process')


				Extra_Parmas = {"unique_reference_id":Unique_Id,"source_reference_number":request_params['source_reference_number'],
"user_reference_number":request_params['user_reference_number'],"document_type":request_params['document_type_id'],"bounding_boxes":Bounding_Box_Coordinates,'file_name':File_Name,'source':request_params['source'],'face':request_params['face']}
				# Face verify enabled type enabled it if speicifed type is there

				if Is_Ocr_Enabled == 'YES':

					# If blur check is enabled
					if Is_Blur_Check_Enabled == 'YES':

						Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-Blur check',
					      'Document_Processer_Set_Document', 'document_process')

						Kind = filetype.guess(Document_To_Upload)
						Exetension = Kind.mime.split('/')
						if Exetension[1] == 'pdf':

							Pages = convert_from_bytes(Document_To_Upload, 500)

							Bytes_Image = BytesIO()

							for Page in Pages:
							    Page.save(Bytes_Image, 'JPEG')

							Document_To_Upload = Bytes_Image.getvalue()


						if Extra_Parmas['bounding_boxes']:


								Document_To_Upload = ImageProcess_Library.cropImages(Document_To_Upload,Extra_Parmas['bounding_boxes'])

						Create_Mutable_Dict['blur_variance'] = round(ImageProcess_Library.blurDetection(Document_To_Upload))
						# Blur theshold should be match specified threshold
						if not round(ImageProcess_Library.blurDetection(Document_To_Upload)) > Blur_Check_Threshold:

								Create_Mutable_Dict['rework_reason'] = 'Image is blurry'
								Create_Mutable_Dict['underwriter_status'] = 'REWORK'
								Create_Mutable_Dict['is_discarded'] = '1'

								Response_Document_Upload = self.uploadDocuments(Document_To_Upload,File_Name,Create_Mutable_Dict,Options_Upload)

								Document_Model_Object.setDocument(Response_Document_Upload,Unique_Id)

								Create_Mutable_Dict['blur_threshold'] = round(ImageProcess_Library.blurDetection(Document_To_Upload))

								Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Response Data | '+json.dumps(Create_Mutable_Dict),
					      'Document_Processer_Set_Document', 'document_process')

								# Only In Case for MMT
								if Create_Mutable_Dict['source'] == 'MMT':


									Thirdparty_Service_Class.executeEventApiMmt(Create_Mutable_Dict,Unique_Id)


								Response['error_code'] = 527
								Response['success'] = False

								return Response

					if Face_Detection_Document == 'YES' and str(Create_Mutable_Dict['document_type_id']) in Face_Detection_Enabled_Document_Type and Create_Mutable_Dict['face'].lower() == 'front':

						Detect_Face_Response = RufiloOcr_Library.detectFace(Document_To_Upload)
						Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-perform face identify '+str(Detect_Face_Response),
					      'Document_Processer_Set_Document', 'document_process')


						if Detect_Face_Response==False:

							Response['error_code'] = 540
							Response['success'] = False
							return Response


					Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Checkpoint-perform ocr',
					      'Document_Processer_Set_Document', 'document_process')

					# OCR Activity if enabled ids from type
					if str(Create_Mutable_Dict['document_type_id']) in Face_Verify_Enabled_Type_Id:

						# Hyperverge APi Call
						# Log every hit of hyperverge

						Response = Hyperverge_Library.verifyKyc(Document_To_Upload,Extra_Parmas)
						print(Response)

						if not 'data' in Response:

							Response['error_code'] = 512
							Response['success'] = False
							return Response

						_insert_logs_hyperverge = {}
						_insert_logs_hyperverge['api_function_name'] = 'verifyKyc'
						_insert_logs_hyperverge['user_reference_number'] = Create_Mutable_Dict['user_reference_number']
						_insert_logs_hyperverge['api_request'] = json.dumps(request_params)
						_insert_logs_hyperverge['api_response'] = json.dumps(Response['data'])
						_insert_logs_hyperverge['transaction_reference_number'] = Create_Mutable_Dict['source_reference_number']
						_insert_logs_hyperverge['transaction_id'] = 0

						del(Response['data'])
						Document_Model_Object.insertHypervergeHitLogs(_insert_logs_hyperverge,Unique_Id)

						Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Hyperverge Response | '+Core_Object.returnJsonForLogs(Response),
					      'Document_Processer_Set_Document', 'document_process')

						# If approved and OCR verified / success
						if Response['success'] == True:

							Create_Mutable_Dict['extracted_data'] = Response['extracted_data']
							Create_Mutable_Dict['screening_status'] = 'APPROVED'

							Response_Json_Decode = json.loads(Response['extracted_data'])

							# To check whether required data in Response_Json_Decode, If it is present add it to doc_unique_id cloum.

							if 'aadhaar_number' in Response_Json_Decode:
								Create_Mutable_Dict['doc_unique_id'] = Response_Json_Decode['aadhaar_number']['value']

							elif 'pan_number' in Response_Json_Decode:
								Create_Mutable_Dict['doc_unique_id'] = Response_Json_Decode['pan_number']['value']

							elif 'passport_number' in Response_Json_Decode :
								Create_Mutable_Dict['doc_unique_id'] = Response_Json_Decode['passport_number']['value']

							elif 'license_number'in Response_Json_Decode:
								Create_Mutable_Dict['doc_unique_id'] = Response_Json_Decode['license_number']['value']

							elif 'voterid_number'in Response_Json_Decode:
								Create_Mutable_Dict['doc_unique_id'] = Response_Json_Decode['voterid_number']['value']

						else:

							if 'extracted_data' in Response:

								Create_Mutable_Dict['extracted_data'] = Response['extracted_data']

							# Set default value auto_rework is true
							if not 'auto_rework' in Create_Mutable_Dict:

								Create_Mutable_Dict['auto_rework'] = 'true'


							if Create_Mutable_Dict['auto_rework'] == 'true':

								# If document is not verified by OCR rework the document

								if Response['error_code'] == 514 or Response['error_code'] == 530 or Response['error_code'] == 525:

									Create_Mutable_Dict['rework_reason'] = 'Incorrect Doc'

								elif Response['error_code'] == 515:

									Create_Mutable_Dict['rework_reason'] = 'Aadhar Number Not Found/Invalid'

								elif Response['error_code'] == 516:

									Create_Mutable_Dict['rework_reason'] = 'Address Mismatch'

								elif Response['error_code'] == 517:

									Create_Mutable_Dict['rework_reason'] = 'Incorrect Doc'

								Create_Mutable_Dict['underwriter_status'] = 'REWORK'

							Create_Mutable_Dict['is_discarded'] = '1'
							# Only In Case for MMT
							if Create_Mutable_Dict['source'] == 'MMT':


								Thirdparty_Service_Class.executeEventApiMmt(Create_Mutable_Dict,Unique_Id)

			# if photo is selfie check for selfie is live or not
			if str(Create_Mutable_Dict['document_type_id']) in Selfie_Document_Type:
						response_liveness = Hyperverge_Library.checkLiveness(Document_To_Upload,{'user_reference_number':Create_Mutable_Dict.get('user_reference_number')})
						Response = response_liveness
						if response_liveness.get('success') == False:
							Create_Mutable_Dict['underwriter_status'] = 'REWORK'
							Create_Mutable_Dict['rework_reason'] = 'Photo is not live'

						# Log every hit of hyperverge
						_insert_logs_hyperverge = {}
						_insert_logs_hyperverge['api_function_name'] = 'check_liveness'
						_insert_logs_hyperverge['user_reference_number'] = Create_Mutable_Dict['user_reference_number']
						_insert_logs_hyperverge['api_request'] = json.dumps(request_params)
						_insert_logs_hyperverge['api_response'] = json.dumps(response_liveness['data'])
						_insert_logs_hyperverge['transaction_reference_number'] = Create_Mutable_Dict['source_reference_number']
						_insert_logs_hyperverge['transaction_id'] = 0

						Document_Model_Object.insertHypervergeHitLogs(_insert_logs_hyperverge,Unique_Id)

						del(Response['data'])


			# Upload document whther it is rework or success (Amazon S3 upload and creation of object to insert)
			Response_Document_Upload = self.uploadDocuments(Document_To_Upload,File_Name,Create_Mutable_Dict,Options_Upload)

			Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|Request Data | '+json.dumps(Response_Document_Upload),
					      'Document_Processer_Set_Document', 'document_process')


			# Make document table entry
			if Document_Model_Object.setDocument(Response_Document_Upload,Unique_Id) == True:

					if not Create_Mutable_Dict['source'] == 'RUFILO_APP':

						# Doc verify txn-service call
						Thirdparty_Service_Class.executeTxnServiceVerifyDoc(request_params,Unique_Id)

						# Web Hook Calls
						Thirdparty_Service_Class.executeWebHookAPi(request_params,Unique_Id)

					# insert data inside extracted data shadow to comparewith hyperverge
					if Shadow_Extracted_Insert == 'yes':
						if Create_Mutable_Dict['document_type_id'] in ['3'] :

							document_type = 'aadhaar_front' if Create_Mutable_Dict.get('face').lower() == 'front' else 'aadhaar_back'

							try:

								files.seek(0)
								Document_To_Upload = files.read()
								_post_data = {}
								_post_data['document_reference_number'] = Response_Document_Upload['document_reference_number']
								_post_data['document_type'] = document_type
								get_data = Thirdparty_Service_Class.postInternalOcr(Document_To_Upload,_post_data)

							except Exception as error_message:
								print(error_message)
								pass

					Response['data'] = {"doc_ref_number":Response_Document_Upload['document_reference_number']}
					# If REWORK is there throw error
					if 'underwriter_status' in Create_Mutable_Dict:

						Response['error_code'] = Response['error_code']
						Response['success'] = False
					else:


						if Create_Mutable_Dict.get('face').lower() == "back" and Create_Mutable_Dict.get('document_type_id') in ['3']:
							created_address_object_keys = {"line_1":"line1","line_2":"line2","room_number":"house_number","landmark":"landmark","pincode":"pin"}
							create_address_object = {}
							create_json = json.loads(Create_Mutable_Dict.get('extracted_data'))

							for add_keys in created_address_object_keys.keys():
								 create_address_object[add_keys] = create_json.get('address')[created_address_object_keys[add_keys]]

							create_address_object['label'] = 'ocr_address'
							create_address_object['tag'] = 'HOME'
							create_address_object['source'] = 'OCR'

							response_insert_add = Thirdparty_Service_Class.executeaadharAddressInsert(Create_Mutable_Dict,create_address_object,Unique_Id)

							Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocuments|setDocumentsService|response executeaadharAddressInsert | '+json.dumps(response_insert_add),
									      'Document_Processer_Set_Document', 'document_process')

							if response_insert_add['success'] == False:
								Response['success'] = True
								return Response

						Response['success'] = True

			else:
					Response['error_code'] = 504
					Response['success'] = False


		except Exception as e:

			# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
			# tail -f /var/log/apache2/doc-service/error.log ( production)
			print('Exception Set Document Service:-'+str(e))
			Core_Object.Write_Logs(str(Unique_Id), ' |service-function|setDocuments|setDocumentsService|Exceptions| '+str(e),
				      'Document_Processer_Set_Document', 'document_process')

			Response['error_code'] = 522
			Response['success'] = False

		return Response


##################################################################################
## function : setDocumentEaadharService					    	##
## User: Eaadhar upload and pdf parsing of eaadhar				##
## Parameters : files (pdf file bytes)		    				##
##              request_params (required params to make entry for pdf)		##
##		Uniuq_id : Request Unique identification number x-request-id 	##
##################################################################################
	def setDocumentEaadharService(self,files,request_params,Unique_Id):


		Response = {}

		try:

			File_Name,Extension = os.path.splitext(files.filename)

			Request_Format = Extension.replace('.','')

			# If file is not pdf return false
			if not 'pdf' in Request_Format.lower():

				Response['error_code'] = 503
				Response['success'] = False

				return Response

			else:

				# Execute eaadhar parsing from Eaadhar library
				Response_Eaadhar_Library = Eaadhar_Library.Eaadhar_Parsing(files,request_params['pdf_password'])
				#print(Response_Eaadhar_Library['pdf_data'])
				#sys.exit()
				Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadhar|setDocumentEaadharService| '+json.dumps(Response_Eaadhar_Library['pdf_data']),
					      'Set_Document_Eaadhaar', 'document_process')


				# If response from Response_Eaadhar_Library is true then create object from parsed data
				if Response_Eaadhar_Library:

					Options_Upload_Photo = {}
					Options_Upload_Photo['Format'] = 'jpg'

					# Common request params create dict for common parameters
					Request_Parameters = {}
					Request_Parameters['user_reference_number'] = request_params['user_reference_number']
					Request_Parameters['source_reference_number'] = request_params['source_reference_number']
					Request_Parameters['source'] = request_params['source']
					Request_Parameters['source_type'] = request_params['source_type']

					# There are two parsts of dict User_Photo_Object and User_Decrypted_Pdf_Object(SAME FRONT & BACK)

					# User_Photo_Object is parsed photo from pdf set categiory and type
					User_Photo_Object = dict()
					User_Photo_Object.update(Request_Parameters)
					Request_Parameters_Photo = {}
					Request_Parameters_Photo['document_category_id'] = Eaadhar_Photo_Category_Id
					Request_Parameters_Photo['document_type_id'] = Eaadhar_Photo_Category_Type
					Request_Parameters_Photo['face'] = 'FRONT'
					User_Photo_Object.update(Request_Parameters_Photo)

					Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadhar|setDocumentEaadharService|user-photo-object| '+json.dumps(Request_Parameters_Photo),
					      'Set_Document_Eaadhaar', 'document_process')

					# Upload user photo
					Response_User_Photo = self.uploadDocuments(Response_Eaadhar_Library['crop_pdf_data'],'User_Aadhar_Photo',User_Photo_Object,Options_Upload_Photo)

					# User_Decrypted_Pdf_Object is parsed pdf data from eaadhar name,address,dob etc

					User_Decrypted_Pdf_Object = dict()
					User_Decrypted_Pdf_Object.update(Request_Parameters)
					Request_Parameters_Pdf = {}
					Request_Parameters_Pdf['document_category_id'] = Eaadhar_Pdf_Category_Id
					Request_Parameters_Pdf['document_type_id'] = Eaadhar_Pdf_Category_Type
					Request_Parameters_Pdf['face'] = 'FRONT'
					Options_Upload_Photo['Format'] = 'pdf'
					User_Decrypted_Pdf_Object.update(Request_Parameters_Pdf)

					Core_Object.Write_Logs(str(Unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadhar|setDocumentEaadharService|user-pdf-object| '+json.dumps(Request_Parameters_Pdf),
					      'Set_Document_Eaadhaar', 'document_process')

					# Upload decrypted pdf
					Response_User_Pdf = self.uploadDocuments(Response_Eaadhar_Library['decrypt_pdf_data'],'User_Aadhar_Pdf',User_Decrypted_Pdf_Object,Options_Upload_Photo)


					# Create Extracted data for Aadhar Front PDF
					# Upload same pdf both front and back

					# Create_Extracted_Data_Front is data for Front

					#### Aadhar Front Extract Data START ######
					Create_Extracted_Data_Front = {}
					Create_Extracted_Data_Front['mother_name'] = ''

					# Convert hypen to slash for auto underwriter
					if re.findall(r"\-", Response_Eaadhar_Library['pdf_data']['dob'], re.MULTILINE | re.IGNORECASE | re.DOTALL):

						Response_Eaadhar_Library['pdf_data']['dob'] = re.sub(r"-",'/', Response_Eaadhar_Library['pdf_data']['dob'])

					Get_Birth_Year = Response_Eaadhar_Library['pdf_data']['dob'].split('/')
					Create_Extracted_Data_Front['birth_year'] = {"value":str(Get_Birth_Year[2]),"conf":100}

					Create_Extracted_Data_Front['date_of_birth'] = {"value":Response_Eaadhar_Library['pdf_data']['dob'],"conf":100}
					Create_Extracted_Data_Front['father_name'] = ''
					Create_Extracted_Data_Front['aadhaar_number'] = {"value":Response_Eaadhar_Library['pdf_data']['uid'],"conf":100}
					Create_Extracted_Data_Front['gender'] = {"value":"Male" if str(Response_Eaadhar_Library['pdf_data']['gender']) == "MALE" else "Female","conf":100}
					Create_Extracted_Data_Front['name'] = {"value":Response_Eaadhar_Library['pdf_data']['name'],"conf":100}
					Create_Extracted_Data_Front['document_identification'] = 'aadhar_front'
					Create_Extracted_Data_Front['to_be_reviewed'] = 'no'

					Response_User_Pdf['extracted_data'] = json.dumps(Create_Extracted_Data_Front)


					#### Extracted Data Captured for Aadhar Front END ######


					#### Aadhar Back Extract Data START ######
					# For Auto Underwriter Aadhar Back data stored in aadhaar extracted_data
					Response_User_Pdf_Back = dict()
					Response_User_Pdf_Back.update(Response_User_Pdf)
					Response_User_Pdf_Back['document_reference_number'] = Core_Object.generateUiid()
					Response_User_Pdf_Back['document_face'] = 'BACK'

					Create_Extracted_Data_Back = {}

					Create_Extracted_Data_Back['father_name'] = ''
					Create_Extracted_Data_Back['aadhaar_number'] = {"value":Response_Eaadhar_Library['pdf_data']['uid'],"conf":100}

					Create_Address = {}
					Create_Address['pin'] = Response_Eaadhar_Library['pdf_data']['pc']
					Create_Address['line1'] = Response_Eaadhar_Library['pdf_data']['house']
					Create_Address['line2'] = Response_Eaadhar_Library['pdf_data']['street']
					Create_Address['state'] = Response_Eaadhar_Library['pdf_data']['state']
					Create_Address['street'] = Response_Eaadhar_Library['pdf_data']['street']
					Create_Address['care_of'] = Response_Eaadhar_Library['pdf_data']['co']
					Create_Address['district'] = Response_Eaadhar_Library['pdf_data']['subdist']
					Create_Address['landmark'] = Response_Eaadhar_Library['pdf_data']['lm']
					Create_Address['locality'] = Response_Eaadhar_Library['pdf_data']['loc']
					Create_Address['house_number'] = ''
					Create_Address['conf'] = 100
					Create_Address['city'] = Response_Eaadhar_Library['pdf_data']['vtc']

					Create_Extracted_Data_Back['address'] = Create_Address
					Create_Extracted_Data_Back['pincode'] = {"value":Response_Eaadhar_Library['pdf_data']['pc'],"conf":100}
					Create_Extracted_Data_Back['document_identification'] = 'aadhar_back'
					Create_Extracted_Data_Back['to_be_reviewed'] = 'no'

					Response_User_Pdf_Back['extracted_data'] = json.dumps(Create_Extracted_Data_Back)

					#### Extracted Data Captured for Aadhar BACK END ######

					# if all success return success
					if Document_Model_Object.setDocument(Response_User_Photo,Unique_Id) == True and Document_Model_Object.setDocument(Response_User_Pdf,Unique_Id) == True and Document_Model_Object.setDocument(Response_User_Pdf_Back,Unique_Id) == True:


							# Need to fetch aadhar front id and Photo id from documents table to update in aadhar data table
							Request_Get_Doc_Aadhar_Photo = {"document_reference_number":Response_User_Photo['document_reference_number']}
							Response_Object_Photo = Document_Model_Object.getDocumentList(Request_Get_Doc_Aadhar_Photo) # Model Call


							Request_Get_Doc_Aadhar_Pdf = {"document_reference_number":Response_User_Photo['document_reference_number']}
							Response_Object_Pdf = Document_Model_Object.getDocumentList(Request_Get_Doc_Aadhar_Pdf) # Model Call

							Update_Extra_Aadhar_Data = {"photo_id":Response_Object_Photo[0]['id'],"aadhaar_card_id":Response_Object_Pdf[0]['id'],"authentication_type":"EAADHAR"}
							Response_Eaadhar_Library['pdf_data'].update(Update_Extra_Aadhar_Data)


							Response_Aadhaar_Update = Thirdparty_Service_Class.executeEaadharDataUpdate(request_params, Response_Eaadhar_Library['pdf_data'], Unique_Id)

							Response['success'] = True

							# Doc verify txn-service call (Auto Underwriter callback)
							Thirdparty_Service_Class.executeTxnServiceVerifyDoc(request_params,Unique_Id,'Set_Document_Eaadhaar')


					else:


							Response['error_code'] = 504
							Response['success'] = False

		except Exception as e:

			# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
			# tail -f /var/log/apache2/doc-service/error.log ( production)
			print('Exception Set Document Eaadhaar Old:-'+str(e))
			Core_Object.Write_Logs(str(Unique_Id), ' |service-function|setDocumentEaadhar|setDocumentEaadharService|Exceptions| '+str(e),
				      'Set_Document_Eaadhaar', 'document_process')

			Response['error_code'] = 504
			Response['success'] = False

		return Response


##################################################################################
## function : setDocumentEaadharServiceXml					##
## User: Eaadhar upload and xml parsing of eaadhar				##
## Parameters : files (zip file bytes)		    				##
##              request_params (required params to make entry for xml)		##
##		Uniuq_id : Request Unique identification number x-request-id 	##
##################################################################################
	def setDocumentEaadharServiceXml(self, files, request_params, unique_Id):

		Response = {}

		try:

			try:
				File_Name, Extension = os.path.splitext(files.filename)
				Type = 'file'
			except Exception as E:

				 Extension = '.zip'
				 Type = 'string'

			Request_Format = Extension.replace('.', '')

			# If file is not pdf return false
			if not 'zip' in Request_Format.lower():



				Core_Object.Write_Logs(str(unique_Id) + " | " + str(request_params['source_reference_number']),
									   '|service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|document-is-zip| ',
									   'Set_Document_Eaadhaar_Xml', 'document_process')

				Response['error_code'] = 537
				Response['success'] = False

				return Response

			else:

				if Type == 'string':

					Options_Upload = {}
					files += "=" * ((4 - len(files) % 4) % 4) #ugh

					Check_File = files.encode("ascii")
					files = base64.decodebytes(Check_File)
					files = io.BytesIO(files)

					#Kind = filetype.guess(Check_Extension)

				# Execute eaadhar parsing from Eaadhar library
				Response_Eaadhar_Library = Eaadhar_Library.xmlFileRd(files, request_params['zip_password'])


				files.seek(0) # Close current file for another operation

				User_Photo_Bytes = Response_Eaadhar_Library['xml_image_object']
				del Response_Eaadhar_Library['xml_image_object']
				Core_Object.Write_Logs(str(unique_Id) + " | " + str(request_params['source_reference_number']),
									   '|service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|Response Data | ' + json.dumps(
										   Response_Eaadhar_Library),
									   'Set_Document_Eaadhaar_Xml', 'document_process')



				Aadhar_Data_Dict = {}
				Aadhar_Data_Dict['adhaar_name'] = str(Response_Eaadhar_Library['name'])
				Aadhar_Data_Dict['adhaar_dob'] = str(Response_Eaadhar_Library['dob'])
				Aadhar_Data_Dict['adhaar_gender'] = "Male" if str(Response_Eaadhar_Library['gender']) == "M" else "Female"

				Aadhar_Data_Dict['address_01'] = str(Response_Eaadhar_Library['name'])
				Aadhar_Data_Dict['address_02'] = str(Response_Eaadhar_Library['co'])
				Aadhar_Data_Dict['address_03'] = str(Response_Eaadhar_Library['house'])
				Aadhar_Data_Dict['address_04'] = str(Response_Eaadhar_Library['street'])
				Aadhar_Data_Dict['address_05'] = str(Response_Eaadhar_Library['loc'])
				Aadhar_Data_Dict['address_06'] = str(Response_Eaadhar_Library['lm'])
				Aadhar_Data_Dict['address_07'] = str(Response_Eaadhar_Library['vtc'])
				Aadhar_Data_Dict['address_08'] = str(Response_Eaadhar_Library['subdist'])
				Aadhar_Data_Dict['address_09'] = str(Response_Eaadhar_Library['state'])
				Aadhar_Data_Dict['adhaar_no_01'] = str(request_params['aadhar_number'])
				#Aadhar_Data_Dict['vid_no_01'] = str(Response_Eaadhar_Library['pc'])
				Aadhar_Data_Dict['adhaar_no_02'] = str(request_params['aadhar_number'])
				#Aadhar_Data_Dict['vid_no_02'] = str(Response_Eaadhar_Library['pc'])
				Aadhar_Data_Dict['address_back_01'] = str(Response_Eaadhar_Library['house'])
				Aadhar_Data_Dict['address_back_02'] = str(Response_Eaadhar_Library['street'])
				Aadhar_Data_Dict['address_back_03'] = str(Response_Eaadhar_Library['loc'])+','+str(Response_Eaadhar_Library['lm'])
				Aadhar_Data_Dict['address_back_04'] = str(Response_Eaadhar_Library['vtc'])+','+str(Response_Eaadhar_Library['subdist'])+','+str(Response_Eaadhar_Library['state'])
				Aadhar_Data_Dict['adhaar_no_03'] = str(request_params['aadhar_number'])
				#Aadhar_Data_Dict['vid_no_03'] = str(Response_Eaadhar_Library['pc'])

				#Aadhar_Data_Dict['address_11'] = str(Response_Eaadhar_Library['dob'])

				Fillable_Aadhaar_Bytes = FillablePdf_Library.fillableAadharForm(Aadhar_Data_Dict,User_Photo_Bytes)


				# If response from Response_Eaadhar_Library is true then create object from parsed data
				if Response_Eaadhar_Library:

					Options_Upload_Photo = {}
					Options_Upload_Photo['Format'] = 'jpg'

					Request_Parameters = {}
					Request_Parameters['user_reference_number'] = request_params['user_reference_number']
					Request_Parameters['source_reference_number'] = request_params['source_reference_number']
					Request_Parameters['source'] = request_params['source']
					Request_Parameters['source_type'] = request_params['source_type']
					Request_Parameters['screening_status'] = 'APPROVED'

					# There are two parsts of dict User_Photo_Object and User_Decrypted_Pdf_Object

					# User_Photo_Object is parsed photo from pdf set categiory and type
					User_Photo_Object = dict()
					User_Photo_Object.update(Request_Parameters)
					Request_Parameters_Photo = {}
					Request_Parameters_Photo['document_category_id'] = Eaadhar_Photo_Category_Id
					Request_Parameters_Photo['document_type_id'] = Eaadhar_Photo_Category_Type
					Request_Parameters_Photo['face'] = 'FRONT'
					User_Photo_Object.update(Request_Parameters_Photo)

					Core_Object.Write_Logs(str(unique_Id) + " | " + str(request_params['source_reference_number']),
									   '|service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|user-photo-object| ' + json.dumps(
										   Response_Eaadhar_Library),
									   'Set_Document_Eaadhaar_Xml', 'document_process')

					# Upload user photo
					Response_User_Photo = self.uploadDocuments(User_Photo_Bytes,'User_Aadhar_Photo', User_Photo_Object, Options_Upload_Photo)

					Response_Eaadhar_Library['uid'] = request_params['aadhar_number']
					# User_Decrypted_Pdf_Object is parsed pdf data from eaadhar name,address,dob etc


					User_Decrypted_Pdf_Object = dict()
					User_Decrypted_Pdf_Object.update(Request_Parameters)
					Request_Parameters_Pdf = {}
					Request_Parameters_Pdf['document_category_id'] = Eaadhar_Pdf_Category_Id
					Request_Parameters_Pdf['document_type_id'] = Eaadhar_Pdf_Category_Type
					Request_Parameters_Pdf['face'] = 'FRONT'

					#Request_Parameters_Pdf['extracted_data'] = 'FRONT'
					Options_Upload_Photo['Format'] = 'pdf'
					User_Decrypted_Pdf_Object.update(Request_Parameters_Pdf)

					Core_Object.Write_Logs(str(unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|user-pdf-object| '+json.dumps(Request_Parameters_Pdf),
					      'Set_Document_Eaadhaar_Xml', 'document_process')

					# Upload decrypted pdf
					Response_User_Pdf = self.uploadDocuments(Fillable_Aadhaar_Bytes,'User_Aadhar_Pdf',User_Decrypted_Pdf_Object,Options_Upload_Photo)

					# For Auto Underwriter Aadhar Front data stored in aadhaar extracted_data
					Create_Extracted_Data_Front = {}
					Get_Birth_Year = Response_Eaadhar_Library['dob'].split('-')
					Create_Extracted_Data_Front['birth_year'] = {"value":str(Get_Birth_Year[2]),"conf":100}
					Create_Extracted_Data_Front['mother_name'] = ''

					# Convert hypen to slash for auto underwriter
					if re.findall(r"\-", Response_Eaadhar_Library['dob'], re.MULTILINE | re.IGNORECASE | re.DOTALL):

						Response_Eaadhar_Library['dob'] = re.sub(r"-",'/', Response_Eaadhar_Library['dob'])
					# Converted in proper datetime format from here. date format converted in yyyy-mm-dd format
					Dob_date_convert = Response_Eaadhar_Library['dob']
					Create_Extracted_Data_Front['date_of_birth'] = {"value":Dob_date_convert,"conf":100}
					Create_Extracted_Data_Front['father_name'] = ''
					Create_Extracted_Data_Front['aadhaar_number'] = {"value":request_params['aadhar_number'],"conf":100,"ismasked":"no"}
					Create_Extracted_Data_Front['gender'] = {"value":"Male" if str(Response_Eaadhar_Library['gender']) == "M" else "Female","conf":100}
					Create_Extracted_Data_Front['name'] = {"value":Response_Eaadhar_Library['name'],"conf":100}
					Create_Extracted_Data_Front['document_identification'] = 'aadhar_front'
					Create_Extracted_Data_Front['to_be_reviewed'] = 'no'
					Create_Extracted_Data_Front['is_eaadhaar'] = 'yes'


					#Store doc ref number of user photo fetched from aadhaar xml base64 inside Aaadhar Front PDF
					Create_Extracted_Data_Front['user_photo_reference_number'] = Response_User_Photo['document_reference_number']
					Response_User_Pdf['extracted_data'] = json.dumps(Create_Extracted_Data_Front)

					# Store doc ref number of user front aadhar pdf into aadhaar user photo to create linkage between both of the document
					Response_User_Photo['extracted_data'] = json.dumps({'user_aadhaar_front_reference_number':Response_User_Pdf['document_reference_number']})

					# For Auto Underwriter Aadhar Back data stored in aadhaar extracted_data
					Response_User_Pdf_Back = dict()
					Response_User_Pdf_Back.update(Response_User_Pdf)
					Response_User_Pdf_Back['document_reference_number'] = Core_Object.generateUiid()
					Response_User_Pdf_Back['document_face'] = 'BACK'

					Create_Extracted_Data_Back = {}

					Create_Extracted_Data_Back['father_name'] = ''
					Create_Extracted_Data_Back['aadhaar_number'] = {"value":request_params['aadhar_number'],"conf":100,"ismasked":"no"}

					Create_Address = {}
					Create_Address['pin'] = Response_Eaadhar_Library['pc']
					Create_Address['line1'] = Response_Eaadhar_Library['house']
					Create_Address['line2'] = Response_Eaadhar_Library['street']
					Create_Address['state'] = Response_Eaadhar_Library['state']
					Create_Address['street'] = Response_Eaadhar_Library['street']
					Create_Address['care_of'] = Response_Eaadhar_Library['co']
					Create_Address['district'] = Response_Eaadhar_Library['subdist']
					Create_Address['landmark'] = Response_Eaadhar_Library['lm']
					Create_Address['locality'] = Response_Eaadhar_Library['loc']
					Create_Address['house_number'] = ''
					Create_Address['conf'] = 100
					Create_Address['city'] = Response_Eaadhar_Library['vtc']

					Create_Extracted_Data_Back['address'] = Create_Address
					Create_Extracted_Data_Back['pincode'] = {"value":Response_Eaadhar_Library['pc'],"conf":100}
					Create_Extracted_Data_Back['document_identification'] = 'aadhar_back'
					Create_Extracted_Data_Back['to_be_reviewed'] = 'no'
					Create_Extracted_Data_Back['is_eaadhaar'] = 'yes'

					Response_User_Pdf_Back['extracted_data'] = json.dumps(Create_Extracted_Data_Back)

					Response_User_Pdf_Back['underwriter_status'] = "APPROVE"

					# Undo date changes to work with db coloumn
					if re.findall(r"\/", Response_Eaadhar_Library['dob'], re.MULTILINE | re.IGNORECASE | re.DOTALL):

						Response_Eaadhar_Library['dob'] = re.sub(r"/",'-', Response_Eaadhar_Library['dob'])



					User_Aadhaar_Zip = dict()
					User_Aadhaar_Zip.update(Request_Parameters)

					Request_Parameters_Pdf_Zip = {}
					Request_Parameters_Pdf_Zip['document_category_id'] = Document_Category_Aadhaar_Zip
					Request_Parameters_Pdf_Zip['document_type_id'] = Document_Type_Aadhaar_Zip
					Request_Parameters_Pdf_Zip['face'] = 'FRONT'
					Request_Parameters_Pdf_Zip['pdf_password'] = request_params['zip_password']
					Options_Upload_Photo['Format'] = 'zip'
					User_Aadhaar_Zip.update(Request_Parameters_Pdf_Zip)

					Core_Object.Write_Logs(str(unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadhar|setDocumentEaadharService|user-pdf-zip| '+json.dumps(Request_Parameters_Pdf),
					      'Set_Document_Eaadhaar', 'document_process')


					# Upload decrypted pdf
					Response_User_Pdf_Zip = self.uploadDocuments(files.read(),'User_Offline_Aadhaar_Zip',User_Aadhaar_Zip,Options_Upload_Photo)



					Core_Object.Write_Logs(str(unique_Id)+" | "+str(request_params['source_reference_number']), '|service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|final-response-library| '+json.dumps(Response_Eaadhar_Library),
					      'Set_Document_Eaadhaar_Xml', 'document_process')


					#Core_Object.generateUiid()

					# if both success return success
					if Document_Model_Object.setDocument(Response_User_Photo,unique_Id) == True and Document_Model_Object.setDocument(Response_User_Pdf,unique_Id) == True and Document_Model_Object.setDocument(Response_User_Pdf_Back,unique_Id) == True and Document_Model_Object.setDocument(Response_User_Pdf_Zip,unique_Id) == True:

						Request_Get_Doc_Aadhar_Photo = {"document_reference_number":Response_User_Photo['document_reference_number']}
						Response_Object_Photo = Document_Model_Object.getDocumentList(Request_Get_Doc_Aadhar_Photo) # Model Call


						Request_Get_Doc_Aadhar_Pdf = {"document_reference_number":Response_User_Pdf['document_reference_number']}
						Response_Object_Pdf = Document_Model_Object.getDocumentList(Request_Get_Doc_Aadhar_Pdf) # Model Call

						Update_Extra_Aadhar_Data = {"photo_id":Response_Object_Photo[0]['id'],"aadhaar_card_id":Response_Object_Pdf[0]['id'],"authentication_type":"EAADHAR"}
						Response_Eaadhar_Library.update(Update_Extra_Aadhar_Data)

						Thirdparty_Service_Response = Thirdparty_Service_Class.executeEaadharDataUpdate(request_params, Response_Eaadhar_Library, unique_Id)


						# check fast cash data here and insert and update data in tbl_fastbanking_document_digital_data
						request_params_data = json.loads(json.dumps(request_params))

						# Check source key is present or not in request parameters. Below code are workinig for only Fastcash.

						if 'source' in request_params_data.keys() and request_params_data['source'] == 'RUFILO_APP':

							fastcash_dict = {}
							fastcash_dict['aadhar_reference_number'] = Thirdparty_Service_Response['data']['aadhaar-details']['aadhaar_reference_number']
							fastcash_dict['address_reference_number'] = Thirdparty_Service_Response['data']['aadhaar-details']['address_reference_number']
							fastcash_dict['birth_year'] = Create_Extracted_Data_Front['birth_year']['value']
							fastcash_dict['date_of_birth'] = datetime.strptime(Dob_date_convert, "%d/%m/%Y").strftime("%Y-%m-%d")
							fastcash_dict['digital_reference_number'] = 'OCR'+Core_Object.generateUiid()
							fastcash_dict['gender'] = Create_Extracted_Data_Front['gender']['value']
							fastcash_dict['name'] = Create_Extracted_Data_Front['name']['value']
							fastcash_dict['photo_document_reference_number'] = Response_User_Photo['document_reference_number']
							fastcash_dict['response'] = json.dumps(request_params_data)
							fastcash_dict['user_identity_number'] = Create_Extracted_Data_Front['aadhaar_number']['value']
							fastcash_dict['user_identity_number_back'] = Create_Extracted_Data_Front['aadhaar_number']['value']
							fastcash_dict['user_reference_number'] = request_params_data['user_reference_number']
							fastcash_dict['document_reference_number'] =  Response_User_Pdf['document_reference_number']
							fastcash_dict['document_reference_number_back'] =  Response_User_Pdf_Back['document_reference_number']
							fastcash_dict['transaction_reference_number'] =  request_params_data['source_reference_number']
							# Make a object from here and pass to model for processing data in DB
							Document_Model_Object.insertUpdateFastcashData(fastcash_dict,unique_Id)
							Core_Object.Write_Logs(str(unique_Id)+" | "+str(request_params_data['source_reference_number']), '|service-function|setDocumentEaadhar|setDocumentEaadharService|FASTCASH '+json.dumps(fastcash_dict),
					      'Fastcash_insert_update_obj_process', 'Fastcash_Logs')


						else:

							Thirdparty_Service_Class.executeTxnServiceVerifyDoc(request_params,unique_Id,'Set_Document_Eaadhaar_Xml')

						Response['success'] = True
						# Doc verify txn-service call (Auto Underwriter callback)



					else:

						Response['error_code'] = 538
						Response['success'] = False

		except Exception as e:


			# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
			# tail -f /var/log/apache2/doc-service/error.log ( production)
			print('Exception Set Document Eaadhaar XML:-'+str(sys.exc_info()[-1].tb_lineno)+'   '+str(e))

			Core_Object.Write_Logs(str(unique_Id), ' |service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|Exceptions| Line Number : '+str(sys.exc_info()[-1].tb_lineno)+'|Message '+str(e),
				      'Set_Document_Eaadhaar_Xml', 'document_process')

			Response['error_code'] = 539
			Response['success'] = False

		return Response

##################################################################################
## function : uploadDocuments						    	##
## User: Sub module function which includes under many main function		##
## Parameters : filesObject (file bytes)		    			##
##              request_params (required params to make entry of document)	##
##		options : option to upload doc				 	##
##################################################################################

	def uploadDocuments(self,filesObject,file_name,request_params,options):

		Request_Object = {}

		try:
			# Create directory
			Raw_Directory_User = str(request_params['user_reference_number'])+str(Application_Salt)
			Has_String = Core_Object.returnHashString(Raw_Directory_User)

			options['Bucket_Key'] = Bucket_Dir+'/'+request_params['user_reference_number']+'/'+Has_String
			Request_Object['document_reference_number'] = Core_Object.generateUiid()

			# Create file name
			Filename =  file_name+'_'+str(Request_Object['document_reference_number'])

			# Upload on AWS using from AWS library function
			Uploaded_Filename = Amazon_Library.Upload_Document_S3(filesObject,options,Filename)

			# Get Document Category By Type Id
			Get_Document_Category_By_Doctype = Document_Model_Object.getDocumentType(request_params['document_type_id'])

			Request_Object[Document_Table_Fields['user_reference_number']] = request_params['user_reference_number']
			Request_Object[Document_Table_Fields['source_reference_number']] = request_params['source_reference_number']
			Request_Object[Document_Table_Fields['source']] = request_params['source']
			Request_Object[Document_Table_Fields['document_category_id']] = Get_Document_Category_By_Doctype[0]['document_category']
			Request_Object[Document_Table_Fields['document_type_id']] = request_params['document_type_id']
			Request_Object[Document_Table_Fields['face']] = request_params['face']
			Request_Object['document_url'] = Uploaded_Filename
			Request_Object[Document_Table_Fields['source_type']] = request_params['source_type']

			"""if 'is_discarded' in request_params and request_params['is_discarded']:

				Request_Object['is_discarded'] = request_params['is_discarded']
			"""
			if 'extracted_data' in request_params and request_params['extracted_data']:

				Request_Object['extracted_data'] = request_params['extracted_data']

			if 'screening_status' in request_params and request_params['screening_status']:

				Request_Object['screening_status'] = request_params['screening_status']

			if 'underwriter_status' in request_params and request_params['underwriter_status']:

				Request_Object['underwriter_status'] = request_params['underwriter_status']

			if 'rework_reason' in request_params and request_params['rework_reason']:

				Request_Object['rework_reason'] = str(request_params['rework_reason'])

				Current_Timestamp = datetime.fromtimestamp(datetime.now().timestamp())
				Decision_Time = Current_Timestamp.strftime("%Y-%m-%d %H:%M:%S")

				Request_Object['decision_time'] = Decision_Time

			if 'doc_unique_id' in request_params and request_params['doc_unique_id']:

				Request_Object['doc_unique_id'] = request_params['doc_unique_id']

			if 'blur_variance' in request_params and request_params['blur_variance']:

				Request_Object['blur_variance'] = request_params['blur_variance']


			Hostname = urlparse(request.base_url)
			Request_Object['decision_by_subuser_id'] = '3874'

			if Hostname.hostname == '127.0.0.1' or Hostname.hostname == 'doc-service.test.rufilo.com':

				Request_Object['decision_by_subuser_id'] = '193'


			if 'pdf_password' in request_params and request_params['pdf_password']:

				Request_Object['document_password'] = request_params['pdf_password']


			return Request_Object

		except Exception as e:

			print('Exception Set Uploadcoeumtns:-'+str(sys.exc_info()[-1].tb_lineno)+'   '+str(e))
			#Core_Object.Write_Logs(str(unique_Id), ' |service-function|setDocumentEaadharXml|setDocumentEaadharServiceXml|Exceptions| '+str(e),
				      #'Set_Document_Eaadhaar_Xml', 'document_process')

			Fail_Response = {}
			Fail_Response['error_code'] = 522
			Fail_Response['success'] = False

			return Fail_Response


##################################################################################
## function : updateDocumentUnderwritingStatusService				##
## service function used to update underwriting into document table		##
## Parameters : rework_reason (file bytes)		    			##
##              underwriter_status (required params to make entry of document)	##
##		document_reference_number					##
##		decision_by_subuser_id (number / id)				##
##		source								##
##		user_reference_number						##
##################################################################################

	def updateDocumentUnderwritingStatusService(self,request_parameters,unique_id):

		Response = {}
		try:

			Fail_Response = {}


			if request_parameters['underwriter_status'] == 'REWORK' and ('rework_reason' not in request_parameters or request_parameters['rework_reason'] == ''):

				Fail_Response['error_code'] = 518
				Fail_Response['success'] = False
				return Fail_Response


			Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatus|updateDocumentUnderwritingStatusService|Request Params| '+json.dumps(request_parameters),
					      'Update_Underwriter_Status', 'document_process')


			Selector_Doc_Ref_Number = request_parameters['document_reference_number']
			Update_Object = {}

			for Key,Values in request_parameters.items():

				if not 'document_reference_number' in Key:

						Update_Object[Key] = Values

			Current_Timestamp = datetime.fromtimestamp(datetime.now().timestamp())
			Decision_Time = Current_Timestamp.strftime("%Y-%m-%d %H:%M:%S")

			Update_Object['decision_time'] = Decision_Time


			if request_parameters['source'] and request_parameters['source'] == 'MMT':



				#
				Thirdparty_Service_Class.executeEventApiMmt(request_parameters,unique_id)


			if 'source' in Update_Object:


				del(Update_Object['source'])



			Model_Response = Document_Model_Object.updateUnderwritingStatus(Selector_Doc_Ref_Number,Update_Object,unique_id)

			# Select document of aadhaar front to approve aadhaar user photo
			Request_Object = {}
			Request_Object['document_reference_number'] = request_parameters['document_reference_number']
			Request_Object['document_category'] = '2'
			Request_Object['document_type'] = '3'

			Response_Object = Document_Model_Object.getDocumentList(Request_Object) # Model Call

			if Response_Object:

				Get_Extracted_Data_Aadhaar = json.loads(Response_Object[0]['extracted_data'])
				if 'user_photo_reference_number' in Get_Extracted_Data_Aadhaar and Get_Extracted_Data_Aadhaar['user_photo_reference_number']:

					Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatus|updateDocumentUnderwritingStatusService|Update Eaadhaar Photo To Approve| ',
					      'Update_Underwriter_Status', 'document_process')

					Update_Aadhaar_Photo_Status = Document_Model_Object.updateUnderwritingStatus(Get_Extracted_Data_Aadhaar['user_photo_reference_number'],Update_Object,unique_id)




			if Model_Response == True:


				Response['success'] = True


			else:

				Response['success'] = False
				Response['error_code'] = 519


		except Exception as e:

				# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
				# tail -f /var/log/apache2/doc-service/error.log ( production)

				print('Exception updateDocumentUnderwritingStatusService:-'+str(e))
				Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatus|updateDocumentUnderwritingStatusService|Exceptions| '+str(e),
				      'Update_Underwriter_Status', 'document_process')

				Response['success'] = False
				Response['error_code'] = 520



		return Response

##################################################################################
## function : verifyDocumentsWithPhoto						##
## service function used to verify id proof photo with selfie 			##
##	documents fetch by source reference number				##
## Parameters : source_reference_number			    			##
##################################################################################

	def verifyDocumentsWithPhoto(self,request_parameters,unique_id):

		Get_Source_Reference =  request_parameters['source_reference_number']

		Response = {}
		try:

			Get_Id_Proof = []
			Get_Selfie = []
			if Get_Source_Reference:

				Request_Object = {}
				Request_Object['source_reference_number'] = Get_Source_Reference
				#Request_Object['underwriter_status'] = 'APPROVE'
				Response_Object = Document_Model_Object.getDocumentList(Request_Object)

				Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |service-function|verifyDocumentesWithSelfie|verifyDocumentsWithPhoto| '+str(Core_Object.returnJsonForLogs(Response_Object)),
				      'Face_Verify_Documents', 'document_process')


				Core_Object.returnJsonForLogs(Response_Object)

				for Extract_Data in Response_Object:

					if str(Extract_Data['document_type']) in Face_Verify_Enabled_Type_Id and Extract_Data['document_face'] == 'FRONT' and Extract_Data['underwriter_status'] in ['APPROVE','NOT_SEEN']:


						Get_Id_Proof.append(Extract_Data)


					if str(Extract_Data['document_type']) in Selfie_Document_Type:


						Get_Selfie.append(Extract_Data)


			if len(Get_Selfie) > 0 and len(Get_Id_Proof) > 0:

				Get_Latest_Selfie_Object = Get_Selfie[0]
				#Amazon_Library.Create_Presigned_Url(Response_Object[Counter]['document_url'])
				Create_Presigned_Selfie_Image_Url = ImageProcess_Library.convertToBytes(Amazon_Library.Create_Presigned_Url(Get_Latest_Selfie_Object['document_url']),2)
				Size_Selfie = ImageProcess_Library.getFileSizeFromCv2(Create_Presigned_Selfie_Image_Url)

				Final_Response_Object = {}
				for Id_Key in Get_Id_Proof:


						Split_Document_Url = Id_Key['document_url'].split('.')
						Source_Reference_Number = Id_Key['source_reference_number']
						Document_Reference_Number = Id_Key['document_reference_number']

						# Eaadhar always comes with pdf skip eaadhar for selfie match for now
						if not Split_Document_Url[1] == 'pdf':


							Id_Image_Object = ImageProcess_Library.convertToBytes(Amazon_Library.Create_Presigned_Url(Id_Key['document_url']),2)

							Extra_Parameters = {}
							Extra_Parameters['user_reference_number'] = Id_Key['user_reference_number']

							Size_Id = ImageProcess_Library.getFileSizeFromCv2(Id_Image_Object)

							Logs_Params = {}
							Logs_Params['unique_id'] = unique_id
							Logs_Params['source_reference_number'] = Source_Reference_Number

							Total_Size_Calculated = round((Size_Id+Size_Selfie) / 1048576)

							# Asynch call to update shadow extracted data
							try:

								_post_data = {}
								_post_data['selfie_document_reference_number'] = Get_Latest_Selfie_Object['document_reference_number']
								extracted_data_shadow_call = Thirdparty_Service_Class.postInternalFaceVerify(ImageProcess_Library.convertCvtoBytes(Create_Presigned_Selfie_Image_Url,Total_Size_Calculated),ImageProcess_Library.convertCvtoBytes(Id_Image_Object,Total_Size_Calculated),_post_data)

							except Exception as E:

								print(E)
								pass

							# Response = Hyperverge_Library.verifyFaceWithId(ImageProcess_Library.convertCvtoBytes(Id_Image_Object,Total_Size_Calculated),ImageProcess_Library.convertCvtoBytes(Create_Presigned_Selfie_Image_Url,Total_Size_Calculated),Extra_Parameters,Logs_Params)
							Response = Amazon_Library.Compare_Faces(ImageProcess_Library.convertCvtoBytes(Id_Image_Object, Total_Size_Calculated), ImageProcess_Library.convertCvtoBytes(Create_Presigned_Selfie_Image_Url, Total_Size_Calculated))
							Updated_Amazon_Response = {}

							if len(Response['FaceMatches']) > 0:
								Updated_Amazon_Response['conf'] = Response['FaceMatches'][0].get('Face').get('Confidence')
							else:
								Updated_Amazon_Response['conf'] = 0
							if len(Response['FaceMatches']) > 0:
								Updated_Amazon_Response['match'] = 'yes'
							else:
								Updated_Amazon_Response['match'] = 'no'

							Updated_Amazon_Response['category_id'] = Id_Key['document_category']
							Updated_Amazon_Response["is_eaadhaar"] = "no"

							if len(Response['FaceMatches']) > 0:
								Updated_Amazon_Response['match-score'] = Response['FaceMatches'][0].get('Similarity')
							else:
								Updated_Amazon_Response['match-score'] = 0

							Updated_Amazon_Response['category_type'] = Id_Key['document_type']
							Updated_Amazon_Response['to_be_reviewed'] = 'no'

							# , Extra_Parameters, Logs_Params

							# _insert_logs_hyperverge = {}
							# _insert_logs_hyperverge['api_function_name'] = 'face_verify'
							# _insert_logs_hyperverge['user_reference_number'] = Id_Key['user_reference_number']
							# _insert_logs_hyperverge['api_request'] = json.dumps({"path":"faceVerify"})
							# _insert_logs_hyperverge['api_response'] = json.dumps(Response)
							# _insert_logs_hyperverge['transaction_reference_number'] = request_parameters['source_reference_number']
							# _insert_logs_hyperverge['transaction_id'] = 0
							#
							# Document_Model_Object.insertHypervergeHitLogs(_insert_logs_hyperverge,unique_id)

							# Response['category_id'] = Id_Key['document_category']
							# Response['category_type'] = Id_Key['document_type']

							# Final_Response_Object[Document_Reference_Number] =  Response
							Final_Response_Object[Document_Reference_Number] = Updated_Amazon_Response

						elif Split_Document_Url[1] == 'pdf':

							Response['match'] = 'yes'
							Response['match-score'] = '100'
							Response['conf'] = '100'
							Response['to_be_reviewed'] = 'no'
							Response['is_eaadhaar'] = 'yes'
							Response['category_id'] = Id_Key['document_category']
							Response['category_type'] = Id_Key['document_type']

							Final_Response_Object[Document_Reference_Number] = Response


				Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |service-function|verifyDocumentesWithSelfie|verifyDocumentsWithPhoto| '+str(Core_Object.returnJsonForLogs(Final_Response_Object)),
				      'Face_Verify_Documents', 'document_process')


				if Final_Response_Object:

					Update_Object = {}

					Selector_Doc_Ref_Number = Get_Latest_Selfie_Object['document_reference_number']
					Update_Object['extracted_data'] = json.dumps(Final_Response_Object)
					Update_Object['screening_status'] = 'APPROVED'

					Model_Response = Document_Model_Object.updateUnderwritingStatus(Selector_Doc_Ref_Number,Update_Object,unique_id)


					if Model_Response:

						Response['success'] = True

					else:

						Response['success'] = False
						Response['error_code'] = 524


					Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |model-response|verifyDocumentesWithSelfie|verifyDocumentsWithPhoto| '+str(Model_Response),
				      'Face_Verify_Documents', 'document_process')


				else:


					Response['success'] = False
					Response['error_code'] = 523
			else:


				Response['success'] = False
				Response['error_code'] = 523


		except Exception as e:

			# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
			# tail -f /var/log/apache2/doc-service/error.log ( production)

			print('Exception verifyDocumentsWithPhoto:-'+str(e)+' '+str(sys.exc_info()[-1].tb_lineno))
			Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |exception|verifyDocumentesWithSelfie|verifyDocumentsWithPhoto| '+str(e),
				      'Face_Verify_Documents', 'document_process')

			Response['success'] = False
			Response['error_code'] = 523

		return Response


##################################################################################
## function : genrateAllFillablePdf						##
## service function used to generate fillable application form 			##
##										##
## Parameters : source_reference_number						##
##		user_reference_number						##
##		create_forcefully (Yes:Application form will generate new entry)##
## 			    	   No : Last created entry will be return	##
##		form_type : (Optional ESIGN | SELFIESIGN)			##
##################################################################################
	def genrateAllFillablePdf(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|',
				      'Genrate_Fillable_Pdf', 'document_process')

					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Transaction_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id,'/extended-details')


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|transaction-service-response|'+Core_Object.returnJsonForLogs(Transaction_Response),
					      'Genrate_Fillable_Pdf', 'document_process')

					Filename = 'Fillable_Application_Form_'+str(request_parameters['source_reference_number'])
					Get_Finaner_Name = 'SiCreva'
					if Transaction_Response['data']['transaction']['assigned_financier_id'] in Assigned_Financer_Id.keys():

						Get_Finaner_Name = Assigned_Financer_Id[Transaction_Response['data']['transaction']['assigned_financier_id']]
						if Get_Finaner_Name == 'Mass':

							return self.generateFillablePdfMass(request_parameters,Unique_Id)


						Filename = Get_Finaner_Name+'_Fillable_Application_Form_'+str(request_parameters['source_reference_number'])

					# For now Fix fedfina form generation
					#Transaction_Response['data']['transaction']['assigned_financier_id'] = 10
					#Filename = 'FedFina_Fillable_Application_Form_'+str(request_parameters['source_reference_number'])
					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'


					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):


						Response['success'] = True
						Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|pdf-exists|'+Core_Object.returnJsonForLogs(Response),
					      'Genrate_Fillable_Pdf', 'document_process')

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:


							return Response



					# Get Transaction SKU Details
					Transaction_Sku_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id,'/get-sku')

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|transaction-sku-service-response|'+Core_Object.returnJsonForLogs(Transaction_Sku_Response),
					      'Genrate_Fillable_Pdf', 'document_process')




					Users_Request_Params = {}
					Users_Request_Params['user_reference_number'] = Transaction_Response['data']['transaction']['user_reference_number']

					# Get User Details
					Users_Response = Thirdparty_Service_Class.executeGetUsersApi(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|user-service-response|'+Core_Object.returnJsonForLogs(Users_Response),
					      'Genrate_Fillable_Pdf', 'document_process')


					# Get User Present Address
					User_Present_Address = Thirdparty_Service_Class.executeGetUsersPresentAddress(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|user-present-address-response|'+Core_Object.returnJsonForLogs(User_Present_Address),
					      'Genrate_Fillable_Pdf', 'document_process')

					# Get User Employment Details
					Emplyment_Details = Thirdparty_Service_Class.executeGetEmplymentDetails(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|employment-response|'+Core_Object.returnJsonForLogs(Emplyment_Details),
					      'Genrate_Fillable_Pdf', 'document_process')




					Merchant_Details = Thirdparty_Service_Class.executeGetMerchantDetails(Transaction_Response['data']['transaction'],Unique_Id)
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|merchant-response|'+Core_Object.returnJsonForLogs(Merchant_Details),
					      'Genrate_Fillable_Pdf', 'document_process')

					Create_Data_Dicts = {}

					# All Data ponits collected inside single variable
					Transaction_Data = Transaction_Response['data']['transaction']
					Users_Data = Users_Response['data']['user']
					Users_Address_Data = User_Present_Address['data']['address']
					#Emplyment_Details_Data = Emplyment_Details['data']['employment_detail']
					Transaction_Sku_Data = 	Transaction_Sku_Response['data']['sku']
					Merchant_Data = Merchant_Details['data']['merchant']


					Kissht_Date = datetime.strptime(Transaction_Data['created_at'], '%Y-%m-%d %H:%M:%S')
					Create_Kissht_Date = str(Kissht_Date.day) +' / '+str(Kissht_Date.month)+' / '+str(Kissht_Date.year)
					Create_Data_Dicts['user_name'] = Users_Data['first_name']+' '+Users_Data['last_name']

					Create_Data_Dicts['user_date'] = Create_Kissht_Date
					Create_Data_Dicts['fullname'] = Users_Data['first_name']+' '+Users_Data['last_name']
					Dob_Date = datetime.strptime(Users_Data['dob'], '%Y-%m-%d')
					Create_Dob_Date = str(Dob_Date.day) +'-'+str(Dob_Date.month)+'-'+str(Dob_Date.year)

					Create_Data_Dicts['date_of_birth'] = Create_Dob_Date

					Create_Data_Dicts['pan_card_no'] = Users_Data['pan']
					Create_Data_Dicts['aadhaar_no'] = Users_Data['aadhaar']

					# Removed on request
					Create_Data_Dicts['phone_number'] = Users_Data['mobile_number']
					Create_Data_Dicts['email_id'] = Users_Data['email']

					Create_Data_Dicts['pincode'] = Users_Address_Data['pincode']
					Create_Data_Dicts['city'] = Users_Address_Data['city']
					Create_Data_Dicts['state'] = Users_Address_Data['state']

					Place = str(Users_Address_Data['city'])
					if Get_Finaner_Name == 'FedFina':

						Place = 'Mumbai'

					Create_Data_Dicts['place'] = Place
					Current_Timestamp = datetime.fromtimestamp(datetime.now().timestamp())
					Current_Date_Form = Current_Timestamp.strftime("%d-%m-%Y %I:%M %P")

					Create_Data_Dicts['kissht_date2'] = Current_Date_Form

					Create_Data_Dicts['address'] = (str(Users_Address_Data['room_number'])+', ' if Users_Address_Data['room_number'] is not None else '')+str(Users_Address_Data['line_1'])

					if Users_Address_Data['line_2'] is not  None:
						Create_Data_Dicts['address2'] = (str(Users_Address_Data['line_2'])+', ' if Users_Address_Data['line_2'] is not None else '') + str(Users_Address_Data['landmark'])


					Create_Data_Dicts['merchant_name'] = Merchant_Data['company_name']
					#Create_Data_Dicts['merchant_code'] = Merchant_Data['merchant_id']
					Create_Data_Dicts['rufilo_id'] = Transaction_Data['fb_transaction_id']


					Create_Data_Dicts['kissht_date'] = Create_Kissht_Date
					Create_Data_Dicts['loan_product_value'] = str(Transaction_Data['product_value'])
					Create_Data_Dicts['loan_downpayment_amount'] = str(Transaction_Data['down_payment_amount'])
					Create_Data_Dicts['loan_loan_amount'] = str(Transaction_Data['loan_amount'])
					Create_Data_Dicts['loan_processing_fees'] = str(Transaction_Data['processing_fees_amount_with_gst'])
					Create_Data_Dicts['loan_emi_amount'] = str(Transaction_Data['instalment_amount'] )
					Create_Data_Dicts['loan_no_of_emis'] = str(Transaction_Data['instalment_no_months'])
					Create_Data_Dicts['loan_rate_interest'] = str(Transaction_Data['interest_component'])
					Create_Data_Dicts['loan_interest_rate'] = str(Transaction_Data['interest'])
					Create_Data_Dicts['loan_total_interest_amount'] = str(Transaction_Data['interest_amount'])
					Create_Data_Dicts['facilitation_charges'] = 'Rs.'+str(0) if Transaction_Data['initiation_fees_amount_with_gst'] == 0 else 'Rs.'+str(Transaction_Data['initiation_fees_amount_with_gst'])


					Counter_Sku_Count = 1
					for Sku_Data in Transaction_Sku_Data:

						Create_Data_Dicts['product_sku_code'+str(Counter_Sku_Count)] = str(Sku_Data['sku_code'])
						Create_Data_Dicts['product_description'+str(Counter_Sku_Count)] = str(Sku_Data['sku_description'])
						Counter_Sku_Count += 1


					Create_Checkbox_Dicts = {}

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|final-object-response|'+Core_Object.returnJsonForLogs(Create_Data_Dicts),
					      'Genrate_Fillable_Pdf', 'document_process')

					if Users_Data['employment_type']:

						if Users_Data['employment_type'] == 'salaried':

							Create_Checkbox_Dicts['occupation_salaried'] = 'Yes'

						else:

							Create_Checkbox_Dicts['occupation_self_employed'] = 'Yes'


					if Users_Data['gender'] == 'MALE':

						Create_Checkbox_Dicts['gendar_male'] = 'Yes'

					if Users_Data['gender'] == 'FEMALE':

						Create_Checkbox_Dicts['gendar_female'] = 'Yes'

					if Users_Data['residence_type']:

						if Users_Data['residence_type'] == 'OWNED':

							Create_Checkbox_Dicts['residence_type_owned'] = 'Yes'

						else:

							Create_Checkbox_Dicts['residence_type_rented'] = 'Yes'



					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'


					#Filename = 'Fillable_Application_Form_'+str(request_parameters['source_reference_number'])

					Bytes = FillablePdf_Library.fillableApplicationForm(Create_Data_Dicts,Create_Checkbox_Dicts,Transaction_Response['data']['transaction']['assigned_financier_id'])
					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Bytes,Options,Filename)

					Response['success'] = True
					Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

					return Response

			except Exception as e:

					# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
					# tail -f /var/log/apache2/doc-service/error.log ( production)

					print('Exception genrateAllFillablePdf:-'+str(e))
					Core_Object.Write_Logs(str(Unique_Id), ' |service-function|genrateFillablePdf|genrateAllFillablePdf|Exceptions| '+str(e),
				      'Genrate_Fillable_Pdf', 'document_process')

					Response['error_code'] = 531
					Response['success'] = False



			return Response



##################################################################################
## function : genrateEsignedPdf							##
## service function used to generate selfie sign application form 		##
##										##
## Parameters : photo (selfie photo)						##
##		signature (signature photo)					##
##		source								##
##		source_type 							##
## 		source_reference_number						##
##		user_reference_number						##
##		pdf_url	    	  						##
##		form_type : (Optional ESIGN | SELFIESIGN)			##
##################################################################################
	def genrateEsignedPdf(self,photo,signature,request_parameters,Unique_Id):


			Response = {}

			try:

				if 'get_pdf_url' in request_parameters and request_parameters['get_pdf_url'] == 'true':


						Request_Object = {}
						Request_Object['source_reference_number'] = request_parameters['source_reference_number']
						Request_Object['document_type'] = '90'
						Response_Object = Document_Model_Object.getDocumentList(Request_Object)

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateSignedPdf|genrateEsignedPdf|get-pdf-url|'+Core_Object.returnJsonForLogs(Response_Object),
					      'Genrate_Signed_Pdf', 'document_process')

						if len(Response_Object) > 0:

							Get_Latest_Entry = Response_Object[0]['document_url']
							Amazon_Url = Amazon_Library.Create_Presigned_Url(Get_Latest_Entry)

							Response['success'] = True
							Response['data'] = {"pdf_url":Amazon_Url}

							return Response

				else:

					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)



					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'
					Filename = 'Fillable_Application_Form_'+str(request_parameters['source_reference_number'])
					Category_Initial = 'Fillable'
					# Get assign financer id to identify which form is to select
					Transaction_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id)


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateSignedPdf|genrateEsignedPdf|transaction-service-response|'+Core_Object.returnJsonForLogs(Transaction_Response),
					      'Genrate_Signed_Pdf', 'document_process')

					Get_Finaner_Name = 'SiCreva'
					if Transaction_Response['data']['transaction']['assigned_financier_id'] in Assigned_Financer_Id.keys():
						Get_Finaner_Name = Assigned_Financer_Id[Transaction_Response['data']['transaction']['assigned_financier_id']]
						Filename = Get_Finaner_Name+'_Fillable_Application_Form_'+str(request_parameters['source_reference_number'])
						Category_Initial = Get_Finaner_Name

					#Filename = 'FedFina_Fillable_Application_Form_'+str(request_parameters['source_reference_number'])
					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'


					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):

							Amazon_Url = Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)


					with urllib.request.urlopen(Amazon_Url) as url:


						Pdf_Bytes = bytearray(url.read())


					Photo_Bytes = photo.read()
					Signature_Bytes = signature.read()

					if Get_Finaner_Name == 'Mass':

						Signed_Pdf = FillablePdf_Library.createSignedPdfMass(Pdf_Bytes,Photo_Bytes,Signature_Bytes)

					else:
						Signed_Pdf = FillablePdf_Library.createSignedPdf(Pdf_Bytes,Photo_Bytes,Signature_Bytes)


					Filename = 'Application_Photo_'+str(request_parameters['source_reference_number'])

					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'jpg'

					Uploaded_Photo = Amazon_Library.Upload_Document_S3(Photo_Bytes,Options,Filename)


					Filename = 'Application_Signature_'+str(request_parameters['source_reference_number'])


					Request_Parameters_Signature = {}
					Request_Parameters_Signature['source'] = request_parameters['source']
					Request_Parameters_Signature['source_type'] = request_parameters['source_type']
					Request_Parameters_Signature['document_category_id'] = '78'
					Request_Parameters_Signature['document_type_id'] = '176'
					Request_Parameters_Signature['face'] = 'FRONT'
					Request_Parameters_Signature['user_reference_number'] = request_parameters['user_reference_number']
					Request_Parameters_Signature['source_reference_number'] = request_parameters['source_reference_number']
					Request_Parameters_Signature['underwriter_status'] = 'APPROVE'

					Options_Upload_Signature = {}
					Options_Upload_Signature['Format'] =  'png'
					Response_User_Signature = self.uploadDocuments(Signature_Bytes,'User_Signature',Request_Parameters_Signature,Options_Upload_Signature)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateSignedPdf|genrateEsignedPdf|Response Data|'+Core_Object.returnJsonForLogs(Response_User_Signature),
					      'Genrate_Signed_Pdf', 'document_process')

					##########################

					Request_Parameters_Pdf = {}
					Request_Parameters_Pdf['source'] = request_parameters['source']
					Request_Parameters_Pdf['source_type'] = request_parameters['source_type']
					Request_Parameters_Pdf['document_category_id'] = Financer_Docket_Mapper[Category_Initial]['Category']
					Request_Parameters_Pdf['document_type_id'] = Financer_Docket_Mapper[Category_Initial]['Type']['Selfie']
					Request_Parameters_Pdf['face'] = 'FRONT'
					Request_Parameters_Pdf['user_reference_number'] = request_parameters['user_reference_number']
					Request_Parameters_Pdf['source_reference_number'] = request_parameters['source_reference_number']
					Request_Parameters_Pdf['underwriter_status'] = 'APPROVE'


					Options_Upload_Pdf = {}
					Options_Upload_Pdf['Format'] =  'pdf'
					Response_User_Pdf = self.uploadDocuments(Signed_Pdf,'Esigned_Pdf',Request_Parameters_Pdf,Options_Upload_Pdf)
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateSignedPdf|genrateEsignedPdf|Response Data|'+Core_Object.returnJsonForLogs(Response_User_Pdf),
					      'Genrate_Signed_Pdf', 'document_process')

					if Document_Model_Object.setDocument(Response_User_Pdf,Unique_Id) == True and Document_Model_Object.setDocument(Response_User_Signature,Unique_Id):

							Request_Object = {}
							Request_Object['source_reference_number'] = request_parameters['source_reference_number']
							Request_Object['document_type'] = Financer_Docket_Mapper[Category_Initial]['Type']['Selfie']
							Response_Object = Document_Model_Object.getDocumentList(Request_Object)


							if len(Response_Object) > 0:

								Get_Latest_Entry = Response_Object[0]['document_url']
								Amazon_Url = Amazon_Library.Create_Presigned_Url(Get_Latest_Entry)

								Response['success'] = True
								Response['data'] = {"pdf_url":Amazon_Url}




					else:


							Response['error_code'] = 504
							Response['success'] = False



					return Response


			except Exception as e:

				print('Exception genrateEsignedPdf:-'+str(e))
				Core_Object.Write_Logs(str(Unique_Id), ' |service-function|genrateSignedPdf|genrateEsignedPdf|Exceptions| '+str(e),
				      'Genrate_Signed_Pdf', 'document_process')

				Response['success'] = False
				Response['error_code'] = 532


				return Response



##################################################################################
## function : genrateNachForm							##
## service function used to generate Nach form pdf				##
##										##
## Parameters : 								##
##		source								##
## 		source_reference_number						##
##		user_reference_number						##
##		create_forcefully	    	  				##
##		nach_reference_number						##
##################################################################################

	def genrateNachForm(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:


					# Nach ref number on s3 bucket
					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)


					Transaction_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|transaction-service-response|'+Core_Object.returnJsonForLogs(Transaction_Response),
					      'Genrate_Nach_Pdf', 'document_process')

					# bank_details_id
					Bank_Details_Request = {}
					Bank_Details_Request['user_bank_account_id'] = Transaction_Response['data']['transaction']['bank_details_id']
					Bank_Details_Request['user_reference_number'] = request_parameters['user_reference_number']


					User_Bank_Details_Response = Thirdparty_Service_Class.executeGetUserBankDetails(Bank_Details_Request,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|bank-details-response|'+Core_Object.returnJsonForLogs(User_Bank_Details_Response),
					      'Genrate_Nach_Pdf', 'document_process')

					Create_Mandate_Request = {}
					Create_Mandate_Request['user_reference_number'] = request_parameters['user_reference_number']
					Create_Mandate_Request['source_reference_number'] = request_parameters['source_reference_number']
					Create_Mandate_Request['source'] = request_parameters['source']
					if 'nach_reference_number' in request_parameters:

						Create_Mandate_Request['mandate_reference_number'] = request_parameters['nach_reference_number']

					else:

						Create_Mandate_Request['mandate_reference_number'] = request_parameters['mandate_reference_number']


					Mandate_Response = Thirdparty_Service_Class.executeGetMandateDetails(Create_Mandate_Request,Unique_Id)


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|mandate-response|'+Core_Object.returnJsonForLogs(Mandate_Response),
					      'Genrate_Nach_Pdf', 'document_process')

					if not User_Bank_Details_Response['data']['bank_account']:

						Response['error_code'] = 546
						Response['success'] = False
						return Response

					Bank_Data = User_Bank_Details_Response['data']['bank_account'][0]

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'
					Filename = 'Nach_Form_'+str(Bank_Data['bank_branch_ifsc'])+'_'+Mandate_Response[0]['mandate_reference_number']


					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|amazon-nach-present|',
					      'Genrate_Nach_Pdf', 'document_process')

						Response['success'] = True
						Response['data'] = {"nach_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:


							return Response





					Users_Response = Thirdparty_Service_Class.executeGetUsersApi(request_parameters,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|user-response|'+Core_Object.returnJsonForLogs(Users_Response),
					      'Genrate_Nach_Pdf', 'document_process')


					Create_Data_Dicts = {}

					if Mandate_Response[0]['umrn_number']:

						Create_Data_Dicts['umrn'] = " ".join(str(Mandate_Response[0]['umrn_number']))


					Dob_Date = Mandate_Response[0]['nach_process_date'].split('-')
					Create_Dob_Date = str(Dob_Date[2]) +'-'+str(Dob_Date[1])+'-'+str(Dob_Date[0])
					Create_Data_Dicts['date_dd'] = " ".join(str(Dob_Date[2]) if len(str(Dob_Date[2])) > 1 else '0'+str(Dob_Date[2]) )
					Create_Data_Dicts['date_mm'] = " ".join(str(Dob_Date[1]) if len(str(Dob_Date[1])) > 1 else '0'+str(Dob_Date[1]) )
					Create_Data_Dicts['date_yyyy'] = " ".join(str(Dob_Date[0]))


					Create_Data_Dicts['sponsor_bank_code'] = Sponsor_Bank_Code # Hardcoded
					Create_Data_Dicts['utility_cod'] = Utility_Code # Hardcode
					Create_Data_Dicts['company_name'] = Company_Name #Hardcode
					Create_Data_Dicts['bank_account_number'] = " ".join(str(User_Bank_Details_Response['data']['bank_account'][0]['bank_account_no']))
					Create_Data_Dicts['bank_name'] = User_Bank_Details_Response['data']['bank_account'][0]['bank_name']
					Create_Data_Dicts['ifsc_code'] = " ".join(str(User_Bank_Details_Response['data']['bank_account'][0]['bank_branch_ifsc'] ))
					Create_Data_Dicts['micr'] = '' #to be given
					Create_Data_Dicts['amount_words'] = self.convertToWords(Mandate_Response[0]['nach_amount'])
					Create_Data_Dicts['amount'] = str(Mandate_Response[0]['nach_amount'])
					Create_Data_Dicts['mandate_reference_number1'] = Mandate_Response[0]['mandate_reference_number']

					#Create_Data_Dicts['user_name1_5'] = str(User_Bank_Details_Response['data']['bank_account'][0]['bank_account_holder_name'])
					Create_Data_Dicts['user_name1_1'] = str(User_Bank_Details_Response['data']['bank_account'][0]['bank_account_holder_name'])

					Create_Data_Dicts['period_from_dd'] = " ".join(str(Dob_Date[2]) if len(str(Dob_Date[2])) > 1 else '0'+str(Dob_Date[2]) )
					Create_Data_Dicts['period_from_mm'] = " ".join(str(Dob_Date[1]) if len(str(Dob_Date[1])) > 1 else '0'+str(Dob_Date[1]) )
					Create_Data_Dicts['period_from_yyyy'] = " ".join(str(Dob_Date[0]))


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateNachForm|genrateNachForm|final-object-response|'+Core_Object.returnJsonForLogs(Create_Data_Dicts),
					      'Genrate_Nach_Pdf', 'document_process')


					Create_Checkbox_Dict = {}
					Bank_Account_Type = User_Bank_Details_Response['data']['bank_account'][0]['bank_account_type']
					if Bank_Account_Type:

							if Bank_Account_Type == 'SAVINGS':

								Create_Checkbox_Dict['debittick-sb4'] = 'YES'

							elif Bank_Account_Type == 'CURRENT':

								 Create_Checkbox_Dict['debittick-ca'] = 'YES'

							else:

								Create_Checkbox_Dict['debittick-other'] = 'YES'






					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'

					Bytes = FillablePdf_Library.fillableNachForm(Create_Data_Dicts,Create_Checkbox_Dict)

					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Bytes,Options,Filename)
					# Parse Data from NASH PDF File
					Create_Json_File = FillablePdf_Library.pdfParser(Bytes, Uploaded_Filename, Pdf_Path)

					Response['success'] = True
					Response['data'] = {"nach_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

					return Response

					#return Response

			except Exception as e:

					print('Exception genrateNachForm:-'+str(e))
					Core_Object.Write_Logs(str(Unique_Id), ' |service-function|genrateNachForm|genrateNachForm|Exceptions| '+str(e),
				      'Genrate_Nach_Pdf', 'document_process')

					Response['error_code'] = 536
					Response['success'] = False



			return Response

##################################################################################
## function : genrateEsignXmlService						##
## service function used to generate NSDL Xml from application form		##
##	 using nsd java sdk			 				##
##										##
## Parameters : 								##
## 		source_reference_number						##
##		user_reference_number						##
##		pdf_url								##
##################################################################################
	def genrateEsignXmlService(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:

					# Get application pdf
					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'


					Get_Uploaded_Application_Form = request_parameters['pdf_url'].split('/')[7].split('.')[0]

					Filename = Get_Uploaded_Application_Form
					Get_Finaner_From_File = Filename.split('_')

					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignXml|genrateEsignXmlService|get-application-pdf|'+Return_Signed_Create_Url,
				      'Genrate_ESigned_Xml', 'document_process')


					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):

						Amazon_Url = Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)

					else:

						Response['error_code'] = 543
						Response['success'] = False
						return Response

					Document_Name = Return_Signed_Create_Url.split('/').pop()
					with urllib.request.urlopen(Amazon_Url) as url:


						Pdf_Bytes = bytearray(url.read())

					Get_User_Information = Thirdparty_Service_Class.executeGetUsersApi(request_parameters,Unique_Id)
					Get_User_Address = Thirdparty_Service_Class.executeGetUsersPresentAddress(request_parameters,Unique_Id)
					User_Information = {}

					User_Information['allow_finaner_id'] = 'SiCreva'
					if Get_Finaner_From_File[0] == 'Mass':

						User_Information['allow_finaner_id'] = 'Mass'

					User_Information['name'] = Get_User_Information['data']['user']['first_name']+' '+Get_User_Information['data']['user']['last_name']
					if 'data' in Get_User_Address and 'address' in Get_User_Address['data'] and 'city' in Get_User_Address['data']['address']:

						User_Information['city'] = str(Get_User_Address['data']['address']['city'])
					else:

						User_Information['city'] = 'Mumbai'


					User_Information['document_name'] = Document_Name
					User_Information['transaction_number'] = request_parameters['source_reference_number']


					Presigned_Xml_Response = FillablePdf_Library.createPresignedXml(Pdf_Bytes,User_Information)


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignXml|genrateEsignXmlService|Response Data| '+Core_Object.returnJsonForLogs(Presigned_Xml_Response),
				      'Genrate_ESigned_Xml', 'document_process')


					if Presigned_Xml_Response['success'] == True:

						Response['success'] = True
						Response['data'] = {'response_xml':Presigned_Xml_Response['xml_data']}

					else:

						Response['success'] = False
						Response['error_code'] = 541

					return Response
					#return Response

			except Exception as e:

					print('Exception genrateEsignXmlService:-'+str(e))
					Response['error_code'] = 542
					Response['success'] = False



			return Response

##################################################################################
## function : genrateEsignPdfFromXmlService					##
## service function used to generate nsdl signed pdf from response xml from 	##
##	nsdl									##
##										##
## Parameters : 								##
## 		source_reference_number						##
##		user_reference_number						##
##		pdf_url								##
##		source								##
##		source_type							##
##		response_xml (nsdl response xml)				##
##################################################################################

	def genrateEsignPdfFromXmlService(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:

					# Nach ref number on s3 bucket
					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Make_Esign_Table_Entry = {}

					Make_Esign_Table_Entry['source_reference_number'] = request_parameters['source_reference_number']
					Make_Esign_Table_Entry['user_reference_number'] = request_parameters['user_reference_number']
					Make_Esign_Table_Entry['esign_attempt_reference_number'] = Core_Object.generateUiid()
					Make_Esign_Table_Entry['source'] = request_parameters['source_type']


					Data = re.findall(r"errCode=\"(.*?)\"|txn=\"(.*?)\"|errMsg=\"(.*?)\"|resCode=\"(.*?)\"",request_parameters['response_xml'], re.MULTILINE)
					#print(Data)
					Error_Code = 622
					if Data[0][0] == 'NA':

						Make_Esign_Table_Entry['response_status'] = 'Success'

					else:

						Make_Esign_Table_Entry['response_status'] = 'Failure'
						Make_Esign_Table_Entry['error_message'] = Data[1][2]
						Make_Esign_Table_Entry['error_code'] = Data[0][0]

						if Make_Esign_Table_Entry['error_code'] in Esign_No_Retry:
							Error_Code = 620
						elif Make_Esign_Table_Entry['error_code'] in Esign_Only_Count:
							Error_Code = 621
						elif Make_Esign_Table_Entry['error_code'] in Esign_Retry_Allow:
							Error_Code = 622




					if len(Data) > 3:

						Make_Esign_Table_Entry['response_txnid'] = Data[3][1]
						Make_Esign_Table_Entry['response_code'] = Data[2][3]

					else:

						Make_Esign_Table_Entry['response_txnid'] = Data[2][1]

					Document_Model_Object.manipulationEsignTable(Make_Esign_Table_Entry,Unique_Id)
					Esign_Attempts = Document_Model_Object.getEsignLogs(request_parameters['source_reference_number'])


					if Esign_Attempts:

						Hardfail = 0
						Softfail = 0
						Serverdown = 0


						for counts in Esign_Attempts:

							if counts['error_code'] in Esign_No_Retry:
								Hardfail = Hardfail + counts['total_count']

							elif counts['error_code'] in Esign_Only_Count:
								Softfail = Softfail + counts['total_count']

							elif counts['error_code'] in Esign_Retry_Allow:
								Serverdown = Serverdown + counts['total_count']

						Total_Count_Failure = int(Hardfail) + int(Softfail) + int(Serverdown)

					if not Data[0][0] == 'NA':

						Response['success'] = False
						Response['error_code'] = Error_Code
						Response['data'] = {'hard_fail_count':Hardfail,'soft_fail_count':Softfail,'total_fail_count':Total_Count_Failure}
						return Response



					Get_Uploaded_Application_Form = request_parameters['pdf_url'].split('/')[7].split('.')[0]

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'
					Filename = Get_Uploaded_Application_Form+'_signedFinal'
					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'
					#print(Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url))
					#sys.exit()
					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|amazon-nach-present|',
					      'Genrate_ESigned_Pdf_From_Xml', 'document_process')

						Response['success'] = True
						Response['data'] = {"esign_pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						return Response


					Get_User_Information = Thirdparty_Service_Class.executeGetUsersApi(request_parameters,Unique_Id)
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|User Information Data|'+Core_Object.returnJsonForLogs(Get_User_Information),
					      'Genrate_ESigned_Pdf_From_Xml', 'document_process')

					Get_User_Address = Thirdparty_Service_Class.executeGetUsersPresentAddress(request_parameters,Unique_Id)
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|User Address Data|'+Core_Object.returnJsonForLogs(Get_User_Address),
					      'Genrate_ESigned_Pdf_From_Xml', 'document_process')

					User_Information = {}


					######## Below Code To Generate certificate file to get user details from response xml UserX509Certificate Tag
					Get_User_Certificate = re.findall(r"<UserX509Certificate>(.*?)</UserX509Certificate>",request_parameters['response_xml'],re.MULTILINE)


					# Create certificate file inside temp folder
					Pdf_Path = os.getcwd()+'/application/library/Fillable_Pdf/Tempfiles/'+request_parameters['source_reference_number']+'_User_Certificate.cert'
					Response_User_Certificate = open(Pdf_Path, "w")
					Response_User_Certificate.write("-----BEGIN CERTIFICATE-----\n"+Get_User_Certificate[0]+"\n-----END CERTIFICATE-----")
					Response_User_Certificate.close()

					# Execute openssl command shell to get details from certificate file
					Signed_User_Details = os.popen('openssl x509 -in '+Pdf_Path+' -text -noout')

					# Extract user details by regular expression
					Get_Signed_User_Details = re.findall(r"Subject: (.*?)dnQualifier",Signed_User_Details.read(),re.MULTILINE)

					# Put all data inside below variable
					Create_Signed_User_Details_Object = {}
					for Details in Get_Signed_User_Details[0].split(','):

						Split_Details = Details.split("=")
						# CN stands for Customer Name
						if Split_Details[0].strip() == 'CN':

							Create_Signed_User_Details_Object['certified_signature_name'] = Split_Details[1].strip()

						# ST stands for Customer State
						elif Split_Details[0].strip() == 'ST':

							Create_Signed_User_Details_Object['certified_signature_state'] = Split_Details[1].strip()

						# C stands for Customer Country
						elif Split_Details[0].strip() == 'C':

							Create_Signed_User_Details_Object['certified_signature_country'] = Split_Details[1].strip()

						# postalCode stands for Customer Pincode
						elif Split_Details[0].strip() == 'postalCode':

							Create_Signed_User_Details_Object['certified_signature_pincode'] = Split_Details[1].strip()


					User_Information['name'] = Get_User_Information['data']['user']['first_name']+' '+Get_User_Information['data']['user']['last_name']

					if 'data' in Get_User_Address and 'address' in Get_User_Address['data'] and 'city' in Get_User_Address['data']['address']:

						User_Information['city'] = str(Get_User_Address['data']['address']['city'])
					else:

						User_Information['city'] = 'Mumbai'

					#User_Information['city'] = Create_Signed_User_Details_Object['certified_signature_state']
					User_Information['transaction_number'] = request_parameters['source_reference_number']
					User_Information['source_reference_number'] = request_parameters['source_reference_number']
					User_Information['pdf_url'] = Get_Uploaded_Application_Form

					User_Information['allow_finaner_id'] = 'SiCreva'
					Get_Assign_Financer = Get_Uploaded_Application_Form.split('_')
					if Get_Assign_Financer[0] == 'Mass':

						User_Information['allow_finaner_id'] = 'Mass'

					Presigned_Pdf_Bytes = FillablePdf_Library.createSignedPdfFromXml(request_parameters['response_xml'],User_Information)

					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'

					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Presigned_Pdf_Bytes,Options,Filename)

					Get_Financer = Get_Uploaded_Application_Form.split('_')
					Request_Parameters_Pdf = {}
					Request_Parameters_Pdf['source'] = request_parameters['source']
					Request_Parameters_Pdf['source_type'] = request_parameters['source_type']
					Request_Parameters_Pdf['document_category_id'] = Financer_Docket_Mapper[Get_Financer[0]]['Category']
					Request_Parameters_Pdf['document_type_id'] = Financer_Docket_Mapper[Get_Financer[0]]['Type']['Esign']
					Request_Parameters_Pdf['face'] = 'FRONT'
					Request_Parameters_Pdf['user_reference_number'] = request_parameters['user_reference_number']
					Request_Parameters_Pdf['source_reference_number'] = request_parameters['source_reference_number']
					#Request_Parameters_Pdf['underwriter_status'] = 'APPROVE'
					Request_Parameters_Pdf['extracted_data'] = json.dumps(Create_Signed_User_Details_Object)


					Options_Upload_Pdf = {}
					Options_Upload_Pdf['Format'] =  'pdf'
					Response_User_Pdf = self.uploadDocuments(Presigned_Pdf_Bytes,'Esigned_Pdf',Request_Parameters_Pdf,Options_Upload_Pdf)


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|Response Data|'+Core_Object.returnJsonForLogs(Response_User_Pdf),
					      'Genrate_ESigned_Pdf_From_Xml', 'document_process')


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|Response Data| Presigned Pdf Bytes Captured',
				      'Genrate_ESigned_Pdf_From_Xml', 'document_process')


					if Document_Model_Object.setDocument(Response_User_Pdf,Unique_Id) == True:

						Thirdparty_Service_Class.executeTxnServiceVerifyDoc(request_parameters,Unique_Id,'Genrate_ESigned_Pdf_From_Xml')
						Response['success'] = True
						Response['data'] = {"esign_pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url),"doc_ref_number":Response_User_Pdf['document_reference_number']}

					else:

						Response['success'] = False
						Response['error_code'] = 544

					return Response
					#return Response

			except Exception as e:

					print('Exception genrateEsignPdfFromXmlService:-'+str(e))
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateEsignPdfFromXml|genrateEsignPdfFromXmlService|Response Data| Exception Captured:- '+str(e),
				      'Genrate_ESigned_Pdf_From_Xml', 'document_process')
					Response['data'] = {}
					Response['error_code'] = 545
					Response['success'] = False



			return Response

##################################################################################
## function : generateFillablePdfMass						##
## service function used to generate fillable pdf mass application form only 	##
##	(its nested function calling from fillableapplicationform)		##
##										##
## Parameters : 								##
## 		source_reference_number						##
##		user_reference_number						##
##		pdf_url								##
##		source								##
##		create_forcefully						##
##################################################################################

	def generateFillablePdfMass(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:


					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|',
				      'Genrate_Fillable_Pdf', 'document_process')

					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Transaction_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id,'/extended-details')
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|transaction-service-response|'+Core_Object.returnJsonForLogs(Transaction_Response),
					      'Genrate_Fillable_Pdf', 'document_process')

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'

					Bank_Details_Request = {}
					#Bank_Details_Request['user_bank_account_id'] = Transaction_Response['data']['transaction']['bank_details_id']
					Bank_Details_Request['user_reference_number'] = request_parameters['user_reference_number']


					#User_Bank_Details_Response = Thirdparty_Service_Class.executeGetUserBankDetails(Bank_Details_Request,Unique_Id)
					#Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|bank-response|'+Core_Object.returnJsonForLogs(User_Bank_Details_Response),
					     # 'Genrate_Fillable_Pdf', 'document_process')


					Filename = 'Mass_Fillable_Application_Form_'+str(request_parameters['source_reference_number'])


					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'
					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):


						Response['success'] = True
						Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|pdf-exists|'+Core_Object.returnJsonForLogs(Response),
					      'Genrate_Fillable_Pdf', 'document_process')

						#return Response

					# Get Transaction SKU Details
					Transaction_Sku_Response = Thirdparty_Service_Class.executeGetTransactionApi(request_parameters,Unique_Id,'/get-sku')

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|transaction-sku-service-response|'+Core_Object.returnJsonForLogs(Transaction_Sku_Response),
					      'Genrate_Fillable_Pdf', 'document_process')




					Users_Request_Params = {}
					Users_Request_Params['user_reference_number'] = Transaction_Response['data']['transaction']['user_reference_number']

					# Get User Details
					Users_Response = Thirdparty_Service_Class.executeGetUsersApi(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|user-service-response|'+Core_Object.returnJsonForLogs(Users_Response),
					      'Genrate_Fillable_Pdf', 'document_process')


					# Get User Present Address
					User_Present_Address = Thirdparty_Service_Class.executeGetUsersPresentAddress(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|user-present-address-response|'+Core_Object.returnJsonForLogs(User_Present_Address),
					      'Genrate_Fillable_Pdf', 'document_process')

					# Get User Employment Details
					Emplyment_Details = Thirdparty_Service_Class.executeGetEmplymentDetails(Users_Request_Params,Unique_Id)

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|employment-response|'+Core_Object.returnJsonForLogs(Emplyment_Details),
					      'Genrate_Fillable_Pdf', 'document_process')




					Merchant_Details = Thirdparty_Service_Class.executeGetMerchantDetails(Transaction_Response['data']['transaction'],Unique_Id)
					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|merchant-response|'+Core_Object.returnJsonForLogs(Merchant_Details),
					      'Genrate_Fillable_Pdf', 'document_process')


					Create_Data_Dicts = {}

					# All Data ponits collected inside single variable
					Transaction_Data = Transaction_Response['data']['transaction']
					Users_Data = Users_Response['data']['user']
					Users_Address_Data = User_Present_Address['data']['address']
					#Emplyment_Details_Data = Emplyment_Details['data']['employment_detail']
					Transaction_Sku_Data = 	Transaction_Sku_Response['data']['sku']
					Merchant_Data = Merchant_Details['data']['merchant']


					Kissht_Date = datetime.strptime(Transaction_Data['created_at'], '%Y-%m-%d %H:%M:%S')
					Create_Kissht_Date = str(Kissht_Date.day) +' / '+str(Kissht_Date.month)+' / '+str(Kissht_Date.year)
					Create_Data_Dicts['user_name'] = Users_Data['first_name']+' '+Users_Data['last_name']
					Create_Data_Dicts['user_date'] = Create_Kissht_Date
					Create_Data_Dicts['loan_application_name1'] = str(Users_Data['first_name'])
					Create_Data_Dicts['loan_application_name3'] = str(Users_Data['last_name'])
					Create_Data_Dicts['loan_application_name2'] = str(Users_Data['middle_name']) if Users_Data['middle_name'] else ''

					Dob_Date = datetime.strptime(Users_Data['dob'], '%Y-%m-%d')
					Create_Dob_Date = str(Dob_Date.day) +'-'+str(Dob_Date.month)+'-'+str(Dob_Date.year)

					Create_Data_Dicts['date_of_birth'] = Create_Dob_Date

					Create_Data_Dicts['pan_card_no'] = Users_Data['pan']
					Create_Data_Dicts['aadhaar_no'] = Users_Data['aadhaar']

					# Removed on request
					Create_Data_Dicts['phone_number'] = Users_Data['mobile_number']
					Create_Data_Dicts['email_id'] = Users_Data['email']

					Create_Data_Dicts['pincode'] = Users_Address_Data['pincode']
					Create_Data_Dicts['city'] = Users_Address_Data['city']
					Create_Data_Dicts['state'] = Users_Address_Data['state']

					Create_Data_Dicts['place'] = Users_Address_Data['city']
					Create_Data_Dicts['address'] = (str(Users_Address_Data['room_number'])+', ' if Users_Address_Data['room_number'] is not None else '')+str(Users_Address_Data['line_1'])

					if Users_Address_Data['line_2'] is not  None:
						Create_Data_Dicts['address2'] = (str(Users_Address_Data['line_2'])+', ' if Users_Address_Data['line_2'] is not None else '') + str(Users_Address_Data['landmark'])


					Create_Data_Dicts['merchant_name'] = Merchant_Data['company_name']
					#Create_Data_Dicts['merchant_code'] = Merchant_Data['merchant_id']
					Create_Data_Dicts['rufilo_id'] = Transaction_Data['fb_transaction_id']

					"""Create_Data_Dicts['loan_bank_account_holder_name'] = str(Bank_Data['bank_account_holder_name'])
					Create_Data_Dicts['bank_name'] = str(Bank_Data['bank_name'])
					Create_Data_Dicts['loan_bank_branch_name'] = str(Bank_Data['bank_branch']) if Bank_Data['bank_branch'] else ''
					Create_Data_Dicts['ifsc_code'] = str(Bank_Data['bank_branch_ifsc'])
					Create_Data_Dicts['loan_bank_account_type'] = str(Bank_Data['bank_account_type'])
					Create_Data_Dicts['bank_account_number'] = str(Bank_Data['bank_account_no'])
					"""

					Create_Data_Dicts['kissht_date'] = Create_Kissht_Date
					Create_Data_Dicts['loan_product_value'] = str(Transaction_Data['product_value'])
					Create_Data_Dicts['loan_downpayment_amount'] = str(Transaction_Data['down_payment_amount'])
					Create_Data_Dicts['loan_sum_amount'] = str(Transaction_Data['loan_amount'])

					Create_Data_Dicts['loan_rupees1'] = self.convertToWords(Transaction_Data['loan_amount'])
					Create_Data_Dicts['loan_name'] = str(Create_Data_Dicts['user_name'])

					Create_Data_Dicts['loan_address'] = (str(Users_Address_Data['room_number'])+', ' if Users_Address_Data['room_number'] is not None else '')+str(Users_Address_Data['line_1']) + (str(Users_Address_Data['line_2'])+', ' if Users_Address_Data['line_2'] is not None else '') + str(Users_Address_Data['landmark'])

					Create_Data_Dicts['load_date1'] = str(Create_Kissht_Date)
					Create_Data_Dicts['loan_name2'] = str(Create_Data_Dicts['user_name'])
					Create_Data_Dicts['loan_date2'] = str(Create_Kissht_Date)
					Create_Data_Dicts['loan_amt_rs'] = str(Transaction_Data['loan_amount'])

					Create_Data_Dicts['loan_percentage'] = str(Transaction_Data['interest_component'])
					Create_Data_Dicts['loan_emi_amt'] = str(Transaction_Data['instalment_amount'] )
					Create_Data_Dicts['loan_tenure'] = str(Transaction_Data['instalment_no_months'])

					#Create_Data_Dicts['loan_first_emi_date'] = str(Create_Kissht_Date)
					#Create_Data_Dicts['loan_last_emi_date'] = str(Create_Kissht_Date)

					# Below is Franch Name
					if Transaction_Data['franchise_id'] and Transaction_Data['franchise_id'] > 0:

						Create_Data_Dicts['loan_name4'] = str(Transaction_Data['franchisee_name'])

					else:

						Create_Data_Dicts['loan_name4'] = str(Create_Data_Dicts['user_name'])

					Create_Data_Dicts['loan_rsamt'] =  str(Transaction_Data['loan_amount'])
					#Create_Data_Dicts['loan_demand'] = str(Create_Data_Dicts['user_name'])
					Create_Data_Dicts['loan_sumof_rupees1'] = self.convertToWords(Transaction_Data['loan_amount'])

					Counter_Sku_Count = 1
					Create_Checkbox_Dicts = {}

					Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|genrateAllFillablePdf|final-object-response|'+Core_Object.returnJsonForLogs(Create_Data_Dicts),
					      'Genrate_Fillable_Pdf', 'document_process')

					if Users_Data['employment_type']:

						if Users_Data['employment_type'] == 'salaried':

							Create_Checkbox_Dicts['loan_employment_occupation_salaried'] = 'Yes'

						else:

							Create_Checkbox_Dicts['loan_employment_occupation_self_employed'] = 'Yes'


					if Users_Data['gender'] == 'MALE':

						Create_Checkbox_Dicts['gendar_male'] = 'Yes'

					if Users_Data['gender'] == 'FEMALE':

						Create_Checkbox_Dicts['gendar_female'] = 'Yes'

					if Users_Data['residence_type']:

						if Users_Data['residence_type'] == 'OWNED':

							Create_Checkbox_Dicts['loan_residence_type_owned'] = 'Yes'

						else:

							Create_Checkbox_Dicts['loan_residence_type_rented'] = 'Yes'



					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'

					Request_Object_Photo = {}
					Request_Object_Photo['source_reference_number'] = request_parameters['source_reference_number']
					Request_Object_Photo['document_type'] = '92'
					Request_Object_Photo['document_category'] = '10'

					Get_Customer_Photo = Document_Model_Object.getDocumentList(Request_Object_Photo) # Model Call

					if Get_Customer_Photo:

						Response['error_code'] = 551
						Response['success'] = False


					Create_Bytes_Object = {}
					Amazon_Url = Amazon_Library.Create_Presigned_Url(Get_Customer_Photo[0]['document_url'])


					with urllib.request.urlopen(Amazon_Url) as url:


						Photo_Bytes = url.read()

					Create_Bytes_Object['photo_bytes'] = Photo_Bytes

					if 'form_type' in request_parameters and (request_parameters['form_type'] == 'ESIGN' or request_parameters['form_type'] == 'SELFIE_SIGN'):

						Request_Object_Aadhar = {}
						Request_Object_Aadhar['source_reference_number'] = request_parameters['source_reference_number']
						Request_Object_Aadhar['document_type'] = '38'
						Request_Object_Aadhar['document_category'] = '9'
						Request_Object_Aadhar['document_face'] = 'FRONT'
						Request_Object_Aadhar['underwriter_status'] = 'APPROVE'

						Get_Customer_Pan = Document_Model_Object.getDocumentList(Request_Object_Aadhar) # Model Call


						if Get_Customer_Pan:

							Get_Extension = Get_Customer_Pan[0]['document_url'].split('.')
							Amazon_Url = Amazon_Library.Create_Presigned_Url(Get_Customer_Pan[0]['document_url'])

							with urllib.request.urlopen(Amazon_Url) as url:


								Document_Bytes = url.read()

							Create_Bytes_Object['pan_data'] = {"pan_type":Get_Extension[1],"pan_bytes":Document_Bytes}


						Request_Object_Aadhar = {}
						Request_Object_Aadhar['source_reference_number'] = request_parameters['source_reference_number']
						Request_Object_Aadhar['document_type'] = '3'
						Request_Object_Aadhar['document_category'] = '2'
						Request_Object_Aadhar['document_face'] = 'BACK'
						Request_Object_Aadhar['underwriter_status'] = 'APPROVE'

						Get_Customer_Aadhar = Document_Model_Object.getDocumentList(Request_Object_Aadhar) # Model Call

						if Get_Customer_Aadhar:

							Get_Extension = Get_Customer_Aadhar[0]['document_url'].split('.')
							Amazon_Url = Amazon_Library.Create_Presigned_Url(Get_Customer_Aadhar[0]['document_url'])

							with urllib.request.urlopen(Amazon_Url) as url:


								Document_Bytes = url.read()

							Create_Bytes_Object['aadhaar_data'] = {"aadhar_type":Get_Extension[1],"aadhar_bytes":Document_Bytes}




					#Filename = 'Fillable_Application_Form_'+str(request_parameters['source_reference_number'])

					if request_parameters['form_type'] in ['ESIGN']:

						"""User_Bank_Details_Response = Thirdparty_Service_Class.executeGetUserBankDetails(Bank_Details_Request,Unique_Id)
						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['source_reference_number']), '|service-function|genrateFillablePdf|generateFillablePdfMass|bank-response|'+Core_Object.returnJsonForLogs(User_Bank_Details_Response),
						      'Genrate_Fillable_Pdf', 'document_process')

						if not User_Bank_Details_Response['data']['bank_account']:

							Response['error_code'] = 546
							Response['success'] = False
							return Response

						Bank_Data = User_Bank_Details_Response['data']['bank_account'][0]
						"""
						Create_Data_Dicts = {}
						Create_Data_Dicts['laf_name_borrower_first1'] = str(Users_Data['first_name'])
						Create_Data_Dicts['laf_name_borrower_middle1'] = str(str(Users_Data['middle_name'])) if str(Users_Data['middle_name']) else ''
						Create_Data_Dicts['laf_name_borrower_last1'] = str(Users_Data['last_name'])
						Create_Data_Dicts['laf_date_of_birth'] = str(Users_Data['dob'])
						Create_Data_Dicts['laf_gender'] = str(Users_Data['gender'])
						#Create_Data_Dicts['laf_martial_status'] = str(Users_Data['last_name'])
						Create_Data_Dicts['laf_occupation'] = str(Users_Data['employment_type'])
						Create_Data_Dicts['laf_nationality'] = str('INDIAN')
						Create_Data_Dicts['laf_proof_of_identity'] = str('PAN CARD')
						Create_Data_Dicts['laf_proof_no'] = str(Users_Data['pan'])
						Create_Data_Dicts['laf_proof_of_address'] = str('AADHAAR CARD')
						Create_Data_Dicts['laf_proof_no1'] = ''
						Create_Data_Dicts['laf_current_address_line1'] = (str(Users_Address_Data['room_number'])+', ' if Users_Address_Data['room_number'] is not None else '')
						Create_Data_Dicts['laf_current_address_line2'] = str(Users_Address_Data['line_1'])
						Create_Data_Dicts['laf_current_address_line3'] = (str(Users_Address_Data['line_2'])+', ' if Users_Address_Data['line_2'] is not None else '') + str(Users_Address_Data['landmark'])

						Create_Data_Dicts['laf_current_address_city1'] = str(Users_Address_Data['city'])
						Create_Data_Dicts['laf_current_address_state1'] = str(Users_Address_Data['state'])
						Create_Data_Dicts['laf_current_address_district1'] = ''
						Create_Data_Dicts['laf_current_address_pin1'] = str(Users_Address_Data['pincode'])

						Create_Data_Dicts['laf_permanent_add_same_current'] = 'YES'

						Create_Data_Dicts['laf_phone_number'] = str(Users_Data['mobile_number'])

						Create_Data_Dicts['laf_date_of_execution'] = str(Create_Kissht_Date)
						Create_Data_Dicts['laf_place_of_execution'] = str(Users_Address_Data['city'])
						Create_Data_Dicts['laf_name_of_borrower'] = str(Users_Data['first_name'])+' '+str(Users_Data['last_name'])

						Create_Data_Dicts['laf_sanctioned_amount'] = str(Transaction_Data['loan_amount'])
						Create_Data_Dicts['laf_processing_fees_by_lender_a'] = str(Transaction_Data['processing_fee'])
						Create_Data_Dicts['laf_emi_amount'] = str(Transaction_Data['instalment_amount'])
						Create_Data_Dicts['laf_installment_frequency'] = str(Transaction_Data['instalment_no_months'])
						Create_Data_Dicts['laf_net_amount_be_disbursed_to_borrower'] = str(Transaction_Data['loan_amount'])
						Create_Data_Dicts['laf_rate_of_interest'] = str(Transaction_Data['interest'])

						Create_Data_Dicts['laf_email'] = str(Users_Data['email'])
						#Create_Data_Dicts['laf_bank_name'] = str(Users_Data['email'])
						#Create_Data_Dicts['laf_bank_branch_details'] = str(Bank_Data['bank_branch']) if Bank_Data['bank_branch'] else ''
						#Create_Data_Dicts['laf_bank_ac_no'] = str(Bank_Data['bank_account_holder_name'])
						#Create_Data_Dicts['laf_ifsc_code'] = str(Bank_Data['bank_branch_ifsc'])
						Create_Data_Dicts['laf_loan_type'] = 'Consumer Loan'
						Create_Data_Dicts['laf_residential_status'] = 'Owned'
						Create_Data_Dicts['laf_marital_status'] = 'Married'
						Create_Data_Dicts['laf_pan_status'] = 'OK'
						Create_Data_Dicts['laf_passport_licence_voter_status'] = 'OK'
						Create_Data_Dicts['laf_last_bank_statement_status'] = 'NA'
						Create_Data_Dicts['laf_any_other_document_lender'] = 'NA'
						Create_Data_Dicts['laf_service_partner_ba'] = 'SiCreva Capitals'

						Bytes = FillablePdf_Library.fillableApplicationMassEsign(Create_Data_Dicts,Create_Checkbox_Dicts,Create_Bytes_Object)

					else:

						Bytes = FillablePdf_Library.fillableApplicationMass(Create_Data_Dicts,Create_Checkbox_Dicts,Create_Bytes_Object)

					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Bytes,Options,Filename)

					Response['success'] = True
					Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

					return Response

			except Exception as e:

					print('Exception generateFillablePdfMass:-'+str(e))
					Core_Object.Write_Logs(str(Unique_Id), ' |service-function|genrateFillablePdf|genrateAllFillablePdf|Exceptions| '+str(e),
				      'Genrate_Fillable_Pdf', 'document_process')

					Response['error_code'] = 531
					Response['success'] = False



			return Response

	def getCategoryDetails(self,request_parameters,Unique_Id):


			if request_parameters:

				Category_ids = request_parameters['category_ids']
				Category_ids = ','.join('"'+str(i)+'"' for i in Category_ids)

				Create_Response_Object = {}
				Model_Response = Document_Model_Object.getCategories(Category_ids)
				if len(Model_Response) > 0:

					Create_Response_Object['success'] = True
					Create_Response_Object['category_details'] = Model_Response


				else:


					Create_Response_Object['success'] = False
					Create_Response_Object['error_code'] = 528



			else:

				Create_Response_Object['success'] = False
				Create_Response_Object['error_code'] = 529



			return Create_Response_Object



	def generateWelcomeLetterPdf(self,request_parameters,Unique_Id):

		_response={}
		try:

			if request_parameters:

					filename = 'Welcome_Letter_'+str(request_parameters['transaction_id'])

					Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['transaction_id']),
										   '|service-function|generateWelcomeLetter|generateWelcomeLetterPdf|request' + Core_Object.returnJsonForLogs(
											   request_parameters),
										   'Genrate_Letters_Pdf', 'document_process')
					raw_directory_user = str(request_parameters['user_reference_number'])+str(Application_Salt)
					has_string = Core_Object.returnHashString(raw_directory_user)

					pdf_path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+has_string+'/AutoGenratedFiles'
					return_signed_create_url = pdf_path+'/'+filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(return_signed_create_url):

						_response['success'] = True
						_response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(return_signed_create_url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['transaction_id']), '|service-function|generateFillableLegalNotice|generateFillableNoticePdf|pdf-exists|'+Core_Object.returnJsonForLogs(_response),
					      'Genrate_Letters_Pdf', 'document_process')

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:
							return _response

					options = {}
					options['Bucket_Key'] = pdf_path
					options['Format'] = 'pdf'

					bytes = FillablePdf_Library.fillableLetters(request_parameters,'_welcome')
					if bytes:
						uploaded_filename = Amazon_Library.Upload_Document_S3(bytes,options,filename)

						_response['success'] = True
						_response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(return_signed_create_url)}
					else:

						_response['success'] = False
						_response['error_code'] = 552
			else:

				_response['success'] = False
				_response['error_code'] = 552

		except Exception as e:

			print(e)
			Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['transaction_id']),
								   '|service-function|generateWelcomeLetter|generateWelcomeLetterPdf|exception|' + str(e),
								   'Genrate_Letters_Pdf', 'document_process')
			_response['success'] = False
			_response['error_code'] = 553


		return _response

	def generateSanctionLetterPdf(self,request_parameters,Unique_Id):

		_response={}
		try:

			if request_parameters:

					filename = 'Sanction_Letter_'+str(request_parameters['transaction_id'])
					Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['transaction_id']),
										   '|service-function|generateSanctionLetter|generateSanctionLetterPdf|request' + Core_Object.returnJsonForLogs(
											   request_parameters),
										   'Genrate_Letters_Pdf', 'document_process')
					raw_directory_user = str(request_parameters['user_reference_number'])+str(Application_Salt)
					has_string = Core_Object.returnHashString(raw_directory_user)

					pdf_path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+has_string+'/AutoGenratedFiles'
					return_signed_create_url = pdf_path+'/'+filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(return_signed_create_url):

						_response['success'] = True
						_response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(return_signed_create_url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['transaction_id']), '|service-function|generateFillableLegalNotice|generateFillableNoticePdf|pdf-exists|'+Core_Object.returnJsonForLogs(_response),
					      'Genrate_Letters_Pdf', 'document_process')

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:
							return _response

					options = {}
					options['Bucket_Key'] = pdf_path
					options['Format'] = 'pdf'

					bytes = FillablePdf_Library.fillableLetters(request_parameters,'_sanction')
					uploaded_filename = Amazon_Library.Upload_Document_S3(bytes,options,filename)

					_response['success'] = True
					_response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(return_signed_create_url)}

			else:

				_response['success'] = False
				_response['error_code'] = 552

		except Exception as e:

			print(e)
			Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['transaction_id']),
								   '|service-function|generateSanctionLetter|generateSanctionLetterPdf|exception|' + str(e),
								   'Genrate_Letters_Pdf', 'document_process')
			_response['success'] = False
			_response['error_code'] = 553

		return _response


### Below service function not in use ####
	def generateFillableNoticePdf(self,request_parameters,Unique_Id):
		Response={}

		try:

			if request_parameters:


					Filename = 'Legal_Notice_Form_'+str(request_parameters['loan_reference_number'])

					Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['loan_reference_number']),
										   '|service-function|generateFillableLegalNotice|generateFillableNoticePdf|request' + Core_Object.returnJsonForLogs(
											   request_parameters),
										   'Genrate_Fillable_Pdf', 'document_process')
					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'

					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):


						Response['success'] = True
						Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['loan_reference_number']), '|service-function|generateFillableLegalNotice|generateFillableNoticePdf|pdf-exists|'+Core_Object.returnJsonForLogs(Response),
					      'Genrate_Fillable_Pdf', 'document_process')

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:


							return Response



					Create_Data_Dict = {}
					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'

					Create_Data_Dict['current_date'] = str(request_parameters['current_date'])
					Create_Data_Dict['user_name1_1'] = str(request_parameters['user_name'])
					Create_Data_Dict['user_name2_1'] = str(request_parameters['user_name'])
					Create_Data_Dict['user_name_3_1'] = str(request_parameters['user_name'])
					Create_Data_Dict['user_name_4'] = str(request_parameters['user_name'])
					Create_Data_Dict['user_name_5'] = str(request_parameters['user_name'])
					Create_Data_Dict['address_1_1'] = str(request_parameters['address_1'])
					Create_Data_Dict['address_1_2'] = str(request_parameters['address_2'])
					Create_Data_Dict['address_2_1'] = str(request_parameters['address_2'])
					Create_Data_Dict['address_2_2'] = str(request_parameters['address_2'])
					Create_Data_Dict['disbursement_amount'] = str(request_parameters['disbursement_amount'])
					Create_Data_Dict['disbursement_amount_word'] = str(request_parameters['disbursement_amount_word'])
					Create_Data_Dict['disbursal_date'] = str(request_parameters['disbursal_date'])
					Create_Data_Dict['loan_reference_number'] = str(request_parameters['loan_reference_number'])
					Create_Data_Dict['total_outstanding_amount'] = str(request_parameters['total_outstanding_amount'])
					Create_Data_Dict['total_outstanding_amount_word'] = str(request_parameters['total_outstanding_amount_word'])
					Create_Data_Dict['tl_name'] = str(request_parameters['tl_name'])
					Create_Data_Dict['tl_contact_number'] = str(request_parameters['tl_contact_number'])

					Bytes = FillablePdf_Library.fillableLegalNoticeForm(Create_Data_Dict)
					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Bytes,Options,Filename)

					Response['success'] = True
					Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}





			else:

				Response['success'] = False
				Response['error_code'] = 552

		except Exception as e:

			print(e)
			Core_Object.Write_Logs(str(Unique_Id) + "|" + str(request_parameters['loan_reference_number']),
								   '|service-function|generateFillableLegalNotice|generateFillableNoticePdf|exception|' + str(e),
								   'Genrate_Fillable_Pdf', 'document_process')
			Response['success'] = False
			Response['error_code'] = 553


		return Response


	def verifyAaadhaarWithPhoto(self,request_parameters,unique_id):

		Get_Source_Reference =  request_parameters['source_reference_number']

		Response = {}
		try:

			Get_Id_Proof = []
			Get_Selfie = []
			if Get_Source_Reference:

				Request_Object = {}
				Request_Object['source_reference_number'] = Get_Source_Reference
				#Request_Object['underwriter_status'] = 'APPROVE'
				Response_Object = Document_Model_Object.getDocumentList(Request_Object)

				Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |service-function|verifyAadhaarPhotoWithSelfie|verifyAaadhaarWithPhoto| '+str(Core_Object.returnJsonForLogs(Response_Object)),
				      'Face_Verify_Offile_Aadhaar', 'document_process')


				Core_Object.returnJsonForLogs(Response_Object)

				for Extract_Data in Response_Object:

					if str(Extract_Data['document_type']) == Eaadhar_Photo_Category_Type and Extract_Data['document_face'] == 'FRONT' and Extract_Data['underwriter_status'] == 'NOT_SEEN':


						Get_Id_Proof.append(Extract_Data)


					if str(Extract_Data['document_type']) in Selfie_Document_Type and Extract_Data['underwriter_status'] == 'APPROVE':


						Get_Selfie.append(Extract_Data)


			if len(Get_Selfie) > 0 and len(Get_Id_Proof) > 0:

				Get_Latest_Selfie_Object = Get_Selfie[0]
				Get_Latest_Aadhar_Xml_Photo = Get_Id_Proof[0]
				#Amazon_Library.Create_Presigned_Url(Response_Object[Counter]['document_url'])
				Create_Presigned_Selfie_Image_Url = ImageProcess_Library.convertToBytes(Amazon_Library.Create_Presigned_Url(Get_Latest_Selfie_Object['document_url']),2)
				Size_Selfie = ImageProcess_Library.getFileSizeFromCv2(Create_Presigned_Selfie_Image_Url)

				Final_Response_Object = {}
				for Id_Key in Get_Id_Proof:


						Split_Document_Url = Id_Key['document_url'].split('.')

						# Eaadhar always comes with pdf skip eaadhar for selfie match for now
						if not Split_Document_Url[1] == 'pdf':


							Source_Reference_Number = Id_Key['source_reference_number']
							Document_Reference_Number = Id_Key['document_reference_number']

							Id_Image_Object = ImageProcess_Library.convertToBytes(Amazon_Library.Create_Presigned_Url(Id_Key['document_url']),2)


							Extra_Parameters = {}
							Extra_Parameters['user_reference_number'] = Id_Key['user_reference_number']

							Size_Id = ImageProcess_Library.getFileSizeFromCv2(Id_Image_Object)


							Logs_Params = {}
							Logs_Params['unique_id'] = unique_id
							Logs_Params['source_reference_number'] = Source_Reference_Number

							Total_Size_Calculated = round((Size_Id+Size_Selfie) / 1048576)

							Response = Hyperverge_Library.verifyFaceWithId(ImageProcess_Library.convertCvtoBytes(Id_Image_Object,Total_Size_Calculated),ImageProcess_Library.convertCvtoBytes(Create_Presigned_Selfie_Image_Url,Total_Size_Calculated),Extra_Parameters,Logs_Params)

							Response['category_id'] = Id_Key['document_category']
							Response['category_type'] = Id_Key['document_type']

							Final_Response_Object[Document_Reference_Number] =  Response



				Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |service-function|verifyAadhaarPhotoWithSelfie|verifyAaadhaarWithPhoto| '+str(Core_Object.returnJsonForLogs(Final_Response_Object)),
				      'Face_Verify_Offile_Aadhaar', 'document_process')


				if Final_Response_Object:

					Update_Object = {}

					Selector_Doc_Ref_Number = Get_Latest_Aadhar_Xml_Photo['document_reference_number']
					Update_Object['extracted_data'] = json.dumps(Final_Response_Object)
					Update_Object['screening_status'] = 'APPROVED'

					Model_Response = Document_Model_Object.updateUnderwritingStatus(Selector_Doc_Ref_Number,Update_Object,unique_id)


					if Model_Response:

						Response['success'] = True

					else:

						Response['success'] = False
						Response['error_code'] = 547


					Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |model-response|verifyAadhaarPhotoWithSelfie|verifyAaadhaarWithPhoto| '+str(Model_Response),
				      'Face_Verify_Offile_Aadhaar', 'document_process')


				else:


					Response['success'] = False
					Response['error_code'] = 548
			else:


				Response['success'] = False
				Response['error_code'] = 548


		except Exception as e:

			print('Exception verifyAaadhaarWithPhoto:-'+str(e))
			Core_Object.Write_Logs(str(unique_id)+" | "+str(Get_Source_Reference), ' |exception|verifyAadhaarPhotoWithSelfie|verifyAaadhaarWithPhoto| '+str(e),
				      'Face_Verify_Offile_Aadhaar', 'document_process')

			Response['success'] = False
			Response['error_code'] = 549

		return Response

### End ###

	def migrateDocuents(self,documents_object,unique_id):

		__response = {}

		try:

			__options = {}

			# this will update data if source ref number is there
			if documents_object.get('source_reference_number'):
				is_update_success = True
				for doc_ids in documents_object['document_data']:
					response_update = Document_Model_Object.updateSourceRefDocumentsnMapping(doc_ids,documents_object.get('source_reference_number'),unique_id)
					if response_update == False:
						is_update_success = False

				Core_Object.Write_Logs(str(unique_id), '|service-function|filtered-columns|saveDocumentsData|responseUpdate| '+str(response_update),
				      'Migrate_Documents', 'document_process')

				if is_update_success:
					__response['success'] = True
					__response['data'] = {'document_ref_numbers':documents_object['document_data']}
				else:
					__response['success'] = False
					__response['error_code'] = 633

				return __response

			accepted_coloumns = ['document_url','document_category','document_type','underwriter_status','rework_reason','document_face','screening_status','extracted_data','copy_status','is_discarded','document_password','document_upload_source']
			__filtered_colomns = []

			for document_coloumns in documents_object['document_data']:
				_create_object = {}
				_create_object['source_reference_number'] = ""
				_create_object['user_reference_number'] = documents_object['user_reference_number']
				_create_object['source_type'] = 'TRANSACTION'

				for filter_col in accepted_coloumns:

					_create_object[filter_col] = document_coloumns[filter_col]

				__filtered_colomns.append(_create_object)

			Core_Object.Write_Logs(str(unique_id), '|service-function|filtered-columns|saveDocumentsData|migrateDocuents| '+str(Core_Object.returnJsonForLogs(__filtered_colomns)),
				      'Migrate_Documents', 'document_process')


			"""document_digital_data_node = documents_object['document_digital_data']
			__create_extarcted_data = {}
			__create_extarcted_data['name'] = {"conf":100,"value":document_digital_data_node['name']}
			__create_extarcted_data['gender'] = {"conf":100,"value":document_digital_data_node['gender']}
			__create_extarcted_data['birth_year'] = {"conf":100,"value":document_digital_data_node['birth_year']}
			__create_extarcted_data['father_name'] = {"conf":100,"value":document_digital_data_node['fathers_name']}
			__create_extarcted_data['mother_name'] = {"conf":100,"value":document_digital_data_node['mothers_name']}
			__create_extarcted_data['date_of_birth'] = {"conf":100,"value":document_digital_data_node['date_of_birth']}
			__create_extarcted_data['is_xerox_copy'] = "no"
			__create_extarcted_data['aadhaar_number'] = {"conf":100,"value":document_digital_data_node['user_identity_number'],"ismasked": "no"}
			__create_extarcted_data['to_be_reviewed'] = "no"
			__create_extarcted_data['document_identification'] = "aadhar_front"
			"""
			is_result_success = True
			_get_document_ref_numbers = []
			for docs_nodes in __filtered_colomns:

					with urllib.request.urlopen(docs_nodes['document_url']) as url:
						Pdf_Bytes = bytearray(url.read())

					docs_nodes['document_type_id'] = str(docs_nodes['document_type'])
					docs_nodes['source_type'] = str(docs_nodes['source_type'])
					docs_nodes['face'] = str(docs_nodes['document_face'])
					docs_nodes['source'] = 'RUFILO_APP'
					split_amazon_url = docs_nodes['document_url'].split('?')

					get_filename_extension_array = split_amazon_url[0].split('/')[-1].split('.')[1]

					"""if docs_nodes['document_type'] == 3 and docs_nodes['document_face'] == 'FRONT' and (docs_nodes['extracted_data'] == "" or docs_nodes['extracted_data'] == NULL or docs_nodes['extracted_data'] == None):
						docs_nodes['extracted_data'] = json.dumps(__create_extarcted_data)

					else:

						del docs_nodes['extracted_data']
					"""

					__options['Format'] = get_filename_extension_array
					file_name = get_filename_extension_array[0]

					document_array = self.uploadDocuments(Pdf_Bytes,file_name,docs_nodes,__options)

					Core_Object.Write_Logs(str(unique_id), '|service-function|self.uploadDocuments|saveDocumentsData|migrateDocuents| '+str(Core_Object.returnJsonForLogs(document_array)),
				      'Migrate_Documents', 'document_process')

					#document_array['document_upload_source'] = docs_nodes['document_upload_source']
					response_insert = Document_Model_Object.setDocument(document_array,unique_id)

					_get_document_ref_numbers.append(document_array['document_reference_number'])

					if not response_insert:

						is_result_success = False

			if is_result_success:

				__response['success'] = True
				__response['data'] = {'document_ref_numbers':_get_document_ref_numbers}

			else:

				__response['success'] = False
				__response['error_code'] = 631

		except Exception as error_message:

			Core_Object.Write_Logs(str(unique_id), '|service-function|exception|saveDocumentsData|migrateDocuents| '+str(error_message),
				      'Migrate_Documents', 'document_process')

			print(error_message)
			__response['success'] = False
			__response['error_code'] = 632

		return 	__response


##########################################################################
## function : get_bank_statements_service				##
## service function is used to get bank statement data			##
## method is GET							##
## function params source reference number 				##
##########################################################################
	def get_bank_statements_service(self,source_reference_number,options,unique_id):

		Response = {}
		try:

			Request_Object_Get_Documents = {}
			Request_Object_Get_Documents['source_reference_number'] = source_reference_number
			Request_Object_Get_Documents['document_category'] = '3'
			Request_Object_Get_Documents['document_type'] = '25'
			Response_Object = Document_Model_Object.getDocumentList(Request_Object_Get_Documents) # Model Call
			Get_Static_Details = ['customer_name','bank_ifsc','bank_name','customer_email','customer_phone','bank_branch_name','customer_address','customer_account_number','bank_unique_dentifier']
			Create_Data_Set = {}
			Append_Account_Numbers_Identifier = []
			Save_Other_Details = {}
			Get_Document_Numbers = {}
			Get_Date_List = {}
			for Values in Response_Object:

				Extracted_Data = json.loads(Values['extracted_data'])
				Data_Set = {}
				Create_Unique_Entry = str(Extracted_Data['customer_account_number'])+'#'+str(Extracted_Data['bank_unique_dentifier'])

				if not int(Extracted_Data['customer_account_number']) in Get_Date_List:

					Get_Date_List[int(Extracted_Data['customer_account_number'])] = []

				if not Create_Unique_Entry in Append_Account_Numbers_Identifier:

					Get_Document_Numbers[int(Extracted_Data['customer_account_number'])] = []
					Get_Document_Numbers[int(Extracted_Data['customer_account_number'])].append(Values['document_reference_number'])

					Save_Other_Details[int(Extracted_Data['customer_account_number'])] = {}
					for All_Other_Details in Extracted_Data:

						if All_Other_Details in Get_Static_Details:

							Save_Other_Details[int(Extracted_Data['customer_account_number'])][All_Other_Details] = Extracted_Data[All_Other_Details]

					Data_Set[int(Extracted_Data['customer_account_number'])] = {}
					#Data_Set[int(Extracted_Data['customer_account_number'])]['transaction_details'] = 'Jayesh Bhagat'
					for Datas in Extracted_Data['transaction_details']:

						Convert_Date_Str = Datas['transaction_date'].replace('-','')
						Get_Date_List[int(Extracted_Data['customer_account_number'])].append(str(Datas['transaction_date']))
						try:

							Data_Set[int(Extracted_Data['customer_account_number'])][Datas['transaction_date']].append(Datas)

						except Exception as e:

							Data_Set[int(Extracted_Data['customer_account_number'])][Datas['transaction_date']] = []
							Data_Set[int(Extracted_Data['customer_account_number'])][Datas['transaction_date']].append(Datas)


					Append_Account_Numbers_Identifier.append(str(Extracted_Data['customer_account_number'])+'#'+str(Extracted_Data['bank_unique_dentifier']))
					Create_Data_Set.update(Data_Set)


				else:
					Remove_Duplicate_Data = []
					Get_Document_Numbers[int(Extracted_Data['customer_account_number'])].append(Values['document_reference_number'])
					Merge_Date = {}

					Merge_Final = {}
					for Datas in Extracted_Data['transaction_details']:

						#Convert_Date_Str = Datas['transaction_date'].replace('-','')
						Get_Date_List[int(Extracted_Data['customer_account_number'])].append(str(Datas['transaction_date']))

						try:

							Merge_Date[Datas['transaction_date']].append(Datas)

						except Exception as e:

							Merge_Date[Datas['transaction_date']] = []
							Merge_Date[Datas['transaction_date']].append(Datas)

					Create_Data_Set[int(Extracted_Data['customer_account_number'])].update(Merge_Date)

			Create_Final_Object = []
			Create_Transaction_Data = []
			for Data in Create_Data_Set:

				Create_Append_Data = {}
				#Create_Append_Data[Data] = {}
				for All_Data in Create_Data_Set[Data]:

					for Single_Entry in Create_Data_Set[Data][All_Data]:

						Create_Transaction_Data.append(Single_Entry)

				Get_Customer_Details = Save_Other_Details[Data]
				Calculated_Deatails = Bank_Statment_Parsing.createStatementDataOutput(Create_Transaction_Data)


				#For Calculating AQB Balance
				AQB_BALANCE=Bank_Statment_Parsing.aqbCalcualtion(Calculated_Deatails)
				if "transaction_data" in options and options['transaction_data'] != "true":

					Calculated_Deatails.pop('transaction_details')

				Document_Reference_Numbers = Get_Document_Numbers[Data]

				Date_Range = sorted(Get_Date_List[Data], key=lambda x: datetime.strptime(x, '%Y-%m-%d'))
				Create_Statement_Start_Date = datetime.strptime(str(Date_Range[0]).strip(), "%Y-%m-%d")
				Create_Statement_Start_Date = str(Create_Statement_Start_Date.year)+'-'+str(Create_Statement_Start_Date.month)+'-'+str(Create_Statement_Start_Date.day)


				Create_Statement_End_Date = datetime.strptime(str(Date_Range[-1]).strip(), "%Y-%m-%d")
				Create_Statement_End_Date = str(Create_Statement_End_Date.year)+'-'+str(Create_Statement_End_Date.month)+'-'+str(Create_Statement_End_Date.day)


				Create_Append_Data.update(Get_Customer_Details)
				Create_Append_Data.update(
					{"document_reference_number": Document_Reference_Numbers, "average_quaterly_balance": AQB_BALANCE,"statement_start_date":Create_Statement_Start_Date,"statement_end_date":Create_Statement_End_Date})
				Create_Append_Data.update(Calculated_Deatails)
				Create_Final_Object.append(Create_Append_Data)


			if Create_Final_Object:

				Response['success'] = True
				Response['data'] = Create_Final_Object

			else:

				Response['success'] = False
				Response['error_code'] = 624


		except Exception as E:

			print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(E).__name__, E)
			Response['success'] = False
			Response['error_code'] = 625

		return Response

##################################################################################
## function :calculateEsignAttempts						##
## this service function used to calculate Esign attemps and logs		##
##################################################################################
	def calculateEsignAttempts(self,source_reference_number,Unique_id):

		try:

			Esign_Attempts = Document_Model_Object.getEsignLogs(source_reference_number)
			Hardfail = 0
			Softfail = 0
			Serverdown = 0

			Core_Object.Write_Logs(str(Unique_id) + " | " + str(source_reference_number),
								   ' |model-response|calculate_esign_attempts|calculateEsignAttempts| ' + str(
									   Esign_Attempts),
								   'Calculate_Esign_Attempts', 'document_process')

			for counts in Esign_Attempts:

				if counts['error_code'] in Esign_No_Retry:
					Hardfail = Hardfail + counts['total_count']

				elif counts['error_code'] in Esign_Only_Count:
					Softfail = Softfail + counts['total_count']

				elif counts['error_code'] in Esign_Retry_Allow:
					Serverdown = Serverdown + counts['total_count']

			Total_Count_Failure = int(Hardfail) + int(Softfail) + int(Serverdown)

			Response = {}
			Response['success'] = True
			Response['error_code'] = 0
			Response['data'] = {'hard_fail_count': Hardfail, 'soft_fail_count': Softfail,
								'total_fail_count': Total_Count_Failure}
			return Response
		except Exception as e:

			print(str(e))
			Core_Object.Write_Logs(str(Unique_id) + " | " + str(source_reference_number),
							   ' |model-response|calculate_esign_attempts|calculateEsignAttempts|Exception ' + str(e),
							   'Calculate_Esign_Attempts', 'document_process')


	def documentsCopyUpload(self,request_parameters,unique_id):

			response = {}
			try:

				Core_Object.Write_Logs(str(unique_id), '|service-function|documents_copy_upload|documentsCopyUpload|request-params|'+str(Core_Object.returnJsonForLogs(request_parameters)),
						      'Document_Copy_Upload', 'document_process')

				if 	request_parameters['copy_type'] == 'RUFILO':
					get_documents = Document_Model_Object.getDocumentsMapping(request_parameters,unique_id)



				if get_documents == False:

					response['success'] = False
					response['error_code'] = 628

					return response

				create_copy_object = []
				for document_data in get_documents:
					_make_object = {}
					_make_object['source_type'] = document_data['source_type']
					_make_object['document_reference_number'] = document_data['document_reference_number']
					_make_object['source_reference_number'] = request_parameters['new_transaction_reference_number']
					create_copy_object.append(_make_object)

				copy_documents = Document_Model_Object.copyDocumnetsMapping(create_copy_object,unique_id)
				if copy_documents:

					response['success'] = True
					response['error_code'] = 0

				else:

					response['success'] = False
					response['error_code'] = 626

				Core_Object.Write_Logs(str(unique_id), '|service-function|documents_copy_upload|documentsCopyUpload|final-response|'+str(Core_Object.returnJsonForLogs(response)),
						      'Document_Copy_Upload', 'document_process')

				return response

			except Exception as error:

				print(error)
				Core_Object.Write_Logs(str(unique_id), '|service-function|documents_copy_upload|documentsCopyUpload|exception|'+str(error),
						      'Document_Copy_Upload', 'document_process')

				response['success'] = False
				response['error_code'] = 627

				return response



# Low level use
	def updateDocuments(self,source_reference_number):

		Response_Queyr = Document_Model_Object.updateDocuments(source_reference_number)

		Response = {}
		if Response_Queyr == True:

			Response['success'] = True

		else:

			Response['error_code'] = 504
			Response['success'] = False


		return Response



	def numToWords(self,n, s):

		one = ["", "one ", "two ", "three ", "four ",
		"five ", "six ", "seven ", "eight ",
		"nine ", "ten ", "eleven ", "twelve ",
		"thirteen ", "fourteen ", "fifteen ",
		"sixteen ", "seventeen ", "eighteen ",
		"nineteen "]

		ten = ["", "", "twenty ", "thirty ", "forty ",
		"fifty ", "sixty ", "seventy ", "eighty ",
		"ninety "]

		str = ""

		if (n > 19):
			str += ten[n // 10] + one[n % 10]
		else:
			str += one[n]

		if (n):
			str += s

		return str

	def convertToWords(self,n):

		out = ""
		out += self.numToWords((n // 10000000),"crore ")

		out += self.numToWords(((n // 100000) % 100),"lakh ")

		out += self.numToWords(((n // 1000) % 100),"thousand ")

		out += self.numToWords(((n // 100) % 10),"hundred ")

		if (n > 100 and n % 100):
			out += "and "

		out += self.numToWords((n % 100), "")

		return out


	def parseBankStatment(self,Pdf_Bytes,parameters):

		return Bank_Statment_Parsing.bankStatmentPasring(Pdf_Bytes,parameters)
#####################################################################



##################################################################################
## function : updateDocumentUnderwritingStatusServiceDoc				##
## service function used to update underwriting into document table		##
## Parameters : rework_reason (file bytes)		    			##
##              underwriter_status (required params to make entry of document)	##
##		document_reference_number					##
##		decision_by_subuser_id (number / id)				##
##		source								##
##		user_reference_number						##
##################################################################################

	def updateDocumentUnderwritingStatusServiceDoc(self,request_parameters,unique_id):

		Response = {}
		try:

			Fail_Response = {}


			if request_parameters['underwriter_status'] == 'REWORK' and ('rework_reason' not in request_parameters or request_parameters['rework_reason'] == ''):

				Fail_Response['error_code'] = 518
				Fail_Response['success'] = False
				return Fail_Response


			Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatusDoc|updateDocumentUnderwritingStatusServiceDoc|Request Params| '+json.dumps(request_parameters),
					      'Update_Underwriter_Status_Doc', 'document_process')


			Selector_Doc_Ref_Number = request_parameters['document_reference_number']
			Update_Object = {}

			for Key,Values in request_parameters.items():

				if not 'document_reference_number' in Key:

						Update_Object[Key] = Values

			Current_Timestamp = datetime.fromtimestamp(datetime.now().timestamp())
			Decision_Time = Current_Timestamp.strftime("%Y-%m-%d %H:%M:%S")

			Update_Object['decision_time'] = Decision_Time


			if request_parameters['source'] and request_parameters['source'] == 'MMT':



				#
				Thirdparty_Service_Class.executeEventApiMmt(request_parameters,unique_id)


			if 'source' in Update_Object:


				del(Update_Object['source'])



			Model_Response = Document_Model_Object.updateUnderwritingStatusDoc(Selector_Doc_Ref_Number,Update_Object,unique_id)

			# Select document of aadhaar front to approve aadhaar user photo
			Request_Object = {}
			Request_Object['document_reference_number'] = request_parameters['document_reference_number']
			Request_Object['document_category'] = '2'
			Request_Object['document_type'] = '3'

			Response_Object = Document_Model_Object.getDocumentList(Request_Object) # Model Call

			if Response_Object:

				Get_Extracted_Data_Aadhaar = json.loads(Response_Object[0]['extracted_data'])
				if 'user_photo_reference_number' in Get_Extracted_Data_Aadhaar and Get_Extracted_Data_Aadhaar['user_photo_reference_number']:

					Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatusDoc|updateDocumentUnderwritingStatusServiceDoc|Update Eaadhaar Photo To Approve| ',
					      'Update_Underwriter_Status_Doc', 'document_process')

					Update_Aadhaar_Photo_Status = Document_Model_Object.updateUnderwritingStatus(Get_Extracted_Data_Aadhaar['user_photo_reference_number'],Update_Object,unique_id)




			if Model_Response == True:


				Response['success'] = True


			else:

				Response['success'] = False
				Response['error_code'] = 519


		except Exception as e:

				# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
				# tail -f /var/log/apache2/doc-service/error.log ( production)

				print('Exception updateDocumentUnderwritingStatusServiceDoc:-'+str(e))
				Core_Object.Write_Logs(str(unique_id)+" | "+str(request_parameters['user_reference_number']), ' |service-function|updateUnderwriterStatusDoc|updateDocumentUnderwritingStatusServiceDoc|Exceptions| '+str(e),
				      'Update_Underwriter_Status_Doc', 'document_process')

				Response['success'] = False
				Response['error_code'] = 520



		return Response

##################################################################################
## function : genrateAllFillablePdf						##
## service function used to generate fillable application form 			##
##										##
## Parameters : source_reference_number						##
##		user_reference_number						##
##		create_forcefully (Yes:Application form will generate new entry)##
## 			    	   No : Last created entry will be return	##
##		form_type : (Optional ESIGN | SELFIESIGN)			##
##################################################################################
	def generateNocLetter(self,request_parameters,Unique_Id):

			Response = {}

			try:

				if request_parameters:

					Raw_Directory_User = str(request_parameters['user_reference_number'])+str(Application_Salt)
					Has_String = Core_Object.returnHashString(Raw_Directory_User)

					Filename = 'Noc_Letter_'+str(request_parameters['loan_reference_number'])

					Pdf_Path = Bucket_Dir+'/'+request_parameters['user_reference_number']+'/'+Has_String+'/AutoGenratedFiles'
					Return_Signed_Create_Url = Pdf_Path+'/'+Filename+'.pdf'

					if Amazon_Library.Check_Amazon_Path_Exists(Return_Signed_Create_Url):


						Response['success'] = True
						Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

						Core_Object.Write_Logs(str(Unique_Id)+"|"+str(request_parameters['transaction_id']), '|service-function|generateNoc|generateNocLetter|pdf-exists|'+Core_Object.returnJsonForLogs(Response),
					      'Generate_Noc', 'document_process')

						# If forcefully parameter is set create new pdf all over again if not set display already created pdf
						if 'create_forcefully' not in request_parameters:


							return Response


					Options = {}
					Options['Bucket_Key'] = Pdf_Path
					Options['Format'] = 'pdf'


					Bytes = FillablePdf_Library.fillableNocApplication(request_parameters)
					Uploaded_Filename = Amazon_Library.Upload_Document_S3(Bytes,Options,Filename)

					Response['success'] = True
					Response['data'] = {"pdf_url":Amazon_Library.Create_Presigned_Url(Return_Signed_Create_Url)}

					return Response

			except Exception as e:

					# Print exception is to check directly on server via tail -f /var/log/apache2/error.log ( test)
					# tail -f /var/log/apache2/doc-service/error.log ( production)
					print('Error on line {}'.format(sys.exc_info()[-1].tb_lineno), type(e).__name__, e)
					Core_Object.Write_Logs(str(Unique_Id), ' |service-function|genrateFillablePdf|genrateAllFillablePdf|Exceptions| '+str(e),
				      'Generate_Noc', 'document_process')

					Response['error_code'] = 627
					Response['success'] = False



			return Response



