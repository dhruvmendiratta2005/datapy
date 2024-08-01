# import module
from pdf2image import convert_from_path
from modules import log
import os

def pdf_to_image(pdf_path):
	
	# convert pdf to image
	try:
		images = convert_from_path(pdf_path)
	except Exception as e:
		log.log('Error converting pdf to image', 'error')
		print(e)
		return False
	
	#save images to temporary folder
	try:
		#make dir temp if not exists
		if not os.path.exists('temp'):
			os.makedirs('temp')
		else:
			#remove all files in temp
			files = os.listdir('temp')
			for file in files:
				os.remove('temp/'+file)
		
		for i in range(len(images)):
			images[i].save('temp/'+str(i)+'.jpg', 'JPEG')
	except Exception as e:
		log.log('Error saving image:', 'error')
		print(e)
		return False
	
	return True
	

