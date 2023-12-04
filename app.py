import streamlit as st
import cv2
import matplotlib.pyplot as pt
import numpy as np
from PIL import Image
import io
import requests
import base64
from tempfile import NamedTemporaryFile
import logging

logging.basicConfig(filename="logfile.log",
                    format='%(asctime)s %(message)s',
                    filemode='w')

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

st.set_page_config(layout="wide")
st.title("Sketch Generator")
st.caption("Use high resolution image to get optimal results")
      
def verify_url(url):  
    try:
        encoded_content = url.split(',')[1]
        image_data = base64.b64decode(encoded_content)
        image = Image.open(io.BytesIO(image_data))
        logger.info("Valid Base64 Url")
        return True, image
    except Exception as e:
        logger.warning("Please Enter a valid Image url"+str(e))
        return False, None
    
def http_url_image(nk04200111):
    try:
        # Send an HTTP request to the URL
        response = requests.get(nk04200111)
        response.raise_for_status()  # Raise an error for bad responses

        # Open the image using PIL
        image = Image.open(io.BytesIO(response.content))
        logger.info("Valid http Url")
        return True, image

    except Exception as e:
        logger.warning("Please Enter a valid Image url"+str(e))
        return False, None

def process_image(url_string,validation):
    try:
        if validation=="http":
            result,upload = http_url_image(url_string)
        elif validation=="data":
            result,upload = verify_url(url_string)
        if result:
            image_np = np.array(upload)
            firstimg=cv2.cvtColor(image_np,cv2.COLOR_BGR2GRAY)
            blurs=cv2.bitwise_not(firstimg)
            secondimg=cv2.GaussianBlur(blurs, (21, 21),sigmaX=30, sigmaY=30)
            finalimg = cv2.divide(firstimg, 255 - secondimg, scale=256)
            column1,column2,column3,column4=st.columns([1,4,4,1])
            with column1:
                pass
            with column2:
                st.image(upload, caption="Original Image", width=600, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
            with column3:
                if finalimg is not None:
                    st.image(finalimg, caption="Final Image", width=600, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
                            
            with column4:
                pass
            logger.info("Image was processed successfully")
        else:
            st.write(f"The URL {url_string} does not contain a valid image.")
            logger.warning(f"The URL {url_string} does not contain a valid image.")
        return finalimg
    except Exception as e:
        logger.error("Exception occured while processing image: "+str(e))

def get_base64_data(data, filename):
    try:
        base64_data = base64.b64encode(data).decode()
        download_link = f'<a href="data:application/octet-stream;base64,{base64_data}" download="{filename}">Download {filename}</a>'
        logger.info("Download Link created successfully")
        return download_link
    except Exception as e:
        logger.error("Unable to create download link"+str(e))

def save_image(finalimg):
    try:
        NKIMAGES=Image.fromarray(finalimg)
        buffer = io.BytesIO()
        NKIMAGES.save(buffer, format="PNG")
        logger.info("Image was converted successfully")
        # Provide a link for the user to download the processed image
        st.markdown(get_base64_data(buffer.getvalue(), "Final Image.png"), unsafe_allow_html=True)
    except Exception as e:
        logger.error("Image conversion failed"+str(e))
        

def uploadfile():
    try:
        firstimg=None
        secondimg=None
        finalimg=None
        val=1
        selection=st.radio(" ", ["Enter Image Url:link:","Upload Image File:open_file_folder:"], index=None, disabled=False, horizontal=True, label_visibility="visible")
        
        if selection=="Enter Image Url:link:":
            cols1,cols2=st.columns([5,1])
            url_string=st.text_input(" ", type="default", placeholder="Enter the image Url", label_visibility="collapsed")
            if st.button("Generate"):
                if url_string !="" and url_string[:4]=="http":
                    finalimg=process_image(url_string,"http")
                    save_image(finalimg)
                elif url_string !=""and url_string[:4]=="data":
                    finalimg=process_image(url_string,"data")
                    save_image(finalimg)
                else:
                    val=2
            if val==2:
                st.write("Enter a valid image url")
        elif selection=="Upload Image File:open_file_folder:":
            uploader=st.file_uploader("Upload the image here", type=None, accept_multiple_files=False, disabled=False, label_visibility="visible")
            if uploader is None:
                st.write("Please upload an image")
            else:
                upload=uploader.read()
                if st.button("Generate"):
                    image_np = np.array(Image.open(io.BytesIO(upload)))
                    firstimg=cv2.cvtColor(image_np,cv2.COLOR_BGR2GRAY)
                    blurs=cv2.bitwise_not(firstimg)
                    secondimg=cv2.GaussianBlur(blurs, (21, 21),sigmaX=30, sigmaY=30)
                    finalimg = cv2.divide(firstimg, 255 - secondimg, scale=256)
                    
                column1,column2,column3,column4=st.columns([1,4,4,1])
                with column1:
                    pass
                with column2:
                        st.image(upload, caption="Original Image", width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
                with column3:
                    if finalimg is not None:
                        st.image(finalimg, caption="Final Image", width=None, use_column_width=None, clamp=False, channels="RGB", output_format="auto")
                
                with column4:
                    pass
                save_image(finalimg)
                logger.info("Program ran successfully")
    except Exception as e:
        logger.error("Error occured in uploadfile"+str(e))
        
if __name__=="__main__":
    uploadfile()
