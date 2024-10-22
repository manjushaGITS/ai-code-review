import asyncio
import os
from openai import OpenAI
from github import Github

# Get the GitHub and OpenAI API Keys from environment
github_token = os.getenv('GITHUB_TOKEN')
openai_api_key = os.getenv("OPENAI_API_KEY")

#Initialize the GitHub and OpenAI clients
github = Github(github_token)
client = OpenAI(api_key=openai_api_key)

#Get the repository and PR from the GitHub API
repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))

pull_request_url = os.getenv('GITHUB_REF')
pull_request_number = pull_request_url.split('/')[-2]
if pull_request_url:
    try:
        pull_request_number = int(pull_request_number)
        if pull_request_number:
            pr = repo.get_pull(pull_request_number)
    except ValueError:
        # Handle invalid URL format or extract manually
        pass
else:
    # Handle case where pull request URL is not available
    pass

# Get the differences in the PR
diff = pr.get_files()

def load_prompts(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def get_streamed_completion(content):
    prompts = load_prompts('.ai/msgenai/ai/rule1.txt')  # Load prompts from the file
    a11y_standards = load_prompts('.ai/msgenai/ai/accessibility.txt')
    custom_elements_standards = load_prompts('.ai/msgenai/ai/custom_elements.txt')
    
    custom_rule_prompt = "\n".join(prompts)
    a11y_prompt = "\n".join(a11y_standards)
    custom_elements_prompt = "\n".join(custom_elements_standards)

    # Combine the default review instruction with the custom rules
    prompt = (
        "Please do the review:\n"
        "A11Y Rules:\n"
        f"{a11y_prompt}\n\n"
        "Custom Element Rules:\n"
        f"{custom_elements_prompt}\n\n"
        "Custom Rules:\n"
        f"{custom_rule_prompt}\n\n"
        "Code:\n"
        f"{content}\n\n"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )
    response1 = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        stream=True,
    )

    comment = ""  # Initialize the comment variable
    for chunk in response:
        delta_content = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
        if delta_content:
            comment += delta_content
        else:
            print("No content in chunk")
    for chunk1 in response1:
        delta1_content = chunk1.choices[0].delta.content if chunk1.choices and chunk1.choices[0].delta else None
        if delta1_content:
            comment1 += delta1_content
        else:
            print("No content in chunk")
    if comment or comment1:
        pr.create_issue_comment(comment+comment1)
def main(diff):
    for file in diff:
        if file.filename.endswith('.js'):
            # Get the content of the file
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
            print("content=", content)
            get_streamed_completion(content)

# Run the main function
main(diff)
