import os
from datetime import datetime
from typing import List, Dict, Any
from .config import Config

class ReportGenerator:
    """Generates comprehensive reports of test case changes and updates."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.reports_dir = Config.REPORTS_DIR
    
    def generate_report(
        self,
        change_request: str,
        analysis_result: Dict[str, Any],
        updated_test_cases: List[Dict[str, Any]],
        new_test_cases: List[Dict[str, Any]],
        execution_summary: Dict[str, Any]
    ) -> str:
        """Generate a comprehensive report of all changes made."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_filename = f"change_request_report_{timestamp}.md"
        report_path = os.path.join(self.reports_dir, report_filename)
        
        try:
            with open(report_path, 'w') as f:
                self._write_report_header(f, change_request, timestamp)
                self._write_execution_summary(f, execution_summary)
                self._write_analysis_summary(f, analysis_result)
                self._write_updated_test_cases(f, updated_test_cases)
                self._write_new_test_cases(f, new_test_cases)
                self._write_assumptions_and_questions(f, analysis_result)
                self._write_footer(f)
            
            return report_path
            
        except Exception as e:
            raise Exception(f"Failed to generate report: {str(e)}")
    
    def _write_report_header(self, file, change_request: str, timestamp: str):
        """Write the report header section."""
        file.write("# AI Test Case Copilot - Change Request Report\n\n")
        file.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        file.write(f"**Report ID:** {timestamp}\n\n")
        
        file.write("## Change Request\n\n")
        file.write("```\n")
        file.write(change_request)
        file.write("\n```\n\n")
        
        file.write("---\n\n")
    
    def _write_execution_summary(self, file, execution_summary: Dict[str, Any]):
        """Write the execution summary section."""
        file.write("## Execution Summary\n\n")
        
        file.write(f"- **Total test cases analyzed:** {execution_summary.get('total_analyzed', 0)}\n")
        file.write(f"- **Test cases updated:** {execution_summary.get('total_updated', 0)}\n")
        file.write(f"- **New test cases created:** {execution_summary.get('total_created', 0)}\n")
        file.write(f"- **Execution time:** {execution_summary.get('execution_time', 'N/A')}\n")
        file.write(f"- **Status:** {execution_summary.get('status', 'N/A')}\n\n")
        
        if execution_summary.get('errors'):
            file.write("### Errors Encountered\n\n")
            for error in execution_summary['errors']:
                file.write(f"- {error}\n")
            file.write("\n")
        
        file.write("---\n\n")
    
    def _write_analysis_summary(self, file, analysis_result: Dict[str, Any]):
        """Write the analysis summary section."""
        file.write("## Analysis Summary\n\n")
        
        if 'summary' in analysis_result:
            file.write(f"{analysis_result['summary']}\n\n")
        
        file.write("### Impact Assessment\n\n")
        
        if 'impacted_test_cases' in analysis_result and analysis_result['impacted_test_cases']:
            file.write("**Impacted Test Cases:**\n\n")
            for impacted in analysis_result['impacted_test_cases']:
                file.write(f"- **{impacted.get('test_case_id', 'Unknown')}** ({impacted.get('impact_level', 'Unknown')} impact)\n")
                file.write(f"  - **Reasoning:** {impacted.get('reasoning', 'No reasoning provided')}\n")
                file.write(f"  - **Required Changes:** {', '.join(impacted.get('required_changes', []))}\n\n")
        else:
            file.write("No existing test cases were impacted by this change request.\n\n")
        
        if 'new_test_cases_needed' in analysis_result and analysis_result['new_test_cases_needed']:
            file.write("**New Test Cases Required:**\n\n")
            for new_case in analysis_result['new_test_cases_needed']:
                file.write(f"- **{new_case.get('test_case_type', 'Unknown')}** - {new_case.get('title', 'No title')} ({new_case.get('priority', 'Unknown priority')})\n")
            file.write("\n")
        
        file.write("---\n\n")
    
    def _write_updated_test_cases(self, file, updated_test_cases: List[Dict[str, Any]]):
        """Write the updated test cases section."""
        if not updated_test_cases:
            return
        
        file.write("## Updated Test Cases\n\n")
        
        for test_case in updated_test_cases:
            file.write(f"### {test_case.get('_file_name', 'Unknown File')}\n\n")
            file.write(f"**Title:** {test_case.get('title', 'No title')}\n")
            file.write(f"**Type:** {test_case.get('type', 'Unknown')}\n")
            file.write(f"**Priority:** {test_case.get('priority', 'Unknown')}\n\n")
            
            if test_case.get('preconditions'):
                file.write(f"**Preconditions:** {test_case['preconditions']}\n\n")
            
            file.write("**Steps:**\n\n")
            for i, step in enumerate(test_case.get('steps', []), 1):
                file.write(f"{i}. **Action:** {step.get('step_text', 'No action specified')}\n")
                file.write(f"   **Expected:** {step.get('step_expected', 'No expected outcome specified')}\n\n")
            
            file.write("---\n\n")
    
    def _write_new_test_cases(self, file, new_test_cases: List[Dict[str, Any]]):
        """Write the new test cases section."""
        if not new_test_cases:
            return
        
        file.write("## New Test Cases Created\n\n")
        
        for test_case in new_test_cases:
            file.write(f"### {test_case.get('_file_name', 'Unknown File')}\n\n")
            file.write(f"**Title:** {test_case.get('title', 'No title')}\n")
            file.write(f"**Type:** {test_case.get('type', 'Unknown')}\n")
            file.write(f"**Priority:** {test_case.get('priority', 'Unknown')}\n\n")
            
            if test_case.get('preconditions'):
                file.write(f"**Preconditions:** {test_case['preconditions']}\n\n")
            
            file.write("**Steps:**\n\n")
            for i, step in enumerate(test_case.get('steps', []), 1):
                file.write(f"{i}. **Action:** {step.get('step_text', 'No action specified')}\n")
                file.write(f"   **Expected:** {step.get('step_expected', 'No expected outcome specified')}\n\n")
            
            file.write("---\n\n")
    
    def _write_assumptions_and_questions(self, file, analysis_result: Dict[str, Any]):
        """Write the assumptions and questions section."""
        file.write("## Assumptions and Open Questions\n\n")
        
        # Extract assumptions and questions from the analysis
        assumptions = []
        questions = []
        
        # Look for assumptions and questions in the analysis result
        if 'summary' in analysis_result:
            summary = analysis_result['summary'].lower()
            if 'assume' in summary or 'assumption' in summary:
                assumptions.append("Analysis made assumptions based on available context")
        
        if 'impacted_test_cases' in analysis_result:
            for impacted in analysis_result['impacted_test_cases']:
                reasoning = impacted.get('reasoning', '').lower()
                if 'assume' in reasoning or 'assumption' in reasoning:
                    assumptions.append(f"Assumptions made for {impacted.get('test_case_id', 'Unknown')}: {impacted.get('reasoning', '')}")
        
        if assumptions:
            file.write("### Assumptions Made\n\n")
            for assumption in assumptions:
                file.write(f"- {assumption}\n")
            file.write("\n")
        
        if questions:
            file.write("### Open Questions for the Team\n\n")
            for question in questions:
                file.write(f"- {question}\n")
            file.write("\n")
        
        if not assumptions and not questions:
            file.write("No specific assumptions or open questions identified during this analysis.\n\n")
        
        file.write("---\n\n")
    
    def _write_footer(self, file):
        """Write the report footer."""
        file.write("## Next Steps\n\n")
        file.write("1. **Review** all updated and new test cases for accuracy\n")
        file.write("2. **Execute** the updated test cases to verify they still pass\n")
        file.write("3. **Execute** new test cases to ensure they cover the intended functionality\n")
        file.write("4. **Update** test execution documentation as needed\n")
        file.write("5. **Share** this report with the development team for review\n\n")
        
        file.write("---\n\n")
        file.write("*Report generated by AI Test Case Copilot v1.0*\n")
