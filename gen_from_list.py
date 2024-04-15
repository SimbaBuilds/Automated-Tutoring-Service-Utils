
import openai
import json

openai.api_key = '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'

def get_prompt(i):
    prompt1_list = ['x^2 - -17x + c = 0 + c',
    'x^2 - 16x + c = 0 + c',
    'x^2 - 5x + c = 0 + c',
    'x^2 - 12x + c = 0 + c',
    'x^2 - 1x + c = 0 + c',
    'x^2 - 0x + c = 0 + c',
    'x^2 - 14x + c = 0 + c',
    'x^2 - -12x + c = 0 + c',
    'x^2 - 17x + c = 0 + c',
    'x^2 - -18x + c = 0 + c']

    prompt1 = f"""

    Generate another question like the one below, utilizing the expression: {prompt1_list[i%10-1]}, formatted in JSON as below.
    All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
    Backslashes must be double escaped to ensure compatibility with JSON (e.g. \\\\), \\\\(, \\\\frac ).
    Make sure the math is correct.

    {{

      "question content": ""

      "answer explanation": ""

      "correct answer": ""
    }}

    """

    prompt2_list = ['x^2 + 10x + -4',
    'x^2 + -4x + 1',
    'x^2 + 0x + 2',
    'x^2 + 6x + 8',
    'x^2 + 4x + 8',
    'x^2 + 3x + -2',
    'x^2 + -10x + 6',
    'x^2 + -2x + 4',
    'x^2 + 7x + 1',
    'x^2 + 3x + -1']
    prompt2 = f"""
    Generate another question like the one below, utilizing the expression: {prompt2_list[i%10-1]}, formatted in JSON as below.
    All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
    Backslashes must be double escaped to ensure compatibility with JSON (e.g. \\\\), \\\\(, \\\\frac ).
    Make sure the math is correct.

   {{

      "question content": ""

      "answer explanation": ""

      "correct answer": ""
    }}


    """

    prompt3_list = ['x^2 + y^2 + -7x + 0y + 0 = 0',
    'x^2 + y^2 + 9x + 0y + -8 = 0',
    'x^2 + y^2 + 8x + -5y + -17 = 0',
    'x^2 + y^2 + -1x + -4y + 2 = 0',
    'x^2 + y^2 + -4x + 10y + 13 = 0',
    'x^2 + y^2 + -4x + -2y + 13 = 0',
    'x^2 + y^2 + 5x + -2y + 13 = 0',
    'x^2 + y^2 + 4x + -2y + -20 = 0',
    'x^2 + y^2 + 0x + 5y + 11 = 0',
    'x^2 + y^2 + 9x + 6y + 15 = 0']
    prompt3 = f"""
    Generate another question like the one below, utilizing the expression: {prompt3_list[i%10-1]}, formatted in JSON as below.
    All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
    Backslashes must be double escaped to ensure compatibility with JSON (e.g. \\\\), \\\\(, \\\\frac ).
    Make sure the math is correct.

  {{

      "question content": ""

      "answer explanation": ""

      "correct answer": ""
    }}


    """
    prompts = [prompt1, prompt2, prompt3]
    prompt = prompts[i % len(prompts)]
    return prompt


# # for gpt 3.5 instruct
# def generate_new_response(prompt):
#     response = openai.Completion.create(
#     model="gpt-3.5-turbo-instruct",
#     prompt=prompt,
#     max_tokens=1000,
#     temperature=0.5,
#     top_p=1,
#     frequency_penalty=0,
#     presence_penalty=0
#     )
#     return response.choices[0].text.strip()



# for gpt 4 turbo, pip install openai==0.28
def generate_new_response(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-4-0125-preview",
    messages=[{"role": "user", "content": prompt}]
  )
  return response.choices[0].message.content




#generate labeled questions from multiple prompts
labeled_questions = {}
i = 1
while i < 5:  
      try:
          # LLM calls
        prompt = get_prompt(i)
        question_text = generate_new_response(prompt)
        # Remove the Markdown code block formatting at the beginning and end
        if question_text.startswith("```json") and question_text.endswith("```"):
            # Strip the leading ```json and the trailing ```
            question_text = question_text[len("```json"):-len("```")].strip()

        # Attempt to parse the JSON
        question_dict = json.loads(question_text)
        
        # If parsing is successful, add to labeled_questions
        labeled_questions[f"Question {i}"] = question_dict
        print(f"Question {i} successfully added to list")
        i += 1  # Only increment if parsing succeeds

      
      except json.JSONDecodeError as e:
          print(f"Error parsing JSON for question {i}: {e}")
          print(question_text)
          # Optionally, log the bad question text for review later
          # You could continue to the next iteration without incrementing i,
          # effectively retrying the current question number
          continue

# Convert the dictionary to JSON string
json_qs = json.dumps(labeled_questions, indent=4)

with open('test.json', 'w') as file:
    file.write(json_qs)
