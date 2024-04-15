import fitz  # PyMuPDF
import base64
from PIL import Image
import io
import json
from openai import OpenAI


def pdf_pages_to_base64(pdf_path):
    doc = fitz.open(pdf_path)
    base64_images = []

    for page in doc:
        # Convert the PDF page to a PIL Image object
        pix = page.get_pixmap()
        img_bytes = pix.tobytes("png")
        img = Image.open(io.BytesIO(img_bytes))
        
        # Convert the PIL Image to base64
        buffered = io.BytesIO()
        img.save(buffered, format="PNG")
        img_base64 = base64.b64encode(buffered.getvalue()).decode()

        base64_images.append(img_base64)

    return base64_images

pdf_path = "missed_questions.pdf"
base64_images = pdf_pages_to_base64(pdf_path)

# openai version: 1.14.3
client = OpenAI(api_key = '')

prompt = """
    This is an image of a pdf.  Put this image in the JSON format below.  If there is a graph or geometric figure, put in the figure description key value a description of the graph or figure for someone who cannot see the graph or figure.  If there is no graph or figure, leave the figure description as an empty string.
    Values with exponents were not rendered properly in the original pdf as signified by the text "msup".  If you see "msup", use clues in the rest of the image to replace "msup" with the correct content.
    Equations that are not inline with the question text or not included in the question key value should be put in the equation key value.  However, do not create an equation that is not already explicitly displayed in the image or problem statement.
    If there are no answer choices, leave the choices key value as an empty string.
    If there is tabular data, put it in the table key format below, otherwise leave the table key value as an empty string.
    The image may be the continuation of the previous question's explanation and not have it's own question ID.  If the image has no question ID, put "YES" in the "continuation" key value.  Otherwise put "NO".
    All math content inside the question, equation, choices, and answer explanation key values should be surrounded by single dollar signs (e.g. $x$, $Ax + By = C$ ) put in LaTeX and double escaped (e.g. \\\\leq, \\\\sqrt, \\\\(, \\\\)) to be compatible with JSON.  
    Your response should only contain the formatted JSON content.  No explanations of what you did or why.
    {
    "question id": "",
    "figure description": "",
    "question content": "",
    "table": {
            "headers": [
                "",
                ""
                            ],
            "rows": [
                {
    
                },
                {
                
                }

            ]
    },
    "answer explanation": "",
    "choices": {
        "A": "",
        "B": "",
        "C": "",
        "D": ""
    },
    "continuation": ""
    }

    """

def get_api_response(image_data_url):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt 
                     },
                    {
                        "type": "image_url",
                        "image_url": {
                          "url": image_data_url
                        }                    
                    }
                ]
            }
        ],
        max_tokens=2000
    )
  
    return response.choices[0].message.content


def generate_from_two_images(url1, url2):
    response = client.chat.completions.create(
        model="gpt-4-vision-preview",
        messages=[
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt
                     },
                    {
                        "type": "image_url",
                        "image_url": {
                          "url": url1
                        }                    
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                          "url": url2
                        }                    
                    }
                ]
            }
        ],
        max_tokens=2000
    )
  
    return response.choices[0].message.content


def remove_markdown(api_response):
    if api_response.startswith("```json") and api_response.endswith("```"):
        # Strip the leading ```json and the trailing ```
        api_response = api_response[len("```json"):-len("```")].strip()
    return api_response

len_image_list = len(base64_images)
question_kv_pair_list = {}
question_num = 1
json_file_path = 'missed_questions.json'
i = 0
# page number is i + 1
while i < len_image_list:    
    try:
        image_data_url = f"data:image/png;base64,{base64_images[i]}"
        api_response = get_api_response(image_data_url)
        api_response = remove_markdown(api_response)
        
        # Attempt to parse the JSON
        json_response = json.loads(api_response)
        
        if json_response["continuation"] == "merp": # "YES"
            print(f"Page {i+1} is a continuation.  Adding content from this page to previous question.")
            question_num -= 1            
            image_data_url1 = f"data:image/png;base64,{base64_images[i]}"
            image_data_url2 = f"data:image/png;base64,{base64_images[i-1]}"
            api_response = generate_from_two_images(image_data_url1, image_data_url2)
            api_response = remove_markdown(api_response)
            # Attempt to parse the JSON again
            json_response = json.loads(api_response)
            # If parsing is successful, add to kv_pair list and iterate accordingly
            question_kv_pair_list[f"Question {question_num}"] = json_response
            print(f"Pages {i} and {i+1} successfully added to question {question_num}")

        else:
            # If parsing is successful, add to kv_pair list and iterate accordingly
            question_kv_pair_list[f"Question {question_num}"] = json_response
            print(f"Page {i+1} successfully added to question {question_num}")
        
        i += 1
        question_num += 1
        
        # Write to file often
        if i % 5 == 0:
            json_qs = json.dumps(question_kv_pair_list, indent=4)
            with open(json_file_path, 'w') as file:
                file.write(json_qs)


    except json.JSONDecodeError as error:
        print(f"Error parsing JSON for page {i+1}: {error}")
        print(api_response)
        continue



json_qs = json.dumps(question_kv_pair_list, indent=4)
with open(json_file_path, 'w') as file:
    file.write(json_qs)

# Read the file
with open(json_file_path, 'r') as file:
    questions = json.load(file)

# Iterating through each question and adding an empty "image" key if it doesn't exist
for question_key, question_value in questions.items():
    if "image" not in question_value:
        question_value["image"] = ""  # or None, or an empty dict {}, depending on your needs


# Save formatted questions to a new file
json_qs = json.dumps(questions, indent=4)
with open(json_file_path, 'w') as file:
    file.write(json_qs)

print("Image key added")
