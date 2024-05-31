import openai

from keys import OPENAI_KEY


def send_prompt(prompt_message, max_response_tokens=3000):
    """
    Sends a prompt to OpenAI's GPT model and returns the response.

    Args:
        prompt_message (str): The message to send to the model.
        max_response_tokens (int): The maximum number of tokens to generate.
    
    Returns:
        str: The response message from the model.
    """
    openai.api_key = OPENAI_KEY

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a Python and Vision AI developer."},
            {"role": "user", "content": prompt_message},
        ],
        max_tokens=max_response_tokens,
    )

    return response["choices"][0]["message"]["content"]


if __name__ == "__main__":
    response_message = send_prompt(
        "Explain unit testing in Python. Tell all you know please"
    )
    print(response_message)
