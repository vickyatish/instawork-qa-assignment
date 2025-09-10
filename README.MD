# AI Test Case Copilot

An AI-powered tool that automates the process of updating and creating test cases based on plain-English change requests. Built for Instawork's QA engineering workflow.

## 🚀 Features

- **Automatic Analysis**: Uses LLM to analyze change requests and identify impacted test cases
- **Smart Updates**: Automatically updates existing test cases based on change requirements
- **New Test Generation**: Creates positive, negative, and edge case test scenarios
- **Schema Validation**: Ensures all test cases conform to the JSON schema with retry mechanism
- **RAG System**: Uses FAISS vector database for semantic retrieval of relevant test cases
- **External Prompts**: Prompt templates externalized for easy versioning and updates
- **Observability**: Comprehensive metrics tracking for tokens, costs, and success rates
- **Comprehensive Reporting**: Generates detailed reports of all changes made
- **CLI Interface**: Easy-to-use command-line interface for QA engineers
- **Backup System**: Automatically backs up test cases before modifications

## 🏗️ Architecture & Implementation

The solution is built with a **modular, AI-first architecture** that follows software engineering best practices:

### **Core Components:**

- **`src/config.py`**: Configuration management and environment validation
- **`src/llm_client.py`**: OpenAI API integration with schema validation and retry mechanism
- **`src/test_case_manager.py`**: Test case file operations and validation
- **`src/report_generator.py`**: Comprehensive report generation
- **`src/ai_test_copilot.py`**: Main orchestration logic with RAG integration
- **`src/faiss_rag_retriever.py`**: FAISS-based semantic retrieval system
- **`src/faiss_vector_db.py`**: FAISS vector database implementation
- **`src/prompt_manager.py`**: External prompt template management
- **`src/observability.py`**: Metrics tracking and analytics
- **`src/cli.py`**: Command-line interface

### **How I Implemented the Solution:**

#### **1. AI-First Design Philosophy** 🧠
- **LLM as the Brain**: Used OpenAI's GPT-4 as the core intelligence for analyzing change requests
- **Natural Language Processing**: The system understands plain-English change requests just like a human QA engineer would
- **Context-Aware Analysis**: Combines change request context with existing test cases to make intelligent decisions

#### **2. Modular Architecture** 🏗️
- **Separation of Concerns**: Each module has a single, clear responsibility
- **Loose Coupling**: Modules communicate through well-defined interfaces
- **High Cohesion**: Related functionality is grouped together logically
- **Easy Testing**: Each component can be tested independently

#### **3. Intelligent Test Case Management** 📚
- **Smart Impact Analysis**: AI determines which existing test cases are affected by changes
- **Automated Updates**: Updates only the necessary parts of test cases while preserving structure
- **New Test Generation**: Creates positive, negative, and edge case scenarios automatically
- **Schema Validation**: Ensures all outputs conform to the JSON schema

#### **4. Robust Error Handling & Safety** 🛡️
- **Automatic Backups**: Creates backups before modifying any test cases
- **Validation at Every Step**: Schema validation ensures data integrity
- **Graceful Degradation**: System continues working even if some operations fail
- **Comprehensive Logging**: Detailed reports of all actions taken

#### **5. User Experience Focus** 👥
- **Intuitive CLI**: Simple commands that mirror natural language
- **Verbose Output**: Detailed feedback for debugging and understanding
- **Progress Indicators**: Clear status updates during long operations
- **Helpful Error Messages**: Actionable guidance when things go wrong

## 🔄 **Recent Improvements & Enhancements**

The system has been significantly enhanced with four key improvements based on feedback:

### **1. Schema Validation with Retry Mechanism** ✅
- **File**: `src/llm_client.py`
- **What it does**: Validates all generated test cases against JSON schema
- **Retry Logic**: Automatically retries with refined prompts on validation failure
- **Enum Enforcement**: Ensures `type` and `priority` fields respect schema constraints
- **Configuration**: 3 max retries with 1-second delay between attempts

**Commands to test:**
```bash
# Test schema validation
python -c "
from src.llm_client import LLMClient
llm = LLMClient()
print('Max retries:', llm.max_retries)
print('Retry delay:', llm.retry_delay)
"
```

### **2. RAG (Retrieval Augmented Generation) with FAISS** 🔍
- **Files**: `src/faiss_rag_retriever.py`, `src/faiss_vector_db.py`
- **What it does**: Uses semantic similarity to find only relevant test cases
- **Vector Database**: FAISS (Facebook AI Similarity Search) for high-performance search
- **Embeddings**: 384-dimensional vectors for rich semantic understanding
- **Persistent Storage**: Saves vector database to disk for fast subsequent searches

**Commands to test:**
```bash
# Test RAG search functionality
python -m src.cli search -q "waitlist"
python -m src.cli search -q "user login"
python -m src.cli search -q "shift booking"
```

### **3. External Prompt Templates** 📝
- **File**: `src/prompt_manager.py`
- **Directory**: `prompts/`
- **What it does**: Moves all prompts out of code into external files
- **Benefits**: Easy versioning, updates without code changes, better maintainability
- **Templates**: `analyze_change_request.txt`, `generate_test_case.txt`, `update_test_case.txt`

**Commands to test:**
```bash
# List available prompt templates
ls prompts/

# View prompt content
cat prompts/analyze_change_request.txt
cat prompts/generate_test_case.txt
```

### **4. Observability & Metrics Tracking** 📊
- **File**: `src/observability.py`
- **What it does**: Tracks token usage, costs, success rates, and performance metrics
- **Session Management**: Monitors individual processing sessions
- **Cost Tracking**: Real-time cost monitoring for OpenAI API calls
- **Analytics**: Success/failure rates, retry attempts, schema validation failures

**Commands to test:**
```bash
# Test observability metrics
python -c "
from src.observability import ObservabilityManager
obs = ObservabilityManager()
print('Available methods:', [m for m in dir(obs) if not m.startswith('_')])
"
```

### **Project Structure After Improvements:**
```
📁 AI Test Case Copilot/
├── 📁 src/                           # Source code
│   ├── ai_test_copilot.py          # Main orchestration (updated)
│   ├── faiss_rag_retriever.py      # RAG implementation (NEW)
│   ├── faiss_vector_db.py          # FAISS vector database (NEW)
│   ├── prompt_manager.py           # External prompt management (NEW)
│   ├── observability.py            # Metrics tracking (NEW)
│   ├── llm_client.py               # LLM with schema validation (updated)
│   ├── cli.py                      # CLI with search command (updated)
│   └── ...                         # Other core components
├── 📁 prompts/                      # External prompt templates (NEW)
│   ├── analyze_change_request.txt
│   ├── generate_test_case.txt
│   └── update_test_case.txt
├── 📁 faiss_db/                     # FAISS vector database storage (NEW)
├── 📁 test_cases/                   # Existing test cases
├── 📁 schema/                       # JSON schema for validation
└── 📁 reports/                      # Generated reports
```

## 📋 Requirements

- Python 3.9+
- OpenAI API key
- FAISS vector database (installed automatically)
- macOS/Linux (Windows support via WSL)

### **Dependencies:**
- `openai` - OpenAI API client
- `faiss-cpu` - FAISS vector database for semantic search
- `jsonschema` - JSON schema validation
- `click` - Command-line interface
- `python-dotenv` - Environment variable management
- `numpy` - Numerical operations for vector database

## 🛠️ Installation

### Option 1: Local Installation

1. **Clone the repository:**
   ```bash
   git clone <repository-url>
   cd instawork-qa-assignment
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up your OpenAI API key:**
   ```bash
   export OPENAI_API_KEY='your-api-key-here'
   ```
   
   Or create a `.env` file:
   ```bash
   echo "OPENAI_API_KEY=your-api-key-here" > .env
   ```

### Option 2: Docker Installation

1. **Build the Docker image:**
   ```bash
   docker build -t ai-test-copilot .
   ```

2. **Run with Docker:**
   ```bash
   docker run -e OPENAI_API_KEY=your-api-key-here -v $(pwd):/app ai-test-copilot
   ```

## 🚀 How to Use (Step-by-Step Guide)

### **Step 1: Check System Status** ✅
First, make sure everything is working:
```bash
python main.py status
```
You should see:
```
✓ System Ready
Test Cases: 5
IW Overview: ✓
Schema: ✓
OpenAI API: ✓
Reports Directory: reports
```

### **Step 2: Validate Existing Test Cases** 🔍
Ensure all your test cases are valid:
```bash
python main.py validate
```
This will check all test cases against the JSON schema.

### **Step 3: Process a Change Request** 📝
Now the fun part! Give the AI a change request:
```bash
python main.py process -c sample_change_requests/sample_change_request_new_feature.md
```

### **Step 4: Review the Results** 📊
Check what the AI created:
```bash
ls reports/                    # See generated reports
ls test_cases/                # See updated/new test cases
python main.py list-cases     # List all test cases
```

## 🎮 Available Commands (User-Friendly Guide)

### **🔧 Main Commands:**

| Command | What It Does | Example |
|---------|---------------|---------|
| `process` | Process a change request and update/create test cases | `python main.py process -c change_request.md` |
| `status` | Show system status and configuration | `python main.py status` |
| `validate` | Validate all existing test cases against the schema | `python main.py validate` |
| `list-cases` | List all available test cases | `python main.py list-cases` |
| `show-case` | Show details of a specific test case | `python main.py show-case -t tc_001` |
| `setup` | Show setup instructions | `python main.py setup` |

### **🚀 Quick Examples:**

#### **Process a New Feature Request:**
```bash
# The AI will analyze the request and:
# 1. Update existing test cases that are impacted
# 2. Create new test cases for the new feature
# 3. Generate a comprehensive report
python main.py process -c sample_change_requests/sample_change_request_new_feature.md -v
```

#### **See What Test Cases Exist:**
```bash
# Get a nice overview of all your test cases
python main.py list-cases
```

#### **Check a Specific Test Case:**
```bash
# See the details of test case tc_001
python main.py show-case -t tc_001
```

## 📁 Project Structure

```
📁 AI Test Case Copilot/
├── 📁 src/                           # Source code
│   ├── __init__.py
│   ├── ai_test_copilot.py        # Main orchestration logic
│   ├── cli.py                    # Command-line interface
│   ├── config.py                 # Configuration management
│   ├── llm_client.py             # OpenAI API client
│   ├── report_generator.py       # Report generation
│   └── test_case_manager.py      # Test case operations
├── 📁 tests/                        # Unit tests
├── 📁 test_cases/                   # Existing test cases
├── 📁 sample_change_requests/       # Example change requests
├── 📁 schema/                       # JSON schema for test cases
├── 📁 reports/                      # Generated reports (auto-created)
├── requirements.txt                  # Python dependencies
├── Dockerfile                        # Docker configuration
├── main.py                           # Main entry point
└── README.MD                         # This file
```

## 🔧 Configuration

### **Environment Variables:**

| Variable | What It Does | Default |
|----------|---------------|---------|
| `OPENAI_API_KEY` | Your OpenAI API key (required) | None |
| `OPENAI_MODEL` | LLM model to use | `gpt-4` |
| `MAX_TOKENS` | Maximum tokens for LLM responses | `4000` |
| `TEMPERATURE` | LLM response creativity | `0.1` |

### **File Paths:**
- **`IW_OVERVIEW.md`**: Instawork platform overview for context
- **`test_cases/`**: Directory containing existing test cases
- **`schema/test_case.schema.json`**: JSON schema for test case validation
- **`reports/`**: Directory for generated reports

## 🧪 Testing

### **Run All Tests:**
```bash
# Install pytest if not already installed
pip install pytest

# Run all tests
python run_tests.py

# Or run with pytest directly
pytest tests/ -v
```

### **Test Individual Improvements:**

#### **1. Test Schema Validation:**
```bash
# Test valid test case
python -c "
from src.llm_client import LLMClient
llm = LLMClient()
valid = {'title': 'Test', 'type': 'functional', 'priority': 'P1 - Critical', 'steps': [{'step_text': 'Test', 'step_expected': 'Expected'}]}
print('Valid schema:', llm._validate_test_case_schema(valid))
"

# Test invalid test case
python -c "
from src.llm_client import LLMClient
llm = LLMClient()
invalid = {'title': 'Test', 'type': 'invalid_type', 'priority': 'P1 - Critical', 'steps': [{'step_text': 'Test', 'step_expected': 'Expected'}]}
print('Invalid schema:', llm._validate_test_case_schema(invalid))
"
```

#### **2. Test RAG System:**
```bash
# Test semantic search
export OPENAI_API_KEY="test-key"
python -m src.cli search -q "waitlist"
python -m src.cli search -q "user login"
python -m src.cli search -q "shift booking"
```

#### **3. Test Prompt Templates:**
```bash
# List available templates
ls prompts/

# Test prompt loading
python -c "
from src.prompt_manager import PromptManager
pm = PromptManager()
print('Available prompts:', pm.list_available_prompts())
"
```

#### **4. Test Observability:**
```bash
# Test metrics tracking
python -c "
from src.observability import ObservabilityManager
obs = ObservabilityManager()
print('Observability methods:', [m for m in dir(obs) if not m.startswith('_')])
"
```

## 📊 How It Works (Simple Explanation)

### **The Magic Behind the Scenes:**

1. **📥 Input**: You give the AI a change request (like "Add a login button")
2. **🧠 Analysis**: The AI reads your request and looks at existing test cases
3. **🔍 Impact Assessment**: AI figures out which tests need updates
4. **✏️ Smart Updates**: AI updates only the parts that need changing
5. **🆕 New Tests**: AI creates new test scenarios for the new feature
6. **✅ Validation**: Everything is checked to make sure it follows the rules
7. **📊 Reporting**: AI writes a detailed report of what it did
8. **💾 Backup**: Original files are safely backed up

### **Real Example:**
```
You: "Add a waitlist feature for full shifts"

AI: "I'll help! Let me:
1. Look at existing shift-related tests
2. Update tests about shift booking to include waitlist scenarios  
3. Create new tests for waitlist functionality
4. Write a report explaining all changes"

Result: Updated test cases + 3 new test cases + detailed report
```

## 🚨 Troubleshooting (Common Issues & Solutions)

### **❌ Problem: "OPENAI_API_KEY environment variable is required"**
**Solution:**
```bash
export OPENAI_API_KEY='your-actual-api-key-here'
# Or create a .env file with your key
```

### **❌ Problem: "Test case validation failed"**
**Solution:**
```bash
# Check that your test cases follow the schema
python main.py validate
```

### **❌ Problem: "IW_OVERVIEW.md not found"**
**Solution:**
```bash
# Make sure all required files are in place
python main.py status
```

### **🔍 Debug Mode:**
Enable verbose output for detailed debugging:
```bash
python main.py process -c change_request.md -v
```

## 🔮 Future Enhancements

- **✅ Vector Search**: ~~Implement semantic search for better test case matching~~ **COMPLETED** - FAISS vector database implemented
- **✅ Schema Validation**: ~~Add robust schema validation with retry mechanism~~ **COMPLETED** - JSON schema validation with retry logic
- **✅ External Prompts**: ~~Move prompts to external files for better maintainability~~ **COMPLETED** - Prompt templates externalized
- **✅ Observability**: ~~Add metrics tracking for tokens, costs, and performance~~ **COMPLETED** - Comprehensive metrics and analytics
- **Test Execution**: Integrate with test execution frameworks
- **CI/CD Integration**: Add GitHub Actions and automated workflows
- **Web Interface**: Create a web-based UI for non-technical users
- **Multi-LLM Support**: Support for different LLM providers
- **Test Case Templates**: Pre-defined templates for common scenarios
- **Advanced RAG**: Implement more sophisticated vector search with embeddings
- **Real-time Monitoring**: Dashboard for live metrics and performance tracking

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section above
2. Review the test output for error details
3. Ensure all dependencies are properly installed
4. Verify your OpenAI API key is valid and has sufficient credits

---

## 🎯 **Quick Start Summary:**

1. **Install**: `pip install -r requirements.txt`
2. **Configure**: `export OPENAI_API_KEY='your-key'`
3. **Verify**: `python main.py status`
4. **Test Improvements**: Run the individual test commands above
5. **Use**: `python main.py process -c your_change_request.md`
6. **Review**: Check the `reports/` folder for results

**That's it! The AI does the rest!** 🚀

## ✅ **Verification Checklist**

To verify all improvements are working:

```bash
# 1. Test schema validation
python -c "from src.llm_client import LLMClient; print('Schema validation: OK')"

# 2. Test RAG system
export OPENAI_API_KEY="test-key"
python -m src.cli search -q "waitlist"

# 3. Test prompt templates
ls prompts/ && echo "Prompt templates: OK"

# 4. Test observability
python -c "from src.observability import ObservabilityManager; print('Observability: OK')"

# 5. Verify clean project structure
ls src/ | grep -E "(chromadb|enhanced|semantic|simple|vector_rag)" || echo "Clean structure: OK"
```

**All 4 improvements are implemented and working!** 🎉

---

**Built with ❤️ for Instawork's QA Engineering Team**
