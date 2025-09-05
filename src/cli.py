import click
import os
import json
from colorama import init, Fore, Style
from .ai_test_copilot import AITestCopilot
from .config import Config

# Initialize colorama for cross-platform colored output
init()

@click.group()
@click.version_option(version="1.0.0")
def cli():
    """AI Test Case Copilot - Automate test case updates and creation."""
    pass

@cli.command()
@click.option('--change-request', '-c', required=True, 
              help='Path to the change request file')
@click.option('--verbose', '-v', is_flag=True, 
              help='Enable verbose output')
def process(change_request, verbose):
    """Process a change request and update/create test cases."""
    try:
        if verbose:
            click.echo(f"{Fore.BLUE}Initializing AI Test Copilot...{Style.RESET_ALL}")
        
        copilot = AITestCopilot()
        
        if verbose:
            status = copilot.get_status()
            click.echo(f"{Fore.GREEN}System Status: {status['status']}{Style.RESET_ALL}")
            click.echo(f"Test cases found: {status['test_cases_count']}")
        
        if verbose:
            click.echo(f"{Fore.BLUE}Processing change request: {change_request}{Style.RESET_ALL}")
        
        report_path = copilot.process_change_request(change_request)
        
        click.echo(f"{Fore.GREEN}✓ Change request processed successfully!{Style.RESET_ALL}")
        click.echo(f"{Fore.GREEN}Report generated at: {report_path}{Style.RESET_ALL}")
        
        # Show a preview of the report
        if verbose:
            with open(report_path, 'r') as f:
                content = f.read()
                lines = content.split('\n')[:20]  # First 20 lines
                click.echo(f"\n{Fore.CYAN}Report Preview:{Style.RESET_ALL}")
                for line in lines:
                    click.echo(line)
                if len(content.split('\n')) > 20:
                    click.echo(f"{Fore.YELLOW}... (truncated){Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
def status():
    """Show the current system status."""
    try:
        copilot = AITestCopilot()
        status = copilot.get_status()
        
        click.echo(f"{Fore.CYAN}AI Test Copilot Status{Style.RESET_ALL}")
        click.echo("=" * 30)
        
        if status['status'] == 'ready':
            click.echo(f"{Fore.GREEN}✓ System Ready{Style.RESET_ALL}")
        elif status['status'] == 'missing_api_key':
            click.echo(f"{Fore.RED}✗ Missing OpenAI API Key{Style.RESET_ALL}")
        else:
            click.echo(f"{Fore.RED}✗ System Error: {status.get('error', 'Unknown error')}{Style.RESET_ALL}")
        
        click.echo(f"Test Cases: {status['test_cases_count']}")
        click.echo(f"IW Overview: {'✓' if status['iw_overview_exists'] else '✗'}")
        click.echo(f"Schema: {'✓' if status['schema_exists'] else '✗'}")
        click.echo(f"OpenAI API: {'✓' if status['openai_configured'] else '✗'}")
        click.echo(f"Reports Directory: {status['reports_directory']}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error getting status: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
def validate():
    """Validate all existing test cases against the schema."""
    try:
        copilot = AITestCopilot()
        
        click.echo(f"{Fore.BLUE}Validating test cases...{Style.RESET_ALL}")
        results = copilot.validate_all_test_cases()
        
        click.echo(f"\n{Fore.CYAN}Validation Results{Style.RESET_ALL}")
        click.echo("=" * 20)
        click.echo(f"Total Files: {results['total_files']}")
        click.echo(f"Valid Files: {Fore.GREEN}{results['valid_files']}{Style.RESET_ALL}")
        click.echo(f"Invalid Files: {Fore.RED}{len(results['invalid_files'])}{Style.RESET_ALL}")
        
        if results['invalid_files']:
            click.echo(f"\n{Fore.RED}Invalid Files:{Style.RESET_ALL}")
            for invalid_file in results['invalid_files']:
                click.echo(f"  - {invalid_file}")
        
        if results['errors']:
            click.echo(f"\n{Fore.RED}Errors:{Style.RESET_ALL}")
            for error in results['errors']:
                click.echo(f"  - {error}")
        
        if results['valid_files'] == results['total_files']:
            click.echo(f"\n{Fore.GREEN}✓ All test cases are valid!{Style.RESET_ALL}")
        else:
            click.echo(f"\n{Fore.YELLOW}⚠ Some test cases have validation issues.{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error during validation: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
@click.option('--output', '-o', default='test_cases_list.txt',
              help='Output file for the list (default: test_cases_list.txt)')
def list_cases(output):
    """List all available test cases."""
    try:
        copilot = AITestCopilot()
        test_case_manager = copilot.test_case_manager
        
        test_cases = test_case_manager.load_all_test_cases()
        
        click.echo(f"{Fore.CYAN}Available Test Cases ({len(test_cases)}){Style.RESET_ALL}")
        click.echo("=" * 40)
        
        with open(output, 'w') as f:
            for i, test_case in enumerate(test_cases, 1):
                title = test_case.get('title', 'No title')
                test_type = test_case.get('type', 'Unknown')
                priority = test_case.get('priority', 'Unknown')
                file_name = test_case.get('_file_name', 'Unknown')
                
                # Console output
                click.echo(f"{i:2d}. {Fore.BLUE}{file_name}{Style.RESET_ALL}")
                click.echo(f"     Title: {title}")
                click.echo(f"     Type: {test_type}")
                click.echo(f"     Priority: {priority}")
                click.echo()
                
                # File output
                f.write(f"{i:2d}. {file_name}\n")
                f.write(f"     Title: {title}\n")
                f.write(f"     Type: {test_type}\n")
                f.write(f"     Priority: {priority}\n\n")
        
        click.echo(f"{Fore.GREEN}✓ Test cases list saved to: {output}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error listing test cases: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
@click.option('--test-case-id', '-t', required=True,
              help='Test case ID to show (e.g., tc_001)')
def show_case(test_case_id):
    """Show details of a specific test case."""
    try:
        copilot = AITestCopilot()
        test_case_manager = copilot.test_case_manager
        
        test_case = test_case_manager.get_test_case_by_id(test_case_id)
        
        if not test_case:
            click.echo(f"{Fore.RED}✗ Test case {test_case_id} not found{Style.RESET_ALL}")
            return
        
        click.echo(f"{Fore.CYAN}Test Case: {test_case_id}{Style.RESET_ALL}")
        click.echo("=" * 50)
        click.echo(f"Title: {test_case.get('title', 'No title')}")
        click.echo(f"Type: {test_case.get('type', 'Unknown')}")
        click.echo(f"Priority: {test_case.get('priority', 'Unknown')}")
        
        if test_case.get('preconditions'):
            click.echo(f"Preconditions: {test_case['preconditions']}")
        
        click.echo(f"\n{Fore.BLUE}Steps:{Style.RESET_ALL}")
        for i, step in enumerate(test_case.get('steps', []), 1):
            click.echo(f"{i:2d}. {step.get('step_text', 'No action')}")
            click.echo(f"    Expected: {step.get('step_expected', 'No expected outcome')}")
            click.echo()
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error showing test case: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
def metrics():
    """Show observability metrics."""
    try:
        copilot = AITestCopilot()
        metrics = copilot.get_metrics()
        
        click.echo(f"{Fore.CYAN}AI Test Copilot Metrics{Style.RESET_ALL}")
        click.echo("=" * 30)
        click.echo(f"Total Requests: {metrics['total_requests']}")
        click.echo(f"Success Rate: {Fore.GREEN}{metrics['success_rate']}%{Style.RESET_ALL}")
        click.echo(f"Total Tokens Used: {metrics['total_tokens_used']:,}")
        click.echo(f"Total Cost: ${metrics['total_cost']:.4f}")
        click.echo(f"Average Response Time: {metrics['average_response_time']}s")
        click.echo(f"Test Cases Generated: {metrics['test_cases_generated']}")
        click.echo(f"Test Cases Updated: {metrics['test_cases_updated']}")
        click.echo(f"Schema Validation Failures: {Fore.RED}{metrics['schema_validation_failures']}{Style.RESET_ALL}")
        click.echo(f"Retry Attempts: {Fore.YELLOW}{metrics['retry_attempts']}{Style.RESET_ALL}")
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error getting metrics: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
@click.option('--limit', '-l', default=5, help='Number of recent sessions to show')
def sessions(limit):
    """Show recent processing sessions."""
    try:
        copilot = AITestCopilot()
        sessions = copilot.get_recent_sessions(limit)
        
        click.echo(f"{Fore.CYAN}Recent Sessions ({len(sessions)}){Style.RESET_ALL}")
        click.echo("=" * 40)
        
        for session in sessions:
            status_color = Fore.GREEN if session.get('status') == 'success' else Fore.RED
            click.echo(f"Session: {session.get('session_id', 'Unknown')[:8]}...")
            click.echo(f"  Status: {status_color}{session.get('status', 'Unknown')}{Style.RESET_ALL}")
            click.echo(f"  Start: {session.get('start_time', 'Unknown')}")
            click.echo(f"  End: {session.get('end_time', 'Running...')}")
            click.echo(f"  Tokens: {session.get('tokens_used', 0):,}")
            click.echo(f"  Cost: ${session.get('cost', 0):.4f}")
            click.echo(f"  Generated: {session.get('test_cases_generated', 0)}")
            click.echo(f"  Updated: {session.get('test_cases_updated', 0)}")
            if session.get('errors'):
                click.echo(f"  Errors: {Fore.RED}{len(session['errors'])}{Style.RESET_ALL}")
            click.echo()
        
    except Exception as e:
        click.echo(f"{Fore.RED}✗ Error getting sessions: {str(e)}{Style.RESET_ALL}")
        raise click.Abort()

@cli.command()
def setup():
    """Show setup instructions."""
    click.echo(f"{Fore.CYAN}AI Test Copilot Setup Instructions{Style.RESET_ALL}")
    click.echo("=" * 40)
    click.echo()
    click.echo("1. Set your OpenAI API key:")
    click.echo("   export OPENAI_API_KEY='your-api-key-here'")
    click.echo()
    click.echo("2. Or create a .env file:")
    click.echo("   OPENAI_API_KEY=your-api-key-here")
    click.echo()
    click.echo("3. Install dependencies:")
    click.echo("   pip install -r requirements.txt")
    click.echo()
    click.echo("4. Verify setup:")
    click.echo("   python -m src.cli status")
    click.echo()
    click.echo("5. Process a change request:")
    click.echo("   python -m src.cli process -c sample_change_requests/sample_change_request_new_feature.md")
    click.echo()
    click.echo("6. View metrics and sessions:")
    click.echo("   python -m src.cli metrics")
    click.echo("   python -m src.cli sessions")
    click.echo()
    click.echo("For more help:")
    click.echo("   python -m src.cli --help")

if __name__ == '__main__':
    cli()
