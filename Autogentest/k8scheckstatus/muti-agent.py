import os
from autogen import ConversableAgent
from dotenv import load_dotenv
from toolcal import podscheck, nodescheck
from autogen import GroupChatManager
from autogen import GroupChat
from autogen import register_function

llm_config={"config_list": [{"model": "gpt-4-turbo", "temperature": 0.7,"api_key": os.environ["OPENAI_API_KEY"],"base_url": os.environ["OPENAI_API_BASE"]}]}

code_writer_agent= ConversableAgent(
    name="Code_Writer_Agent",
    system_message="You are a helpful AI assistant. Solve tasks using your coding and language skills. In the following cases, suggest python code (in a python coding block) or shell script (in a sh coding block) for the user to execute. 1. When you need to collect info, use the code to output the info you need, for example, browse or search the web, download/read a file, print the content of a webpage or a file, get the current date/time, check the operating system. After sufficient info is printed and the task is ready to be solved based on your language skill, you can solve the task by yourself. 2. When you need to perform some task with code, use the code to perform the task and output the result. Finish the task smartly. Solve the task step by step if you need to. If a plan is not provided, explain your plan first. Be clear which step uses code, and which step uses your language skill. When using code, you must indicate the script type in the code block. The user cannot provide any other feedback or perform any other action beyond executing the code you suggest. The user can't modify your code. So do not suggest incomplete code which requires users to modify. Don't use a code block if it's not intended to be executed by the user. If you want the user to save the code in a file before executing it, put # filename: <filename> inside the code block as the first line. Don't include multiple code blocks in one response. Do not ask users to copy and paste the result. Instead, use 'print' function for the output when relevant. Check the execution result returned by the user. If the result indicates there is an error, fix the error and output the code again. Suggest the full code instead of partial code or code changes. If the error can't be fixed or if the task is not solved even after the code is executed successfully, analyze the problem, revisit your assumption, collect additional info you need, and think of a different approach to try. When you find an answer, verify the answer carefully. Include verifiable evidence in your response if possible. Reply 'TERMINATE' in the end when everything is done.",
    llm_config=llm_config,
)

k8s_podcheck_agent = ConversableAgent(
    name="K8s_podcheck_agent",
    system_message="You can check the pod status of k8s pod here."
    "Call podscheck() to get list of pod status. ",
    llm_config=llm_config,
)

k8s_nodecheck_agent = ConversableAgent(
    name="K8s_nodecheck_agent",
    system_message="You can check the node status of k8s pod here."
    "Call nodescheck() to get list of node status. ",
    llm_config=llm_config,
)

# Register the calculator function to the two agents.
register_function(
    podscheck,
    caller=k8s_podcheck_agent,  # The assistant agent can suggest calls to the calculator.
    executor=code_writer_agent,  # The user proxy agent can execute the calculator calls.
    name="k8s_podcheck_agentr",  # By default, the function name is used as the tool name.
    description="A pod status check tool",  # A description of the tool.
)

register_function(
    nodescheck,
    caller=k8s_nodecheck_agent,  # The assistant agent can suggest calls to the calculator.
    executor=code_writer_agent,  # The user proxy agent can execute the calculator calls.
    name="k8s_nodecheck_agentr",  # By default, the function name is used as the tool name.
    description="A node status check tool",  # A description of the tool.
)


group_chat = GroupChat(
    agents=[k8s_podcheck_agent, k8s_nodecheck_agent,code_writer_agent],
    messages=[],
    max_round=6,
)
group_chat_manager = GroupChatManager(
    groupchat=group_chat,
    llm_config=llm_config,
)
chat_result = code_writer_agent.initiate_chat(
    group_chat_manager,
    message="Check node status in k8s.",
    summary_method="reflection_with_llm",
)

# nested_chats = [
#     # {
#     #     "recipient": group_chat_manager_with_intros,
#     #     "summary_method": "reflection_with_llm",
#     #     "summary_prompt": "Summarize the sequence of operations used to turn " "the source number into target number.",
#     # },

#     {
#         "recipient": k8s_podcheck_agent,
#         "message": "check k8s pod status.",
#         "summary_method": "reflection_with_llm",
#     },
#     {
#         "recipient": k8s_nodecheck_agent,
#         "message": "check k8s node status.",
#         "max_turns": 1,
#         "summary_method": "last_msg",
#     },
# ]

# code_writer_agent.register_nested_chats(
#     nested_chats,
#     # The trigger function is used to determine if the agent should start the nested chat
#     # given the sender agent.
#     # In this case, the arithmetic agent will not start the nested chats if the sender is
#     # from the nested chats' recipient to avoid recursive calls.
#     trigger=lambda sender: sender not in [k8s_nodecheck_agent,k8s_podcheck_agent],
# )

# reply = code_writer_agent.generate_reply(
#     messages=[{"role": "user", "content": "help me check pods and node status ."}]
# )

