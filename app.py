import openai
import streamlit as st
import ast
import subprocess
import os
import re

# Configure OpenAI API Key
openai.api_key = "your_openai_api_key"

def analyze_code(language: str, snippet: str) -> str:
    """
    Analyzes the provided code snippet for syntax errors based on the selected language.

    Args:
        language (str): The programming language chosen by the user.
        snippet (str): The code snippet to be analyzed.

    Returns:
        str: A message indicating whether syntax errors were found.
    """
    temp_filename = "temp_code"
    output_filename = "temp_executable"

    try:
        if language == "Python":
            try:
                ast.parse(snippet)  # Check Python code syntax using AST
                exec(snippet)  # Execute the code to check for runtime issues
                return "No syntax errors detected."
            except SyntaxError as e:
                return f"Syntax Error: {e}"
            except Exception as e:
                return f"Runtime Error: {e}"

        elif language in ["C", "C++"]:
            # For C/C++, write the code to a temporary file
            temp_filename += ".c" if language == "C" else ".cpp"
            with open(temp_filename, "w") as f:
                f.write(snippet)
            
            compiler = "gcc" if language == "C" else "g++"
            # Run the compiler and capture any errors
            process = subprocess.run(
                [compiler, temp_filename, "-o", output_filename],
                capture_output=True,
                text=True
            )

            if process.returncode == 0:
                return "No syntax errors detected."
            else:
                return f"Syntax Error: {process.stderr.strip()}"

        elif language == "Java":
            # For Java, check for the main public class
            match = re.search(r"public\s+class\s+(\w+)", snippet)
            if match:
                temp_filename = f"{match.group(1)}.java"
                with open(temp_filename, "w") as f:
                    f.write(snippet)
                # Compile the Java code and check for errors
                process = subprocess.run(
                    ["javac", temp_filename],
                    capture_output=True,
                    text=True
                )
                if process.returncode == 0:
                    return "No syntax errors detected."
                else:
                    return f"Syntax Error: {process.stderr.strip()}"
            else:
                return "Syntax Error: Could not determine the public class name in the Java code."

        else:
            return "Language not supported for syntax validation."
    finally:
        # Clean up temporary files after processing
        for file in [temp_filename, output_filename]:
            if os.path.exists(file):
                os.remove(file)

def suggest_optimizations(language: str, snippet: str) -> str:
    """
    Uses GPT to generate suggestions for optimizing the provided code snippet.

    Args:
        language (str): The programming language of the code.
        snippet (str): The code to analyze for optimization.

    Returns:
        str: Suggested improvements or optimizations for the code.
    """
    try:
        # Use OpenAI's GPT model to generate optimization suggestions
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Ensure you're using the correct GPT model
            messages=[
                {"role": "system", "content": f"You are a helpful assistant skilled in {language} code analysis."},
                {"role": "user", "content": f"The following {language} code may have performance or syntactic issues:\n\n{snippet}\n\nProvide detailed suggestions for optimization, explaining your reasoning."}
            ],
            max_tokens=150
        )
        return response['choices'][0]['message']['content'].strip()
    except Exception as e:
        return f"Error generating optimization suggestions: {str(e)}"

# Streamlit Interface to interact with the tool
st.title("AI-Powered Code Analyzer")

# Dropdown menu to select programming language
language = st.selectbox("Select Programming Language", ["Python", "C", "C++", "Java"])

# Text area to input code snippet
code_input = st.text_area(f"Paste your {language} code below:", height=200)

if st.button("Analyze Code"):
    if code_input.strip():
        with st.spinner("Analyzing..."):
            # Perform syntax validation
            syntax_result = analyze_code(language, code_input)
            # Generate optimization suggestions using GPT
            suggestions = suggest_optimizations(language, code_input)
        
        # Display syntax validation result
        st.subheader("Syntax Validation")
        st.write(syntax_result)
        
        # Display optimization suggestions
        st.subheader("Optimization Suggestions")
        st.write(suggestions)
    else:
        st.error("Please paste some code before analyzing!")
