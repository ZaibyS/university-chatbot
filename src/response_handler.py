"""
This module provides functions to process user queries, generate
responses using a language model (LLM),and trigger fallback 
mechanisms if necessary. It leverages vector search for
schema context retrievaland includes refined prompt generation
when SQL query generation fails.
"""

from langchain_core.messages import SystemMessage, HumanMessage
from src.system_prompt import SYSTEM_PROMPT


def generate_initial_response(user_input, llm, vector_store, k=3):
    """- Generates an initial response from the LLM based on the user's
    input and schema context retrieved from a Chroma vector store.
    - Retrieves relevant schema information using similarity search
    and constructs a response.
    - Returns either an SQL query or an appropriate response message."""
    try:
        results = vector_store.similarity_search(user_input, k=k)
        flattened_context = [item.page_content for item in results]
        context = "\n".join(flattened_context)
        system_message = SystemMessage(
            content=f"{SYSTEM_PROMPT}\nSchema Context:\n{context}"
        )
        human_message = HumanMessage(content=user_input)
        response = llm.invoke([system_message, human_message])
        return response.content.strip()
    except Exception as e:
        print(f"Error generating response: {e}")
        return (
            "An error occurred while processing your request. Please try again later."
        )


def trigger_fallback_logic(user_input, llm, context, human_message):
    """Trigger the fallback logic when the initial response cannot generate a SQL query."""
    try:
        print("Triggering fallback logic")
        SYSTEM_PROMPT_2 = f"""
        You are an assistant tasked with refining natural language queries for better SQL generation.
        **IMPORTANT INSTRUCTIONS:**
        1. **You are strictly bounded NOT to generate or include any SQL queries under any circumstances.**
        2. Your task is to:
        - Explain why the user's original query could not generate a valid SQL query.
        - You are strictly bound to return at least 3 refined natural language prompts that address the issues in the original query.
        3. Your response must strictly contain:
        - A short explanation of why the original query failed.
        - Refined natural language prompts, formatted as bullet points.
        4. **Do NOT explain how to write SQL queries.**
        5. **Do NOT mention SQL query structures, examples, or any SQL-related code in your response.**
        **Here is the user's query that needs refinement:**
        {user_input}
        **Schema Context:**
        {context}
        **Response Format:**
        1. **Why the Query Failed:**
        - [Brief explanation of failure]
        2. **Refined Prompts:**
        - Refined Prompt 1: [First refined query]
        - Refined Prompt 2: [Second refined query]
        - Refined Prompt 3: [Third refined query]
        **Strict Reminder:**
        - You are strictly bound NOT to generate or include SQL queries in your response.
        - You are strictly bound NOT to NOT discuss SQL syntax, query examples, or anything related to SQL query writing.
        - You are strictly bound not to **Suggested SQL Query:**
        - You are strictly bound not to return Improved SQL (based on Refined Prompt)
        """
        refined_system_message = SystemMessage(content=SYSTEM_PROMPT_2)
        refined_response = llm.invoke([refined_system_message, human_message])
        print("Refined Response generated:")
        # print(refined_response.content.strip())
        return refined_response.content.strip()
    except Exception as e:
        print(f"Error triggering fallback logic: {e}")
        return "An error occurred while processing the fallback logic. Please try again later."


def get_response(user_input, llm, vector_store, k=3):
    """Main function to get response and handle fallback logic if needed."""
    try:
        response = generate_initial_response(user_input, llm, vector_store, k)
        if (
            "I cannot generate a SQL query for this request based on the provided schema."
            in response
        ):
            print("Fallback triggered.")
            results = vector_store.similarity_search(user_input, k=k)
            flattened_context = [item.page_content for item in results]
            context = "\n".join(flattened_context)
            return trigger_fallback_logic(
                user_input, llm, context, HumanMessage(content=user_input)
            )
        return response
    except Exception as e:
        print(f"Error in get_response: {e}")
        return (
            "An error occurred while processing your request. Please try again later."
        )
