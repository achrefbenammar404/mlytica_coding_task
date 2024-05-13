# MLytica coding task

## Task
Building a Chatbot with FastAPI Endpoints

### Requirements:
1. You will be provided with a text file named competition_results.txt.
2. Your goal is to create a chatbot powered by Language Models (LLMs).
3. The chatbot should take the user's question and decide which of the two endpoints to call based on the input.

### Endpoints:
#### Endpoint1:
- Input: "1st place", "2nd place", "3rd place"
- Output: Corresponding department

#### Endpoint2:
- Input: "1st place", "2nd place", "3rd place"
- Output: Corresponding employee

### Requirements for Endpoints:
- The endpoints should be flexible enough to handle any changes in the competition results text file, which may vary each month.
- Dockerize your solution to ensure portability and easy deployment.

### Implementation Details:
- Create two separate FastAPI instances: one for the endpoints and one for the chatbot.
- You can use OpenAI directly or choose a framework like LangChain to implement the chatbot functionality.
- Showcase your coding skills, problem-solving abilities, and knowledge of different types of agents.
- We would like to see you use an agentic method.

### Dockerization:
- Package your solution into Docker containers to ensure easy deployment and scalability.
- Provide clear instructions on how to run the Docker containers.

### Note:
Ensure that your solution is scalable and adaptable to dynamic changes in the competition results. The provided text file may contain different data each month, and your endpoints should be capable of reading any competition results text file and returning the appropriate values. 

Please do what you can and send us whatever you could manage.