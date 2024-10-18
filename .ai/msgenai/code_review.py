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
print("pull_request_url=", pull_request_url);
pull_request_number = pull_request_url.split('/')[-2]
print("pull_request_number=", pull_request_number)
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
    coding_standards = load_prompts('.ai/msgenai/ai/common_coding_standards.txt')
    custom_rule_prompt = "\n".join(prompts)
    common_coding_standards = "\n".join(coding_standards)

    # Combine the default review instruction with the custom rules
    prompt = (
        "Please review the following code for adherence to openAI's coding review and the specific custom rules outlined below.\n\n"
        "Common Coding Standards:\n"
        f"{common_coding_standards}\n\n"
        "Custom Rules:\n"
        f"{custom_rule_prompt}\n\n"
        "Code:\n"
        f"{content}\n\n"
        "Review Instructions:\n"
        "- Evaluate the code for both common coding standards and custom rules.\n"
        "- Report only on violations and avoid mentioning the absence of functions, variables, or classes unless it is directly relevant to a rule.\n"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    comment = ""  # Initialize the comment variable
    for chunk in response:
        print("Chunk received:", chunk)  # Debug line
        delta_content = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
        if delta_content:
            print("comment=", delta_content)
            comment += delta_content
        else:
            print("No content in chunk")
    if comment:
        pr.create_issue_comment(comment)
def main(diff):
    for file in diff:
        if file.filename.endswith('.js'):
            # Get the content of the file
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
            print("content=", content)
            get_streamed_completion(content)

# Run the main function
main(diff)
