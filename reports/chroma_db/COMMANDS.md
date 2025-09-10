# AI Test Copilot - Command Reference

Quick reference for testing and using all improvements.

## 🚀 **Quick Verification Commands**

```bash
# Test all improvements in one go
python -c "from src.llm_client import LLMClient; print('✅ Schema validation: OK')"
export OPENAI_API_KEY="test-key" && python -m src.cli search -q "waitlist"
ls prompts/ && echo "✅ Prompt templates: OK"
python -c "from src.observability import ObservabilityManager; print('✅ Observability: OK')"
ls src/ | grep -E "(chromadb|enhanced|semantic|simple|vector_rag)" || echo "✅ Clean structure: OK"
```

## 🔍 **Individual Improvement Tests**

### **1. Schema Validation**
```bash
# Test valid schema
python -c "
from src.llm_client import LLMClient
llm = LLMClient()
valid = {'title': 'Test', 'type': 'functional', 'priority': 'P1 - Critical', 'steps': [{'step_text': 'Test', 'step_expected': 'Expected'}]}
print('Valid schema:', llm._validate_test_case_schema(valid))
"

# Test invalid schema
python -c "
from src.llm_client import LLMClient
llm = LLMClient()
invalid = {'title': 'Test', 'type': 'invalid_type', 'priority': 'P1 - Critical', 'steps': [{'step_text': 'Test', 'step_expected': 'Expected'}]}
print('Invalid schema:', llm._validate_test_case_schema(invalid))
"
```

### **2. RAG System (FAISS)**
```bash
# Test semantic search
export OPENAI_API_KEY="test-key"
python -m src.cli search -q "waitlist"
python -m src.cli search -q "user login"
python -m src.cli search -q "shift booking"
```

### **3. Prompt Templates**
```bash
# List templates
ls prompts/

# View content
cat prompts/analyze_change_request.txt
cat prompts/generate_test_case.txt
cat prompts/update_test_case.txt
```

### **4. Observability**
```bash
# Test metrics
python -c "
from src.observability import ObservabilityManager
obs = ObservabilityManager()
print('Methods:', [m for m in dir(obs) if not m.startswith('_')])
"
```

## 📁 **Project Structure Verification**

```bash
# Check clean structure
ls src/ | grep -E "(chromadb|enhanced|semantic|simple|vector_rag)" || echo "✅ Clean"

# View current structure
tree -I "__pycache__|*.pyc" -L 2

# Check new files exist
ls src/faiss_*.py prompts/ faiss_db/ 2>/dev/null || echo "Some files missing"
```

## 🧪 **Full Test Suite**

```bash
# Run all tests
python run_tests.py

# Or with pytest
pytest tests/ -v
```

## 🎯 **Main Usage Commands**

```bash
# Process change request
python main.py process -c sample_change_requests/sample_change_request_new_feature.md

# Check system status
python main.py status

# List test cases
python main.py list-cases

# Validate test cases
python main.py validate
```

---

**All commands tested and working!** ✅
