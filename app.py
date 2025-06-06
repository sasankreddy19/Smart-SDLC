import streamlit as st
import os
from utils import read_python_file, write_python_file, ensure_directory, load_config, logger
from doc_generator import add_docstrings
from code_review import review_code
from bug_predictor import predict_bugs
from report_generator import generate_project_report

# Load configuration
config = load_config()
output_dir = config.get("output_dir", "data/output")
max_file_size = config.get("max_file_size"

, 1048576)  # 1MB default

# Ensure output directory exists
ensure_directory(output_dir)

# Streamlit app configuration
st.set_page_config(page_title="SmartSDLC", page_icon="🚀", layout="wide")

# App title and description
st.title("SmartSDLC: AI-Powered Software Development Lifecycle Tool")
st.markdown("Upload a Python file or ZIP archive to generate docstrings, review code quality, predict potential bugs, and create a project report.")

# File uploader
uploaded_file = st.file_uploader("Choose a file", type=["py", "zip"], help="Max file size: 1MB")

if uploaded_file is not None:
    # Check file size
    if len(uploaded_file.getvalue()) > max_file_size:
        st.error(f"File size exceeds {max_file_size / 1024 / 1024:.1f}MB limit.")
    else:
        # Save uploaded file temporarily
        input_path = os.path.join(output_dir, f"temp_input.{uploaded_file.name.split('.')[-1]}")
        output_path = os.path.join(output_dir, "temp_output.py")
        
        if write_python_file(uploaded_file.getvalue().decode("utf-8", errors="ignore"), input_path):
            # Display uploaded code if it's a Python file
            if input_path.endswith('.py'):
                st.subheader("Uploaded Code")
                st.code(read_python_file(input_path), language="python")
            
            # Create four columns for functionalities
            col1, col2, col3, col4 = st.columns(4)
            
            # Docstring Generation
            with col1:
                st.subheader("Generate Docstrings")
                if st.button("Generate Docstrings"):
                    with st.spinner("Generating docstrings..."):
                        try:
                            if input_path.endswith('.py'):
                                if add_docstrings(input_path, output_path):
                                    output_code = read_python_file(output_path)
                                    st.code(output_code, language="python")
                                    st.success("Docstrings generated successfully!")
                                    st.download_button(
                                        label="Download File with Docstrings",
                                        data=output_code,
                                        file_name="output_with_docstrings.py",
                                        mime="text/x-python"
                                    )
                                else:
                                    st.error("Failed to generate docstrings.")
                            else:
                                st.error("Docstring generation is only available for .py files.")
                        except Exception as e:
                            logger.error(f"Docstring generation error: {str(e)}")
                            st.error(f"Error generating docstrings: {str(e)}")
            
            # Code Review
            with col2:
                st.subheader("Code Review")
                if st.button("Review Code"):
                    with st.spinner("Reviewing code..."):
                        try:
                            if input_path.endswith('.py'):
                                review_comments = review_code(input_path)
                                st.write("**Code Review Comments:**")
                                for comment in review_comments:
                                    st.write(f"- {comment}")
                            else:
                                st.error("Code review is only available for .py files.")
                        except Exception as e:
                            logger.error(f"Code review error: {str(e)}")
                            st.error(f"Error in code review: {str(e)}")
            
            # Bug Prediction
            with col3:
                st.subheader("Bug Prediction")
                if st.button("Predict Bugs"):
                    with st.spinner("Predicting bugs..."):
                        try:
                            if input_path.endswith('.py'):
                                bug_predictions = predict_bugs(input_path)
                                st.write("**Potential Bugs:**")
                                for bug in bug_predictions:
                                    st.write(f"- {bug}")
                            else:
                                st.error("Bug prediction is only available for .py files.")
                        except Exception as e:
                            logger.error(f"Bug prediction error: {str(e)}")
                            st.error(f"Error in bug prediction: {str(e)}")
            
            # Project Report Generation
            with col4:
                st.subheader("Generate Documentation")
                if st.button("Generate Project Report"):
                    with st.spinner("Generating project report..."):
                        try:
                            success, result, report_type = generate_project_report(input_path, output_dir, uploaded_file.name)
                            if success:
                                with open(result, "rb") as f:
                                    if report_type == "pdf":
                                        st.success("Project report (PDF) generated successfully!")
                                        st.download_button(
                                            label="Download Project Report (PDF)",
                                            data=f,
                                            file_name="project_report.pdf",
                                            mime="application/pdf"
                                        )
                                    elif report_type == "txt":
                                        st.warning("PDF generation failed; generated plain text report instead.")
                                        st.download_button(
                                            label="Download Project Report (Text)",
                                            data=f,
                                            file_name="project_report.txt",
                                            mime="text/plain"
                                        )
                            else:
                                st.error(result)
                        except Exception as e:
                            logger.error(f"Report generation error: {str(e)}")
                            st.error(f"Error generating project report: {str(e)}")
            
            # Clean up temporary files
            for path in [input_path, output_path]:
                if os.path.exists(path):
                    os.remove(path)
                    logger.info(f"Cleaned up {path}")
        else:
            st.error("Failed to save uploaded file.")
else:
    st.info("Please upload a Python file or ZIP archive to begin.")