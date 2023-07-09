import streamlit as st
import base64

def show_pdf(file_path, page_number, iframe_id):
    with open(file_path, "rb") as f:
        base64_pdf = base64.b64encode(f.read()).decode("utf-8")
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}#page={page_number}" width="100%" height="600" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)

file_path = "C:/Users/tarifat/OneDrive - Microsoft/MTC/2023-06-16 Mott MacDonald/Sample Data/Contract for the Design and Construction of a New Bridge.pdf"
page_number = 1
iframe_id = "pdf-iframe"

if st.button("Page Change"):
    st.write("", key=iframe_id)
    page_number = 5
    show_pdf(file_path, page_number, iframe_id)

show_pdf(file_path, page_number, iframe_id)