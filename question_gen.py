
import openai
import json

openai.api_key = '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'



prompt1 = """

Generate another question like the one below, formatted in JSON as below.
All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
Backslashes must be escaped as below to ensure compatibility with JSON.
Make sure the math is correct.

{
 "question content": "Which expression is equivalent to $12y^2 + 8y$?",
        "choices": {
            "A": "$4y(3y + 2)$",
            "B": "$8y(12y + 1)$",
            "C": "$12y(y + 8)$",
            "D": "$y^2(12y + 8)$"
        },
        "correct answer": "A",
        "answer explanation": "To factor $12y^2 + 8y$, we need to find the greatest common factor (GCF) of the two terms. The GCF of $12y^2$ and $8y$ is $4y$, so we can factor out $4y$ from both terms, which gives us $4y(3y + 2)$."
    }

"""

prompt2 = """
Generate another question like the one below, formatted in JSON as below.
All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
Backslashes must be escaped as below to ensure compatibility with JSON.
Make sure the math is correct.

{
        "question content": "Which expression is equivalent to $x^2 - 3x - 10$?",
        "choices": {
            "A": "$(x - 1)(x + 10)$",
            "B": "$(x - 4)(x + 3)$",
            "C": "$(x - 2)(x + 5)$",
            "D": "$(x - 5)(x + 2)$"
        },
        "correct answer": "D",
        "answer explanation": "To factor $x^2 - 3x - 10$, we look for two numbers that multiply to -10 and add up to -3. The numbers 2 and -5 meet these criteria since $2 \\times -5 = -10$ and $2 + (-5) = -3$. Therefore, the factored form is $(x - 5)(x + 2)$."
    }

"""


prompt3 = """
Generate another question like the one below, formatted in JSON as below.
All mathematical language needs to be converted to LaTeX utilizing single dollar signs for inline math mode and double dollar signs for a displayed equation. 
Backslashes must be escaped as below to ensure compatibility with JSON.
Make sure the math is correct.

{
    "question content": "One of the factors of $2x^3 + 24x^2 + 72x$ is $x + b$, where $b$ is a positive constant. What is the smallest possible value of $b$?",
    "correct answer": "4",
    "answer explanation": "To factor $2x^3 + 24x^2 + 72x$, we look for the greatest common factor (GCF) which is $2x$. This leaves us with $2x(x^2 + 12x + 32)$. The factors of 32 that add up to 12 are 8 and 4. Since we need the smallest possible positive value of $b$, we choose 4, making the factor $x + 4$. Therefore, the smallest possible value of $b$ is 4."
}

"""



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



# for gpt 4
def generate_new_response(prompt):
  response = openai.ChatCompletion.create(
    model="gpt-4-0125-preview",
    messages=[{"role": "user", "content": prompt}]
  )
  return response.choices[0].message.content


prompts = [prompt1, prompt2, prompt3]

#generate labeled questions from multiple prompts
labeled_questions = {}
i = 1
while i < 5:  
      try:
          # LLM calls

        prompt = prompts[i % len(prompts)]
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
