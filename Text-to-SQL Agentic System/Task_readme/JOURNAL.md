This md file contains the difficulties faced during all task completion and the learning.

# Task 2

- created parser in parse_schema to prase the schema of seed.sql.
- then the parsed schema is used to generate the decomposition in query_decompositions.py.
- The questions is taken from sql_questions.csv and passed into the system prompt to generate the decompositiom from the parsed schema. 
- The results are appended into the query_decompositions.json file.
- The previously parsed questions will be skipped. This makes it quicker and easier if later we added more question on the sql_questions.csv file. Instead if we want to run it again we can use (Cache Reset) --force to make it run from the start without skipping. 


**Issues**
- Name error Grok vs Groq. I had groq api and setup but mistakenly during agents prompt included grok which led to model incompatality. Then, Fixed it with correct name and the dependencies. As a result, with grok my query_decomposition wasn't able to operate or it provided none as a results in tabels.. (can see in first two). Then with the correct setup the model worked and it provided with the correct decomposition for the rest of the 48 questions. 


**Lesson learned**
- Always double check your api key and model name.  
- Make your code resuable. Only .env and loading part needed to be changed rest were intact.

# Task 3

 `**Tasks Completed:**`
> 1. Build on top of Task 2 following query decomposition.
> 2. Generated sql queries. 
> 3. Ran the generated sql queries on the postgresql database in docker. 
> 4. Since some of the query output have large number of rows, only the first 10 rows are displayed and other are displayed as total row count.
> 5. The query generated after the query decomposition for all the questions are saved in json format, by looking at which we can identify if the query generated matches with the question and decomposition or not (manually).
> 6. Created a streamlit app running on port 8501.
>
> SQL Generation and sql execution are placed in logs. This makes easier to debug.

`**Findings/Test in app:**`

> 7. The app asks for user custom query or build in query (listed from the questions). 
> 8. It shows the first 10 rows of the output and total row count if there are more than 10 rows.
> 9. On right side we can see the step by step decomposition as well as sql query generated for that particular question.
> 10. Currently if tried to other than select, such as delete (it ignores the delete and only does the select part) doesnt throw an error. [Future Improvement]
> 11. If send (such as shit, or ) database unrelated query, it shows unknown on decomposition and instead of error or crashing, it displayes data records of our database (showing the list of table names).
> 12. all the operations, joins works correctly (As it has prebuild all 50 questions listed can check indivisually in the app).
> 13. Input "S10_1678 update this product with product line as "abcd"" resulted into "SELECT "productLine" FROM products WHERE "productCode" = 'S10_1678'". It takes delete, update, edit etc as select and shows that data. 

# Task 4

 `Tasks Completed:`
> 1. Developed a RESTful FastAPI endpoint: `POST /agent/sql` housed in `fastapi_agent.py`.
> 2. Structured a **Relevance Guardrail** using a LLM intent classifier to block database-unrelated inputs and supply custom hints based on the active table list.
> 3. Hardened a **Safety Guardrail** to enforce `SELECT`-only execution. Mutating commands (`DELETE`, `UPDATE`, `DROP`, etc.) are caught and blocked at both the natural language interface and raw SQL generation levels.
> 4. Formatted the output exactly as requested, supporting raw numerical counts for simple aggregate queries and JSON arrays for records.
> 5. Created a **Dynamic Summarizer** prompting Groq to translate the returned raw rows into a beautiful, human-sounding sentence (`"summary"` key).
> 6. Enabled **Enhanced Self-Correction Retries** allowing the query execution logic to retry up to a maximum of 3 times in the event of database syntax/ambiguity failures, with real-time logging of timings, decomposition stages, and SQL generation runs.
> 7. Added `api` service mapping to port `8000:8000` inside `docker-compose.yml` to start FastAPI in the same bridge network as Streamlit and PostgreSQL.
> 8. Created and executed a complete integration test suite in `test_fastapi_agent.py` proving 100% success across valid, safety-blocked, relevance-blocked, and self-corrected queries.

`Test Cases/Summary`
> Tested in /docs/agent/sql
> 1. Ran the delte customers table, and resulted cannot perform this operation. (Correctly Blocked, in task 3 it used to show the selete results ignoring delete/..).
> 2. Ran something else than sql query, it showed unknown and resulted couldn't perform this operations.
> 3. All the list / select reultes are correct. 
> 4. Join queries in natural language are understanable and workes fine. 
> 5. At last shows the summary regarding the query and the output in human readable format. 