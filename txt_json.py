import json

file_path = "all_reading.txt"

# Refined function to address the specified corrections
def parse_questions_to_json_refined(file_path):
    questions = []
    current_question = {}
    question_text_lines = []
    capturing_rationale = False
    rationale_text = ""
    
    def add_current_question():
        if current_question:
            # Ensure the question text is set correctly before the choices
            current_question["question content"] = " ".join(question_text_lines).strip()
            current_question["choices"] = current_question.pop("choices")
            if capturing_rationale:
                current_question["answer explanation"] = rationale_text.strip()
            questions.append(current_question.copy())
            
    with open(file_path, 'r') as file:
        lines = file.readlines()
        
        for line in lines:
            line = line.strip()
            if line.startswith("Question ID"):
                add_current_question()  # Add the previous question to the list
                current_question.clear()
                question_text_lines.clear()
                rationale_text = ""
                capturing_rationale = False
                current_question["question id"] = line.split()[-1]
                current_question["choices"] = {}
            elif line.startswith("ID: ") and "Answer" not in line and not question_text_lines:
                # Start capturing question text after the first ID line
                continue
            elif line.startswith("A. ") or line.startswith("B. ") or line.startswith("C. ") or line.startswith("D. "):
                choice = line.split(". ", 1)[0]
                text = line.split(". ", 1)[1]
                current_question["choices"][choice] = text
            elif line.startswith("ID: ") and "Answer" in line:
                # Skip adding to question text
                continue
            elif line.startswith("Rationale"):
                capturing_rationale = True
                rationale_text += line.partition("Rationale")[2].strip() + " " if line.partition("Rationale")[2] else ""
            elif capturing_rationale:
                rationale_text += line + " "
            else:
                question_text_lines.append(line)
                
    add_current_question()  # Add the last question to the list
    
    return json.dumps(questions, indent=4)

# Re-parse the document with refined adjustments
json_output_refined = parse_questions_to_json_refined(file_path)

# Save the refined JSON output to a new file
output_file_path_refined = 'r_w_parsed_from_txt.json'
with open(output_file_path_refined, 'w') as json_file:
    json_file.write(json_output_refined)



