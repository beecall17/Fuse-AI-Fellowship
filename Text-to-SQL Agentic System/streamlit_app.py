import os
import json
import streamlit as st
import pandas as pd
from query_decomposition import parse_schema
from sql_pipeline import run_full_pipeline, execute_query, is_query_safe, get_db_connection

# Page Configuration
st.set_page_config(
    page_title="AI Text-to-SQL Agentic System",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom premium styling via Streamlit Markdown
st.markdown("""
<style>
    .main-title {
        font-size: 2.8rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00C6FF, #0072FF);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #7F8C8D;
        margin-bottom: 2rem;
    }
    .panel-header {
        font-size: 1.4rem;
        font-weight: 700;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #F8F9F9;
        border: 1px solid #E5E7E9;
        border-radius: 8px;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .stAlert {
        border-radius: 8px;
    }
</style>
""", unsafe_allow_html=True)

# Resolve paths
base_dir = os.path.dirname(os.path.abspath(__file__))
sql_path = os.path.join(base_dir, "Scripts", "seed.sql")
if not os.path.exists(sql_path):
    sql_path = os.path.join(base_dir, "scripts", "seed.sql")
    
questions_path = os.path.join(base_dir, "Scripts", "sql_questions.csv")
if not os.path.exists(questions_path):
    questions_path = os.path.join(base_dir, "scripts", "sql_questions.csv")

# Load Schema Context
@st.cache_resource
def load_db_schema():
    try:
        schema = parse_schema(sql_path)
        schema_desc_lines = []
        for table, cols in schema.items():
            schema_desc_lines.append(f"Table '{table}': {', '.join(cols)}")
        return schema, "\n".join(schema_desc_lines)
    except Exception as e:
        st.error(f"Error loading database schema: {e}")
        return {}, ""

schema, schema_desc = load_db_schema()

# Load Sample Questions
@st.cache_data
def load_sample_questions():
    questions = []
    if os.path.exists(questions_path):
        import csv
        try:
            with open(questions_path, 'r', encoding='utf-8-sig') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    if 'question' in row and row['question'].strip():
                        questions.append(row['question'].strip())
        except Exception:
            pass
    # Fallbacks if file not loaded
    if not questions:
        questions = [
            "List all products",
            "Show all orders placed by customers in Germany",
            "Get employees and their manager",
            "Count customers per country",
            "Total payments per customer"
        ]
    return questions

sample_questions = load_sample_questions()

# SIDEBAR: Database Schema Catalog
with st.sidebar:
    st.image("https://img.icons8.com/clouds/200/database.png", width=100)
    st.markdown("### 📊 Database Catalog")
    st.markdown("This system runs against a simulated **ClassicModels** database schema containing **8 relational tables**:")
    
    for table_name, columns in schema.items():
        with st.expander(f"📁 {table_name}"):
            st.markdown(f"**Columns ({len(columns)}):**")
            for col in columns:
                # Highlight primary / foreign keys if matched
                if col in ["productLine", "productCode", "officeCode", "employeeNumber", "customerNumber", "checkNumber", "orderNumber"]:
                    st.markdown(f"- `🔑 {col}`")
                else:
                    st.markdown(f"- `{col}`")

# MAIN BODY
st.markdown('<div class="main-title">🤖 AI Text-to-SQL Agentic System</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Natural Language DB Interface with Case-Insensitive Groq Reasoning and Self-Correction.</div>', unsafe_allow_html=True)

# Question Input Section
st.markdown("### ✍️ Enter Your Natural Language Question")
col_sel, col_btn = st.columns([6, 1])

with col_sel:
    # Option to select example or write custom
    use_custom = st.checkbox("Write a custom query instead of standard list", value=False)
    if use_custom:
        user_question = st.text_input(
            label="Custom Question",
            value="Show all customers in the USA with a credit limit over 100000",
            placeholder="Type your question here...",
            label_visibility="collapsed"
        )
    else:
        user_question = st.selectbox(
            label="Sample Questions",
            options=sample_questions,
            label_visibility="collapsed"
        )

with col_btn:
    st.markdown("<div style='height: 4px;'></div>", unsafe_allow_html=True)
    run_btn = st.button("🚀 Run Pipeline", use_container_width=True)

st.markdown("---")

# Main Content Layout: 2 Columns
left_col, right_col = st.columns([5, 4])

if run_btn or 'active_question' in st.session_state:
    if run_btn:
        st.session_state.active_question = user_question
        with st.spinner("Executing Text-to-SQL pipeline phases..."):
            # Execute pipeline
            # Retrieve cached decomposition if standard and exists to save time, else dynamic
            decomposition = {}
            # If standard query, let's see if we can find it in query_decompositions.json
            decomp_path = os.path.join(base_dir, "Scripts", "query_decompositions.json")
            if os.path.exists(decomp_path) and not use_custom:
                try:
                    with open(decomp_path, 'r', encoding='utf-8') as f:
                        decomps = json.load(f)
                        for d in decomps:
                            if d.get("question") == user_question:
                                decomposition = d
                                break
                except Exception:
                    pass
            
            # Execute the coordinated pipeline
            pipeline_output = run_full_pipeline(user_question, decomposition, schema_desc)
            st.session_state.pipeline_output = pipeline_output

    output = st.session_state.pipeline_output
    
    # ================= LEFT COLUMN: RESULTS & EXECUTION =================
    with left_col:
        st.markdown('<div class="panel-header">🎯 Execution Output</div>', unsafe_allow_html=True)
        
        # Success/Failure Status
        if output["status"] == "success":
            st.success("✅ Query Executed Successfully!")
        else:
            error_msg = output.get("error", "Unknown execution error")
            st.error(f"❌ Execution Failure: {error_msg}")
            
        # Generated SQL Code Box
        st.markdown("#### 📝 Generated SQL Query")
        if output["sql"]:
            st.code(output["sql"], language="sql")
        else:
            st.warning("No SQL query could be generated.")
            
        # Execution Results Dataframe
        st.markdown("#### 📋 Data Records")
        if output["status"] == "success":
            results = output["result"]
            total_rows = output["total_row_count"]
            
            if results:
                df = pd.DataFrame(results)
                # Re-index starting from 1 for premium presentation
                df.index = df.index + 1
                
                # Show dataframe
                st.dataframe(df, use_container_width=True)
                
                # Show Total Row Count details
                st.markdown(
                    f"<div class='metric-card'>🤖 <b>Total Rows in DB:</b> {total_rows} "
                    f"| <i>(Displaying first {len(results)} rows)</i></div>",
                    unsafe_allow_html=True
                )
            else:
                st.info("Query successfully returned 0 records.")
        else:
            st.info("No records to display due to query execution error.")

    # ================= RIGHT COLUMN: REASONING & PIPELINE LOGS =================
    with right_col:
        st.markdown('<div class="panel-header">🧠 Pipeline Reasoning & Logs</div>', unsafe_allow_html=True)
        
        # Dynamic Decomposition
        st.markdown("#### 1️⃣ Structured Decomposition (Prompt 1)")
        decomp = output["decompose"]
        if decomp and decomp.get("Intent") != "Error decomposing question":
            st.markdown(f"**Intent:** `{decomp.get('Intent')}`")
            
            # Tables Involved
            tables = decomp.get("Tables")
            if isinstance(tables, list):
                st.markdown(f"**Tables:** `{', '.join(tables)}`")
            else:
                st.markdown(f"**Tables:** `{tables}`")
                
            # Columns Needed
            columns = decomp.get("Columns")
            if isinstance(columns, list):
                st.markdown(f"**Columns:** `{', '.join(columns)}`")
            else:
                st.markdown(f"**Columns:** `{columns}`")
                
            # Filters
            st.markdown(f"**Filters:** `{decomp.get('Filters')}`")
            # Joins
            st.markdown(f"**Joins:** `{decomp.get('Joins')}`")
        else:
            st.warning("Decomposition parsing returned invalid components.")
            
        st.markdown("---")
        
        # Safety Validator Status
        st.markdown("#### 2️⃣ Safety Validator")
        if output["sql"]:
            is_safe, reason = is_query_safe(output["sql"])
            if is_safe:
                st.markdown("🟩 **Safety Status:** `PASSED` (Only SELECT actions detected)")
            else:
                st.markdown(f"🟥 **Safety Status:** `FAILED` ({reason})")
        else:
            st.markdown("⬜ **Safety Status:** `N/A`")
            
        st.markdown("---")
        
        # Generation and Debug logs
        st.markdown("#### 3️⃣ Pipeline Logs")
        
        # Read latest lines from generation and execution logs
        log_content = []
        if os.path.exists("logs/sql_generation.log"):
            with open("logs/sql_generation.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Fetch last 4 lines containing our active question
                active_lines = [line.strip() for line in lines if user_question[:15] in line or "decomposed" in line or "Generated SQL" in line or "Self-Corrected" in line][-4:]
                log_content.extend(active_lines)
                
        if os.path.exists("logs/sql_execution.log"):
            with open("logs/sql_execution.log", "r", encoding="utf-8") as f:
                lines = f.readlines()
                # Fetch last 3 execution lines
                active_lines = [line.strip() for line in lines if "Attempting" in line or "Successful" in line or "Failed" in line][-3:]
                log_content.extend(active_lines)
                
        if log_content:
            st.text_area(
                label="Console Log Snippets",
                value="\n".join(log_content),
                height=150,
                disabled=True,
                label_visibility="collapsed"
            )
        else:
            st.caption("No log metrics found for this query session yet.")
            
else:
    # Initial State Welcome Card
    st.info("💡 **Welcome!** Choose a question from the selectbox or write your custom query, then click **Run Pipeline** to view SQL Generation, Self-Correction, and Live Database Execution.")
