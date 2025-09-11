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

Here is the work item history:
{history_json}
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

Here is the work items history:
{history_json}
"""

class Templates ():
    answer_prompt = ChatPromptTemplate.from_template(answer_template)
    initial_transcription_prompt = ChatPromptTemplate.from_template(initial_transcription_template)
    
    def get_initial_transcription(self):
        return self.initial_transcription_prompt

    def get_answer_prompt(self):
        return self.answer_prompt