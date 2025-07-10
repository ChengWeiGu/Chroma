# -*- coding: utf-8 -*-
import openai
from openai import AzureOpenAI, OpenAIError
import time


## default setting
chat_settings = {
    'endpoint':"<your endpoint>",
    'api_key1':"<your api key1>",
    'api_key2':"<your api key2>",
    'region':"eastus",
    'api_version':"<your api version>",
    'chat_model':"<your model name of chatgpt>",
    'api_type':"azure"
}



def chat_completion_openai_history_stream(system_prompt:str="You are a helpful assistant to help user find information",
                                          openai_history_messages:list=[], 
                                          model:str=chat_settings['chat_model']):
    try:
        client = AzureOpenAI(
                            api_key = chat_settings['api_key1'], 
                            api_version = chat_settings['api_version'], 
                            azure_endpoint = chat_settings['endpoint']
                        )
        chat_completion = client.chat.completions.create(
                model=model,
                temperature=0.7,
                max_tokens=2048,
                top_p=0.95,
                frequency_penalty=0,
                presence_penalty=0,
                stop=None,
                messages=[{"role":"system","content":system_prompt}] + openai_history_messages,
                stream=True
            )
        # EOS -> chunk_content is None
        for chunk in chat_completion:
            # print(chunk)
            if chunk.choices != []:
                chunk_content = chunk.choices[0].delta.content
                yield chunk_content
                
        # print(chat_completion)
    except openai.APIError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please retry your request or try another question after a brief wait."
        # print(str(e))
        for word in error_reason:
            yield word
            
    except openai.APITimeoutError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please retry your request after a brief wait."
        for word in error_reason:
            yield word
            
    except openai.RateLimitError as e:
        error_reason = "You have hit your assigned rate limit due to OpenAI's policy. Please retry your request after a brief wait."
        for word in error_reason:
            yield word
            
    except openai.APIConnectionError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please check your network settings, proxy configuration, SSL certificates, or firewall rules."
        for word in error_reason:
            yield word
            
    except openai.AuthenticationError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please check your API key or token and make sure it is correct and active."
        for word in error_reason:
            yield word
            
    except openai.BadRequestError as e:
        error_reason = "Your request was malformed or missing some required parameters, such as a token or an input. Please try another question."
        for word in error_reason:
            yield word
            
    except openai.ConflictError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please try to update the resource again and ensure no other requests are trying to update it."
        for word in error_reason:
            yield word
            
    except openai.InternalServerError as e:
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please Retry your request after a brief wait."
        for word in error_reason:
            yield word
            
    except openai.NotFoundError as e:
        error_reason = "Requested resource does not exist. Please ensure you are the correct resource identifier."
        for word in error_reason:
            yield word
            
    except openai.PermissionDeniedError as e:
        error_reason = "You don't have access to the requested resource. Please ensure you are using the correct API key, organization ID, and resource ID."
        for word in error_reason:
            yield word
            
    except openai.UnprocessableEntityError as e:
        error_reason = "Unable to process the request despite the format being correct. Please try the request again."
        for word in error_reason:
            yield word
            
    except OpenAIError as e:
        # error_reason = f"[OPENAI ERROR]{str(e)}"
        error_reason = "I'm sorry, I cannot answer your question due to OpenAI's policy. Please try another question."
        for word in error_reason:
            yield word
            
    except Exception as e:
        # error_reason = f"[OPENAI ERROR]{str(e)}"
        error_reason = "I'm sorry, I cannot answer your question. Please try again."
        for word in error_reason:
            yield word
            

    
class SummaryAgent:
    
    def __init__(self):
        self.system_prompt = "You are a helpful assistant to help user find information"
    
    def generate_structure_prompt(self, query, working_context):
        return f"""
                [ROLE]
                You are an AI assistant working for Weintek, a leading HMI equipment manufacturer. Your task is to efficiently and professionally sort and respond to customer service inquiries about Weintek's products, software, hardware, and firmware.

                [Task Description]
                1. The information in [Retrieval Knowledge] are your only source of truth. Only answer the question with the provided context.
                2. Carefully analyze the customer's inquiry by following [Thinking Steps].

                [New Inquiry]
                A customer has submitted the following question:
                "{query}"
                
                [Retrieval Knowledge]
                {working_context}
                
                [Thinking Steps]
                Step 1: To make you better understand some professional terminology and words before thinkings, please refer to the following explanation:
                    a. CODESYS has other expressions such as codesys、Codesys、CoDeSys, 3S CoDeSys or CODESYS® (Optional).
                    b. Basic model has other expression such as `cMT X Basic Series`
                    c. Standard model has other expression such as `cMT X Standard Series`
                    e. Advance model has other expression such as `cMT X Advanced Series`
                    f. Headless model has other expression such as `cMT X Headless Series`
                    g. G series are the short term of `Gateway Series`
                    h. EA2.0 is the short term of `EasyAccess 2.0`
                    i. HW Key is the short term of `Hardware Key`
                    j. EBPro or EB means `EasyBuilder Pro`

                Step 2: Categorize User's Question
                    - Objective: Classify the nature of the user's inquiry.
                    - Categories:
                        a. Class 1: Questions un-related to Weintek's products, software, or hardware issues.
                        b. Class 2: Questions related to Weintek's products, software, or hardware issues.
                
                Step 3: Decide on Response Strategy
                    - Objective: Determine whether to proceed with answering or to inform of inability to assist.
                    - Decision Process:
                        a. If Step 2 results in "Class 1", please reply with
                            "Unfortunately, I don't have specific details about [product/feature/action/task/service]. You may want to contact Sales (Email: salesmail@weintek.com) for more information." or
                            "I'm sorry, but I can't assist with that. If you need help with a specific Weintek product or service, please let me know!"
                            Then, stop to think the next step.
                        b. If Step 2 results in "Class 2", then proceed to think the next step.
                
                Step 4: Write down your answer and summary to the user's question and use the rules below: 
                    a. In your summary, please shorten your reply and provide the key point of your solution.
                    b. In your summary, if instruction includes manipulation of sub pages, please guide user how to click on [tabs].
                    c. Do not show any thinking step in your reply. Make your response precise and accurate.
                    d. For manipulation and operation issues, please provide clear instructions with bullet points.
                    e. For region-specific model or produced by Weinview, please advise user to contact their supplier or sales for help.                
                
                [Output format]
                Please structure your response as follows:
                <step 4 result in English>
                
                [Important Notes]
                • Maintain a professional and helpful tone throughout your response.
                • Do not provide any external information or assumptions. Only answer the question with the provided context in [Retrieval Knowledge]. if answer cannot be found, please reply with
                "I'm sorry. I don't have exact information about <user requirement>. You may want to contact salesmail@weintek.com for more information."
                • Sometimes remind user of providing any feedback for us so that we can improve our responses.
                • Do not provide any invalid reference.
                """
    
    def generate_answer(self, query, working_context):
        prompt = self.generate_structure_prompt(query, working_context)
        # define messages
        openai_history_messages = [{
                                    "role":"user",
                                    "content": [{
                                            "type":"text",
                                            "text": prompt
                                            }]
                                }]
        
        # call openai func
        for chunk in chat_completion_openai_history_stream(
                            system_prompt=self.system_prompt, 
                            openai_history_messages=openai_history_messages
                            ):
            yield chunk