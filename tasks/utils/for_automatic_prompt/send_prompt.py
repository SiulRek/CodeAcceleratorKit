from openai import OpenAI

try:
    from keys import OPENAI_KEY
except ModuleNotFoundError:
    OPENAI_KEY = None

def send_prompt(prompt_message, max_response_tokens=3000, model="gpt-4o"):
    """
    Sends a prompt to OpenAI's GPT model and returns the response.

    Args:
        - prompt_message (str): The message to send to the model.
        - max_response_tokens (int): The maximum number of tokens to
            generate.

    Returns:
        - str: The response message from the model.
    """
    if OPENAI_KEY is None:
        raise ValueError("OPENAI_KEY is not set. Please set it in keys.py.")
    
    client = OpenAI(api_key=OPENAI_KEY)

    response = client.chat.completions.with_raw_response.create(
        messages=[
            {"role": "system", "content": "You are a Python developer."},
            {"role": "user", "content": prompt_message},
        ],
        model=model,
        max_tokens=max_response_tokens,
    )


    completion = response.parse()
    response_message = completion.choices[0].message.content
    return response_message


if __name__ == "__main__":
    response_message = send_prompt(
        "Explain unit testing in Python. Tell all you know please",
        max_response_tokens=10,
    )
    print(response_message)