import numpy as np
import os
import openai

class LLMAgent(object):
    
    def __init__(self):
        self.llm = None
        self.key = None
        self.model = None


    def create_llama_agent(self):
        self.llm = "llama"

    def create_openai_agent(self):
        self.llm = "openai"
        # PLEASE CHANGE THIS KEY FOR TESTING SINCE ITS USING FUNDS OF MY ACCOUNT !!!!!!!!!!!!!!!!!!!
        self.key = "<YOUR API KEY>" 
        self.model = "gpt-3.5-turbo"  # DO NOT CHANGE THIS!
        openai.api_key = self.key
    
    def send_message(self, messages, max_tokens=100, temperature=0):
        """Communicate with the agent and get a response."""
        if self.llm == "openai":
            response = openai.ChatCompletion.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            return response.choices[0].message['content'].strip()
        elif self.llm == "llama":
            # Logic for Llama-based communication (if applicable)
            pass
        else:
            raise ValueError("Invalid agent type.")

article = """With house prices soaring, it's not easy finding 
somewhere to live. And this community has thrown in the towel.
Meet Seattle's rolling neighborhood of RVs, where each unassuming 
vehicle is a capsule home. The unusual format has been captured in a 
series of photographs by visual journalist Anna Erickson. Meet Bud Dodson,
57, and welcome to his home: An RV in Seattle's SoDo where he watches over
the parking lot in exchange for a spot . No place like home: John Warden, 52, has
turned his $200 vehicle into his home after his apartment burned down years ago .
There are around 30 drivers that float in and out of this parking lot in the SoDo (South of Downtown)
area of the city in Washington State. One might not notice them in the mornings as hundreds of workers 
in the nearby factories, such as Starbucks, park up and rush into work. But on the weekends, as the 
rabble flocks back to their beds, this unique group remains. John Worden, 52, has been living in
his vehicle for years since his apartment burned down and he was left homeless. He told Anna
his car cost $200, and doesn't drive very well. But for a home, it's just about enough. 
Though plan on the outside, it is a Pandora's Box inside, Anna tells DailyMail.com. 
'It was scattered with trinkets that he had been collecting over the years,' she explained,
'and a pile of beer cans that he was saving to turn in for money.' For work, he panhandles 
while helping people find parking spaces at Safeco Field stadium, where he used to be a cook.
People come and go for work in the factories nearby, but on the weekend it is just
the RV-dwellers that area left . Daily life: Here Bud can be seen preparing himself
a barbecue on the gravel outside his capsule home, one of about 30 in the community .
Eclectic: While Bud's RV is organized and functional, John's is full of trinkets and
belongings dating back years . Alongside him - most of the time - is Bud Dodson, 57
. While some are forced to move about regularly, Dodson, a maintenance man,
looks after the parking lot in exchange for a semi-permanent spot. His home has
its own unique stamp on it. 'He had really made the RV his home and taken good
care of it,' Anna described. 'It was more functional [than John's] and a 
cleaner space with a bed, kitchen and bathroom.' Whether organized or eclectic,
however, each one is home. 'None of them seem to want to move on,' Anna said. 
'It's not perfect but they seem pretty content. Move in, move out: Some have 
agreements to stay, but others have to keep driving around to find a spot . 
John works as a panhandler at Safeco Fields stadium, where he used to work as 
a cook . He is content with his life in between the usual confines of society 
. Personal: To many this may just seem like a parking lot but for these men it
is a very personal space . 'Bud is very grateful, he said the parking lot owner
is just such a nice guy to let him live like this.' She came across them when 
she stopped to ask a seemingly homeless man for directions. 'We got talking,' 
she said, 'and he mentioned that he lived nearby in an RV. I went round to look 
and there was a whole bunch of them.' Curious, she spent about two months returning 
to the spot, meeting with the community and building their trust. 'These RVs are their homes 
so it's a very personal thing,' she explained."""

agent = LLMAgent()
agent.create_openai_agent()

def base_summary(text):
    """Generate an initial entity-sparse summary of the given text."""
    messages = [
        {"role": "user", "content": f"Please provide a concise summary for the following text with minimal entity details: {text}"}
    ]
    return agent.send_message(messages)

def extract_entities(text):
    """Extract and rank entities from the given text, utilizing enhanced prompting techniques."""
    
    # Part 1: Explicitly defining "entity" in the prompt
    prompt = (f"Identify and rank the entities, such as names of people, places, organizations, "
              f"dates, or other specific details, from the following text: {text}")
    response_text = agent.send_message([{"role": "system", "content": "You are a helpful assistant."},
                                        {"role": "user", "content": prompt}], 
                                       max_tokens=150)
    initial_entities = response_text.split(',')
    
    # Part 2: Iterative extraction
    refined_entities = []
    for entity in initial_entities:
        entity = entity.strip()  # Clean up the extracted entity
        
        # Validate the entity with another prompt
        validation_prompt = f"Provide a reason why '{entity}' is considered a significant entity in the text."
        validation = agent.send_message([{"role": "user", "content": validation_prompt}], 
                                        max_tokens=50)
        
        # Store the entity and its validation
        refined_entities.append((entity, validation))

    return refined_entities  # Return a list of tuples containing entities and their validations


def llm_dense_summary(summary, entities, target_length):
    """Generate a denser summary using GPT-3.5 with abstraction and fusion techniques."""
    entities_str = ', '.join([e[0] for e in entities])
    
    # Updated prompt to incorporate abstraction and fusion techniques
    prompt = (f"Given the summary: '{summary}', and important entities: {entities_str}, "
              f"please rephrase and distill the content focusing on core ideas (abstraction), "
              f"and combine related pieces of information into unified statements (fusion). "
              f"Produce a denser summary without exceeding {target_length} characters.")
    
    response_text = agent.send_message([{"role": "user", "content": prompt}],
                                       max_tokens=target_length)
    
    return response_text


def increase_density(summary, entities, target_length):
    # Get a denser summary using the helper function
    denser_summary = llm_dense_summary(summary, entities, target_length)
    
    return denser_summary

def evaluate_summaries(summaries):
    """Compare the given summaries and evaluate based on entity density and a proposed alternative method."""
    evaluations = {}
    
    for idx, summary in enumerate(summaries):
        # Count the number of entities using the extract_entities function
        entities = [entry[0] for entry in extract_entities(summary)]  # Extract only entity names, not validations
        entity_count = len(entities)
        
        evaluations[f'Summary_{idx + 1}'] = {
            'Entity Count': entity_count,
            'Entities': entities
        }
        
    return evaluations


if __name__ == "__main__":
    initial_summary = base_summary(article)
    entities = extract_entities(article)
    
    # Iteratively call the increase_density function three times
    denser_summary_1 = increase_density(initial_summary, entities, len(initial_summary))
    denser_summary_2 = increase_density(denser_summary_1, entities, len(initial_summary))
    final_summary = increase_density(denser_summary_2, entities, len(initial_summary))
    summaries = [initial_summary, final_summary]
    results = evaluate_summaries(summaries)
    print("Initial Summary: ", initial_summary)
    print("Final Summary: ", final_summary)
    print("------")
    print("Results", results)

