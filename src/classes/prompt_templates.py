from langchain_core.prompts import ChatPromptTemplate

initial_transcription_template = """
You are a highly skilled Software Architect. Your task is to analyze the provided transcription to extract software requirements, identify potential issues, and gather all relevant context.

Please use the following transcription as your source material:
{documents}

Your response should include:
1. A detailed summary of the transcription.
2. A list of identified requirements and any ambiguities or issues found.
3. Suggestions for possible improvements or changes.
4. A set of proposed User Stories, each with:
    - Title
    - Description
    - Acceptance Criteria

Present your analysis in a clear, organized, and professional manner.
Return a json with 2 keys:
    - "summary", that contains the detailed summary of the transcription in markdown format.
    - "user_stories", that contains a list of user stories derived from the transcription.
Ensure that your response is thorough and provides valuable insights for further development.
"""

answer_template = """
Answer the following question: {question}
use {documents} to help answer the question.
"""

history_analysis_template = """
You are a skilled Software Architect. Provided below is a JSON containing the complete history of an Azure DevOps work item.

Your tasks:
1. Summarize the key interactions and changes throughout the work item lifecycle.
2. identify any patterns or recurring themes in the comments and updates.
3. Highlight any significant decisions or changes that impacted the work item progression.
4. Let me know which phase of SDLC is taking most of the time and why
5. Provide insights or recommendations based on the analysis of the history.
6. Estimate the time spent in each phase of the SDLC for each work item.
7. Estimate time effort for each work item to be completed.
8. Predict risk of not completing each work item on time.

Here is the work item title, description, acceptance criteria and current status:
{work_item_info}

Here is the work item history:
{history_json}

Here is the comments history:
{comments_json}
"""

multiple_history_analysis_template = """
You are a skilled Software Architect. Provided below is a JSON containing the complete history of an Azure DevOps work items.

Your tasks:
1. Summarize the key interactions and changes throughout the work items lifecycle.
2. identify any patterns or recurring themes in the comments and updates.
3. Highlight any significant decisions or changes that impacted the work items progression.
4. Let me know which phase of SDLC is taking most of the time and why
5. Provide insights or recommendations based on the analysis of the history.
6. Estimate the time spent in each phase of the SDLC for each work item.
7. Estimate time effort for each work item to be completed.
8. Predict risk of not completing each work item on time.
9. Sort the work items depending of the priority of being addressed, and provide an explanation for the prioritization.

Here is the work items title, description, acceptance criteria and current status:
{work_items_info}

Here is the work items history:
{history_json}

Here is the comments history:
{comments_json}
"""


code_analysis_template = """
You are a highly skilled Software Architect. Your task is to analyze the provided code changes to extract software requirements, identify potential issues, and gather all relevant context.
Please use the following code changes as your source material:
{code_changes}

Your response should include:
1. A detailed summary of the code changes.
2. A list of identified requirements and any ambiguities or issues found.
3. Suggestions for possible improvements or changes.
4. A set of proposed User Stories, each with:
    - Title
    - Description
    - Acceptance Criteria
Present your analysis in a clear, organized, and professional manner.

Return a json with 2 keys:
    - "summary", that contains the detailed summary of the code changes in markdown format.
    - "user_stories", that contains a list of user stories derived from the code changes.
Ensure that your response is thorough and provides valuable insights for further development.
"""

code_analysis_template = """
You are a highly skilled Software Architect. Your task is to thoroughly analyze the provided code changes in the context of an Azure DevOps work item. Your goal is to ensure the code aligns with the specified requirements, identify any issues, and suggest actionable improvements.

Provided information:
- **Title:** {title}
- **Description:** {description}
- **Acceptance Criteria:** {acceptance_criteria}
- **Code Changes:** {diff_data}

Your analysis should include:

1. **Detailed Summary:** Provide a comprehensive summary of the code changes in markdown format, highlighting what was modified, added, or removed.
2. **Requirements Alignment:** Assess how well the code changes meet the work item requirements and acceptance criteria. Note any gaps, ambiguities, or misalignments.
3. **Issue Identification:** List any requirements not addressed, ambiguities, defects, or risks found in the code changes.
4. **Quality Analysis:** Evaluate the code for performance, security, maintainability, and scalability concerns. Highlight any potential issues and their impact.
5. **Optimizations:** Suggest specific optimizations or refactoring opportunities to improve code quality and project outcomes.
6. **Improvement Suggestions:** Recommend prioritized improvements or changes, explaining their importance and expected benefits.

**Action Items:**
- Create a prioritized list of new work items for pending tasks, improvements, or defects. Name this list `pending_items`. Each item should follow this format:
    {{
        "title": "Title of the work item",
        "description": "Detailed description of the work item",
        "acceptance_criteria": "List of acceptance criteria items"
    }}

- Create a list of relevant test cases to validate the code changes and requirements. Name this list `test_cases`. Each test case should follow this format:
    {{
        "test_case_id": "ID of the test case",
        "test_case_description": "Detailed description of the test case"
    }}

**Response Format:**  
Return a JSON object with the following keys:
1. `"detailed_analysis"`: The markdown-formatted analysis of the code changes.
2. `"pending_items"`: The list of work items in JSON format.
3. `"test_cases"`: The list of test cases in JSON format.

Ensure your response is clear, well-structured, and provides actionable insights for further development.
"""

project_code_analysis_template = """
You are a highly skilled Software Architect. Your task is to thoroughly analyze the provided code changes in the context of an Azure DevOps work item. Your goal is to ensure the code aligns with the specified requirements, identify any issues, and suggest actionable improvements.

Provided information:
- **Work Items:** {work_items_info}
- **Code Changes:** {commits}

Your analysis should include:

1. **Detailed Summary:** Provide a comprehensive summary of the code changes in markdown format, highlighting what was modified, added, or removed.
2. **Requirements Alignment:** Assess how well the code changes meet the work item requirements and acceptance criteria. Note any gaps, ambiguities, or misalignments.
3. **Issue Identification:** List any requirements not addressed, ambiguities, defects, or risks found in the code changes.
4. **Quality Analysis:** Evaluate the code for performance, security, maintainability, and scalability concerns. Highlight any potential issues and their impact.
5. **Optimizations:** Suggest specific optimizations or refactoring opportunities to improve code quality and project outcomes.
6. **Improvement Suggestions:** Recommend prioritized improvements or changes, explaining their importance and expected benefits.

**Action Items:**
- Create a prioritized list of new work items for pending tasks, improvements, or defects. Name this list `pending_items`. Each item should follow this format:
    {{
        "title": "Title of the work item",
        "description": "Detailed description of the work item",
        "acceptance_criteria": "List of acceptance criteria items"
    }}

- Create a list of relevant test cases to validate the code changes and requirements. Name this list `test_cases`. Each test case should follow this format:
    {{
        "test_case_id": "ID of the test case",
        "test_case_description": "Detailed description of the test case"
    }}

**Response Format:**  
Return a JSON object with the following keys:
1. `"detailed_analysis"`: The markdown-formatted analysis of the code changes.
2. `"pending_items"`: The list of work items in JSON format.
3. `"test_cases"`: The list of test cases in JSON format.

Ensure your response is clear, well-structured, and provides actionable insights for further development.
"""

class Templates ():
    answer_prompt = ChatPromptTemplate.from_template(answer_template)
    initial_transcription_prompt = ChatPromptTemplate.from_template(initial_transcription_template)
    
    def get_initial_transcription(self):
        return self.initial_transcription_prompt

    def get_answer_prompt(self):
        return self.answer_prompt